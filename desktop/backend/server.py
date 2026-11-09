# -*- coding: utf-8 -*-
"""Backend local de YTDownloader4K (nueva arquitectura desktop/).

FastAPI en 127.0.0.1 que expone la lógica real de descarga (yt-dlp + ffmpeg)
al frontend Electron:

  GET  /api/health    -> estado (versión, ffmpeg listo o no)
  POST /api/load      -> info del vídeo + formatos procesados (formatos.py)
  POST /api/download  -> inicia descarga (vídeo->MKV o audio->MP3) en ~/Downloads
  WS   /ws            -> progreso en tiempo real de la descarga activa

Reutiliza src/formatos.py (la lógica testeada de deduplicado/orden) y replica
los puntos duros de src/descargador.py: opciones ydl con ffmpeg_location,
detección del muro anti-bot, format string con fallbacks [protocol^=http],
timeout duro de extracción y ffmpeg auto-descargado a %LOCALAPPDATA%.
"""
import argparse
import asyncio
import concurrent.futures
import os
import subprocess
import sys
import tempfile
import threading
import traceback
import zipfile
from pathlib import Path

# Congelado con console=False, PyInstaller deja sys.stdout/stderr en None y
# cualquier print/log de uvicorn revienta. Los redirigimos a un log en %TEMP%.
if getattr(sys, "frozen", False):
    _log = open(Path(tempfile.gettempdir()) / "ytd4k-backend.log", "a",
                buffering=1, encoding="utf-8", errors="replace")
    sys.stdout = sys.stderr = _log

# lógica compartida con la app clásica. Congelado (PyInstaller) el módulo va
# empaquetado vía pathex del .spec; desde fuente se resuelve contra ../../src.
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from formatos import procesar_formatos_video  # noqa: E402

import urllib.request  # noqa: E402

import yt_dlp  # noqa: E402
from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel  # noqa: E402
import uvicorn  # noqa: E402

__version__ = "0.1.0"

APP_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))) / "YTDownloader4k"
FFMPEG_DIR = APP_DATA_DIR / "ffmpeg"
FFMPEG_URL = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
CARPETA_DESCARGAS = Path.home() / "Downloads"

ffmpeg_location = None
ffmpeg_listo = False


# ─── ffmpeg (misma estrategia que descargador.py, sin GUI) ───────────
def _ffmpeg_disponible():
    global ffmpeg_location
    if (FFMPEG_DIR / "ffmpeg.exe").exists() and (FFMPEG_DIR / "ffprobe.exe").exists():
        ffmpeg_location = str(FFMPEG_DIR)
        return True
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5,
                       creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        ffmpeg_location = None
        return True
    except Exception:
        return False


def _instalar_ffmpeg():
    """Descarga ffmpeg/ffprobe a LOCALAPPDATA (bloqueante; corre en hilo)."""
    global ffmpeg_location, ffmpeg_listo
    try:
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        zip_path = APP_DATA_DIR / "ffmpeg.zip"
        req = urllib.request.Request(FFMPEG_URL, headers={"User-Agent": "YTDownloader4K"})
        with urllib.request.urlopen(req, timeout=300) as r, open(zip_path, "wb") as f:
            while True:
                bloque = r.read(1024 * 512)
                if not bloque:
                    break
                f.write(bloque)
        FFMPEG_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            for nombre in zf.namelist():
                base = os.path.basename(nombre)
                if base in ("ffmpeg.exe", "ffprobe.exe"):
                    (FFMPEG_DIR / base).write_bytes(zf.read(nombre))
        zip_path.unlink(missing_ok=True)
        if (FFMPEG_DIR / "ffmpeg.exe").exists():
            ffmpeg_location = str(FFMPEG_DIR)
            ffmpeg_listo = True
    except Exception:
        pass  # /api/health seguirá reportando ffmpeg: false


def preparar_ffmpeg():
    global ffmpeg_listo
    if _ffmpeg_disponible():
        ffmpeg_listo = True
    else:
        threading.Thread(target=_instalar_ffmpeg, daemon=True).start()


def opciones_ydl(extras=None):
    opts = {}
    if ffmpeg_location:
        opts["ffmpeg_location"] = ffmpeg_location
    if extras:
        opts.update(extras)
    return opts


# ─── muro anti-bot (igual que la app clásica) ────────────────────────
MENSAJE_BLOQUEO = (
    "YouTube is currently blocking this specific video with a bot check. "
    "Wait a few minutes and try again, or try a different video."
)


def _es_error_bot(err):
    t = str(err).lower()
    return ("sign in to confirm" in t or "not a bot" in t
            or ("cookies" in t and "authentication" in t))


# ─── API ─────────────────────────────────────────────────────────────
app = FastAPI(title="YTDownloader4K backend", version=__version__)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

clientes_ws = set()
cola_eventos: asyncio.Queue = None
loop_principal: asyncio.AbstractEventLoop = None
descarga_activa = threading.Event()


class LoadReq(BaseModel):
    url: str


class DownloadReq(BaseModel):
    url: str
    format_id: str | None = None   # None o "mp3" => audio MP3
    height: int | None = None


@app.on_event("startup")
async def _startup():
    global cola_eventos, loop_principal
    cola_eventos = asyncio.Queue()
    loop_principal = asyncio.get_running_loop()
    preparar_ffmpeg()
    asyncio.create_task(_difusor())


async def _difusor():
    """Reparte los eventos de progreso a todos los websockets conectados."""
    while True:
        msg = await cola_eventos.get()
        muertos = []
        for ws in clientes_ws:
            try:
                await ws.send_json(msg)
            except Exception:
                muertos.append(ws)
        for ws in muertos:
            clientes_ws.discard(ws)


def emitir(msg: dict):
    """Desde los hilos de descarga: encola un evento hacia los websockets."""
    if loop_principal and cola_eventos is not None:
        loop_principal.call_soon_threadsafe(cola_eventos.put_nowait, msg)


@app.get("/api/health")
async def health():
    return {"ok": True, "version": __version__, "ffmpeg": ffmpeg_listo,
            "downloading": descarga_activa.is_set()}


@app.post("/api/load")
async def load(req: LoadReq):
    opts = opciones_ydl({
        "quiet": True, "no_warnings": True, "geo_bypass": True,
        "socket_timeout": 30, "extractor_retries": 2, "retries": 2,
        "noplaylist": True,
    })

    def extraer():
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(req.url, download=False)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            info = await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(pool, extraer), timeout=90)
    except asyncio.TimeoutError:
        return {"error": "Timeout: extraction took longer than 90s."}
    except Exception as e:
        if _es_error_bot(e):
            return {"error": MENSAJE_BLOQUEO, "blocked": True}
        return {"error": str(e)[:300]}

    if not info:
        return {"error": "Could not retrieve video information."}

    formatos = procesar_formatos_video(info.get("formats", []))
    if not formatos:
        return {"error": "No video formats found."}

    # chips: la mejor variante de las 2 alturas más altas (la lista ya viene
    # ordenada desc y la primera aparición de cada altura es la mejor)
    top, vistas = [], set()
    for f in formatos:
        if f["height"] not in vistas:
            vistas.add(f["height"])
            top.append(f)
        if len(top) == 2:
            break

    dur = info.get("duration") or 0
    duracion = f"{int(dur) // 3600}:{int(dur) % 3600 // 60:02d}:{int(dur) % 60:02d}" \
        if dur >= 3600 else f"{int(dur) // 60}:{int(dur) % 60:02d}"

    return {
        "title": info.get("title"),
        "channel": info.get("uploader") or info.get("channel") or "",
        "duration": duracion if dur else "",
        "thumbnail": info.get("thumbnail") or "",
        "top": [{k: f[k] for k in ("format_id", "height", "label")} for f in top],
        "formats": [{k: f[k] for k in ("format_id", "height", "label")} for f in formatos],
    }


@app.post("/api/download")
async def download(req: DownloadReq):
    if descarga_activa.is_set():
        return {"error": "A download is already in progress."}
    descarga_activa.set()
    threading.Thread(target=_descargar, args=(req,), daemon=True).start()
    return {"started": True}


def _descargar(req: DownloadReq):
    def hook(d):
        try:
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                hecho = d.get("downloaded_bytes", 0)
                emitir({
                    "status": "downloading",
                    "pct": round(hecho / total * 100, 1) if total else 0,
                    "speed": round((d.get("speed") or 0) / (1024 * 1024), 2),
                    "eta": d.get("eta"),
                })
            elif d["status"] == "finished":
                emitir({"status": "processing"})
        except Exception:
            pass

    es_audio = not req.format_id or req.format_id == "mp3"
    if es_audio:
        extra = {
            "format": "bestaudio/best",
            "outtmpl": str(CARPETA_DESCARGAS / "%(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
    else:
        h = req.height
        extra = {
            "format": (f"{req.format_id}+bestaudio/"
                       f"bestvideo[height={h}][protocol^=http]+bestaudio/"
                       f"best[height={h}][protocol^=http]/best[height={h}]"),
            "merge_output_format": "mkv",
            "outtmpl": str(CARPETA_DESCARGAS / f"%(title)s [{h}p].mkv"),
        }
    extra.update({"noplaylist": True, "quiet": True, "no_warnings": True,
                  "geo_bypass": True, "progress_hooks": [hook]})

    try:
        with yt_dlp.YoutubeDL(opciones_ydl(extra)) as ydl:
            ydl.download([req.url])
        emitir({"status": "done", "folder": str(CARPETA_DESCARGAS)})
    except Exception as e:
        if _es_error_bot(e):
            emitir({"status": "blocked", "message": MENSAJE_BLOQUEO})
        else:
            emitir({"status": "error", "message": str(e)[:300]})
    finally:
        descarga_activa.clear()


@app.websocket("/ws")
async def ws_progreso(ws: WebSocket):
    await ws.accept()
    clientes_ws.add(ws)
    try:
        while True:
            await ws.receive_text()  # keepalive; el cliente no manda nada útil
    except WebSocketDisconnect:
        pass
    finally:
        clientes_ws.discard(ws)


def _vigilar_padre(pid: int):
    """Si el proceso padre (Electron) muere, el backend se cierra solo.
    Evita huérfanos incluso si Electron crashea o lo matan a la fuerza."""
    def _esperar():
        try:
            import ctypes
            SYNCHRONIZE = 0x00100000
            h = ctypes.windll.kernel32.OpenProcess(SYNCHRONIZE, False, pid)
            if h:
                ctypes.windll.kernel32.WaitForSingleObject(h, 0xFFFFFFFF)
        except Exception:
            pass
        os._exit(0)
    threading.Thread(target=_esperar, daemon=True).start()


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--port", type=int, default=8765)
        parser.add_argument("--parent-pid", type=int, default=0)
        args = parser.parse_args()
        if args.parent_pid:
            _vigilar_padre(args.parent_pid)
        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
    except Exception:
        # congelado no hay consola: deja el traceback en el log de %TEMP%
        traceback.print_exc()
        raise

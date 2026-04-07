#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YTDownloader4K - YouTube Video Downloader
Author: Alejandro Zabaleta
Description: A user-friendly YouTube downloader with GUI
License: MIT
"""

__version__ = "1.6.4"

import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from io import BytesIO
import os
import sys
import urllib.request
import json
import webbrowser
import threading
import subprocess
import zipfile
import tempfile
import traceback
from pathlib import Path


# Directorio de datos de la app
APP_DATA_DIR = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / "YTDownloader4k"
FFMPEG_DIR = APP_DATA_DIR / "ffmpeg"

# Variable global para la ruta de ffmpeg
ffmpeg_location = None

# Constantes del repo
GITHUB_REPO = "ZabaHD4K/DescargadorYT"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.txt"
EXE_DOWNLOAD_URL = f"https://github.com/{GITHUB_REPO}/raw/main/YTDownloader4k.exe"


def mostrar_error(titulo, mensaje):
    """Muestra un error en messagebox, creando root temporal si no existe."""
    try:
        messagebox.showerror(titulo, mensaje)
    except Exception:
        try:
            tmp = tk.Tk()
            tmp.withdraw()
            messagebox.showerror(titulo, mensaje, parent=tmp)
            tmp.destroy()
        except Exception:
            pass


# ─── INSTANCIA ÚNICA ────────────────────────────────────────────────
def instancia_unica():
    """Verifica que solo haya una instancia de la aplicación ejecutándose."""
    if getattr(sys, 'frozen', False):
        lock_file = Path(tempfile.gettempdir()) / "ytdownloader4k.lock"

        if lock_file.exists():
            try:
                pid = int(lock_file.read_text().strip())
                import psutil
                if psutil.pid_exists(pid):
                    sys.exit(0)
            except (ValueError, ImportError, Exception):
                pass

        lock_file.write_text(str(os.getpid()))
        import atexit
        atexit.register(lambda: lock_file.unlink(missing_ok=True))

instancia_unica()


# ─── FFMPEG ─────────────────────────────────────────────────────────
def ffmpeg_disponible():
    """Comprueba si ffmpeg está disponible en el sistema o en la carpeta de la app."""
    global ffmpeg_location

    ffmpeg_exe = FFMPEG_DIR / "ffmpeg.exe"
    ffprobe_exe = FFMPEG_DIR / "ffprobe.exe"
    if ffmpeg_exe.exists() and ffprobe_exe.exists():
        ffmpeg_location = str(FFMPEG_DIR)
        return True

    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        ffmpeg_location = None
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    return False


def instalar_ffmpeg():
    """Descarga e instala ffmpeg automáticamente con ventana de progreso."""
    FFMPEG_URL = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

    ventana = tk.Tk()
    ventana.title("Installing dependencies")
    ventana.geometry("500x180")
    ventana.resizable(False, False)
    ventana.eval('tk::PlaceWindow . center')

    tk.Label(
        ventana,
        text="Installing required dependencies...",
        font=("Arial", 12, "bold")
    ).pack(pady=15)

    label_estado = tk.Label(ventana, text="Downloading FFmpeg...", font=("Arial", 10))
    label_estado.pack(pady=5)

    progress = ttk.Progressbar(ventana, length=400, mode='determinate')
    progress.pack(pady=10)

    label_detalle = tk.Label(ventana, text="This is a one-time setup", font=("Arial", 9), fg="gray")
    label_detalle.pack(pady=5)

    instalacion_ok = [False]

    def descargar_ffmpeg():
        global ffmpeg_location
        try:
            APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
            zip_path = APP_DATA_DIR / "ffmpeg.zip"

            req = urllib.request.Request(FFMPEG_URL)
            req.add_header('User-Agent', 'YTDownloader4K')

            with urllib.request.urlopen(req, timeout=120) as response:
                total = int(response.headers.get('Content-Length', 0))
                descargado = 0
                bloque = 1024 * 256

                with open(zip_path, 'wb') as f:
                    while True:
                        datos = response.read(bloque)
                        if not datos:
                            break
                        f.write(datos)
                        descargado += len(datos)

                        if total > 0:
                            porcentaje = (descargado / total) * 80
                            progress['value'] = porcentaje
                            mb_desc = descargado / (1024 * 1024)
                            mb_total = total / (1024 * 1024)
                            label_detalle.config(text=f"Downloading: {mb_desc:.1f} MB / {mb_total:.1f} MB")
                        ventana.update_idletasks()

            label_estado.config(text="Extracting FFmpeg...")
            label_detalle.config(text="Almost done...")
            progress['value'] = 85
            ventana.update_idletasks()

            FFMPEG_DIR.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zf:
                for nombre in zf.namelist():
                    basename = os.path.basename(nombre)
                    if basename in ('ffmpeg.exe', 'ffprobe.exe'):
                        datos = zf.read(nombre)
                        destino = FFMPEG_DIR / basename
                        with open(destino, 'wb') as f:
                            f.write(datos)

            progress['value'] = 95
            ventana.update_idletasks()

            zip_path.unlink(missing_ok=True)

            if (FFMPEG_DIR / "ffmpeg.exe").exists():
                ffmpeg_location = str(FFMPEG_DIR)
                instalacion_ok[0] = True
                progress['value'] = 100
                label_estado.config(text="✓ FFmpeg installed successfully", fg="green")
                label_detalle.config(text="Ready to use", fg="green")
                ventana.update_idletasks()
                ventana.after(1500, ventana.destroy)
            else:
                raise Exception("FFmpeg files not found after extraction")

        except Exception as e:
            label_estado.config(text="⚠ Error installing FFmpeg", fg="red")
            label_detalle.config(text=str(e)[:60], fg="red")
            ventana.update_idletasks()
            ventana.after(4000, ventana.destroy)

    thread = threading.Thread(target=descargar_ffmpeg, daemon=True)
    thread.start()

    ventana.mainloop()
    return instalacion_ok[0]


def verificar_dependencias():
    """Verifica que todas las dependencias estén disponibles."""
    if not ffmpeg_disponible():
        if not instalar_ffmpeg():
            mostrar_error(
                "Warning",
                "FFmpeg could not be installed.\n\n"
                "Video merging and MP3 conversion may not work.\n"
                "You can install it manually from:\n"
                "https://ffmpeg.org/download.html"
            )


# ─── AUTO-ACTUALIZACIÓN DEL EXE ────────────────────────────────────
def verificar_actualizacion_app():
    """Verifica si hay una nueva versión y ofrece auto-actualizar el .exe."""
    if not getattr(sys, 'frozen', False):
        return

    try:
        req = urllib.request.Request(VERSION_URL)
        req.add_header('User-Agent', 'YTDownloader4K')

        with urllib.request.urlopen(req, timeout=5) as response:
            latest_version = response.read().decode().strip()
            current_version = __version__

            if latest_version == current_version:
                return  # Ya estamos al día

    except Exception:
        return  # Sin conexión, seguir sin actualizar

    # Hay nueva versión — mostrar ventana de actualización
    ventana = tk.Tk()
    ventana.title("Update Available")
    ventana.geometry("500x220")
    ventana.resizable(False, False)
    ventana.eval('tk::PlaceWindow . center')

    tk.Label(
        ventana,
        text="New version available!",
        font=("Arial", 13, "bold"),
        fg="#2e7d32"
    ).pack(pady=10)

    tk.Label(
        ventana,
        text=f"Current: v{current_version}  →  New: v{latest_version}",
        font=("Arial", 10)
    ).pack(pady=5)

    label_estado = tk.Label(ventana, text="", font=("Arial", 9), fg="gray")
    label_estado.pack(pady=3)

    progress = ttk.Progressbar(ventana, length=400, mode='determinate')

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=15)

    actualizando = [False]

    def iniciar_actualizacion():
        if actualizando[0]:
            return
        actualizando[0] = True

        # Ocultar botones, mostrar progreso
        frame_botones.pack_forget()
        progress.pack(pady=10)
        label_estado.config(text="Downloading update...", fg="#1976d2")
        ventana.update_idletasks()

        def descargar_y_reemplazar():
            try:
                exe_actual = Path(sys.executable)
                exe_destino = exe_actual.parent / f"YTDownloader4k_v{latest_version}.exe"
                exe_nuevo = exe_actual.parent / "YTDownloader4k_update.exe"

                # Descargar nuevo exe con progreso
                req_dl = urllib.request.Request(EXE_DOWNLOAD_URL)
                req_dl.add_header('User-Agent', 'YTDownloader4K')

                with urllib.request.urlopen(req_dl, timeout=120) as resp:
                    total = int(resp.headers.get('Content-Length', 0))
                    descargado = 0
                    bloque = 1024 * 256

                    with open(exe_nuevo, 'wb') as f:
                        while True:
                            datos = resp.read(bloque)
                            if not datos:
                                break
                            f.write(datos)
                            descargado += len(datos)

                            if total > 0:
                                porcentaje = (descargado / total) * 100
                                progress['value'] = porcentaje
                                mb_desc = descargado / (1024 * 1024)
                                mb_total = total / (1024 * 1024)
                                label_estado.config(
                                    text=f"Downloading: {mb_desc:.1f} MB / {mb_total:.1f} MB"
                                )
                            ventana.update_idletasks()

                # Verificar que se descargó correctamente (mínimo 1MB)
                if exe_nuevo.stat().st_size < 1_000_000:
                    raise Exception("Downloaded file is too small, may be corrupted")

                progress['value'] = 100
                label_estado.config(text="Restarting with new version...", fg="green")
                ventana.update_idletasks()

                # Crear script .bat que:
                # 1. Espera a que este proceso muera
                # 2. Reemplaza el exe viejo con el nuevo
                # 3. Lanza el nuevo exe
                # 4. Se borra a sí mismo
                bat_path = exe_actual.parent / "_update.bat"
                bat_contenido = f'''@echo off
ping 127.0.0.1 -n 3 > nul
del "{exe_actual}"
move "{exe_nuevo}" "{exe_destino}"
start "" "{exe_destino}"
del "%~f0"
'''
                bat_path.write_text(bat_contenido)

                # Lanzar el bat oculto y cerrar la app
                subprocess.Popen(
                    ['cmd', '/c', str(bat_path)],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                ventana.destroy()
                sys.exit(0)

            except Exception as e:
                # Limpiar archivo parcial
                try:
                    exe_nuevo = Path(sys.executable).parent / "YTDownloader4k_update.exe"
                    exe_nuevo.unlink(missing_ok=True)
                except Exception:
                    pass

                progress.pack_forget()
                frame_botones.pack(pady=15)
                actualizando[0] = False
                label_estado.config(
                    text=f"Error: {str(e)[:50]}. Try again or skip.",
                    fg="red"
                )
                ventana.update_idletasks()

        thread = threading.Thread(target=descargar_y_reemplazar, daemon=True)
        thread.start()

    def omitir():
        ventana.destroy()

    tk.Button(
        frame_botones,
        text="Update Now",
        command=iniciar_actualizacion,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold"),
        width=20
    ).pack(side="left", padx=5)

    tk.Button(
        frame_botones,
        text="Skip",
        command=omitir,
        bg="#757575",
        fg="white",
        font=("Arial", 10),
        width=12
    ).pack(side="left", padx=5)

    ventana.mainloop()


# ─── ACTUALIZACIÓN LIBRERÍAS (SOLO PYTHON) ──────────────────────────
def verificar_actualizaciones():
    """Verifica y actualiza las librerías necesarias (solo desde Python)."""
    if getattr(sys, 'frozen', False):
        return

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True, text=True, timeout=10
        ).check_returncode()
    except Exception:
        return

    ventana = tk.Tk()
    ventana.title("Checking Updates")
    ventana.geometry("500x200")
    ventana.resizable(False, False)
    ventana.eval('tk::PlaceWindow . center')

    tk.Label(ventana, text="Checking library updates", font=("Arial", 12, "bold")).pack(pady=15)

    label_estado = tk.Label(ventana, text="Starting verification...", font=("Arial", 10))
    label_estado.pack(pady=5)

    progress = ttk.Progressbar(ventana, length=400, mode='indeterminate')
    progress.pack(pady=10)
    progress.start(10)

    label_detalle = tk.Label(ventana, text="", font=("Arial", 9), fg="gray")
    label_detalle.pack(pady=5)

    def actualizar_librerias():
        dependencias = ['yt-dlp', 'Pillow']
        actualizaciones_realizadas = []

        try:
            for i, libreria in enumerate(dependencias):
                label_estado.config(text=f"Checking {libreria}...")
                label_detalle.config(text=f"Library {i+1} of {len(dependencias)}")
                ventana.update()

                try:
                    resultado = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--upgrade", libreria],
                        capture_output=True, text=True, timeout=60
                    )
                    if "Successfully installed" in resultado.stdout:
                        actualizaciones_realizadas.append(libreria)
                        label_detalle.config(text=f"✓ {libreria} updated", fg="green")
                    else:
                        label_detalle.config(text=f"✓ {libreria} up to date", fg="blue")
                    ventana.update()
                except subprocess.TimeoutExpired:
                    label_detalle.config(text=f"⚠ Timeout updating {libreria}", fg="orange")
                    ventana.update()
                except Exception:
                    label_detalle.config(text=f"⚠ Error updating {libreria}", fg="orange")
                    ventana.update()

            progress.stop()
            progress.config(mode='determinate', value=100)

            if actualizaciones_realizadas:
                label_estado.config(text=f"✓ Updates completed ({len(actualizaciones_realizadas)})", fg="green")
                label_detalle.config(text=f"Updated: {', '.join(actualizaciones_realizadas)}", fg="green")
            else:
                label_estado.config(text="✓ All libraries are up to date", fg="blue")
                label_detalle.config(text="No updates required", fg="blue")

            ventana.update()
            ventana.after(2000, ventana.destroy)

        except Exception as e:
            progress.stop()
            label_estado.config(text="⚠ Error during verification", fg="red")
            label_detalle.config(text=str(e)[:50], fg="red")
            ventana.update()
            ventana.after(3000, ventana.destroy)

    thread = threading.Thread(target=actualizar_librerias, daemon=True)
    thread.start()
    ventana.mainloop()


# ─── OPCIONES YT-DLP ───────────────────────────────────────────────
def obtener_opciones_ydl(extras=None):
    """Devuelve opciones base de yt-dlp con ffmpeg_location si es necesario."""
    opts = {}
    if ffmpeg_location:
        opts["ffmpeg_location"] = ffmpeg_location
    if extras:
        opts.update(extras)
    return opts


# ─── VERIFICACIONES AL INICIO ──────────────────────────────────────
try:
    verificar_actualizacion_app()
except Exception as e:
    mostrar_error("Update Error", f"Error checking for updates:\n\n{e}")

try:
    verificar_dependencias()
except Exception as e:
    mostrar_error("Dependency Error", f"Error checking dependencies:\n\n{e}")

try:
    verificar_actualizaciones()
except Exception as e:
    mostrar_error("Library Error", f"Error updating libraries:\n\n{e}")


# ─── VARIABLES GLOBALES ────────────────────────────────────────────
formatos_disponibles = []
info_video = None


# ─── CARGAR VIDEO ──────────────────────────────────────────────────
def cargar_video():
    """Carga la información del video y muestra formatos disponibles."""
    global formatos_disponibles, info_video

    url = entry_url.get().strip()
    if not url:
        messagebox.showwarning("Error", "Please enter a YouTube URL.")
        return

    btn_cargar.config(state="disabled", text="Loading...")
    combo_resolucion.set("")
    combo_resolucion["values"] = []

    # Contador visual para que el usuario sepa que sigue trabajando
    cargando = [True]

    def actualizar_contador():
        segundos = 0
        while cargando[0]:
            try:
                btn_cargar.config(text=f"Loading... ({segundos}s)")
                root.update_idletasks()
            except Exception:
                break
            import time
            time.sleep(1)
            segundos += 1

    hilo_contador = threading.Thread(target=actualizar_contador, daemon=True)
    hilo_contador.start()

    def cargar():
        global formatos_disponibles, info_video
        try:
            # Lanzar 2 extracciones en paralelo con distintos clients
            # El primero que responda gana, el otro se descarta
            import concurrent.futures

            opts_default = obtener_opciones_ydl({
                "quiet": True,
                "no_warnings": True,
                "nocheckcertificate": True,
                "geo_bypass": True,
                "socket_timeout": 30,
                "extractor_retries": 1,
                "retries": 1,
                "noplaylist": True,
            })

            opts_android = obtener_opciones_ydl({
                "quiet": True,
                "no_warnings": True,
                "nocheckcertificate": True,
                "geo_bypass": True,
                "socket_timeout": 30,
                "extractor_retries": 1,
                "retries": 1,
                "noplaylist": True,
                "extractor_args": {"youtube": {"player_client": ["android"]}},
            })

            def extraer_con_opts(opts):
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(url, download=False)

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                futuro_default = pool.submit(extraer_con_opts, opts_default)
                futuro_android = pool.submit(extraer_con_opts, opts_android)

                futuros = {futuro_default: "default", futuro_android: "android"}
                resultado_info = None
                errores = []

                for futuro in concurrent.futures.as_completed(futuros, timeout=90):
                    try:
                        resultado_info = futuro.result()
                        if resultado_info:
                            # Tenemos resultado, cancelar el otro
                            for f in futuros:
                                if f is not futuro:
                                    f.cancel()
                            break
                    except Exception as e:
                        errores.append(f"{futuros[futuro]}: {e}")

            if resultado_info is None:
                if errores:
                    raise Exception("Could not load video:\n\n" + "\n".join(errores))
                raise Exception("Could not retrieve video information. The URL may be invalid or the video may be private.")

            info_video = resultado_info

            # Cargar miniatura
            try:
                thumbnail_url = info_video.get('thumbnail')
                if thumbnail_url:
                    req = urllib.request.Request(thumbnail_url)
                    req.add_header('User-Agent', 'YTDownloader4K')
                    img_data = urllib.request.urlopen(req, timeout=10).read()
                    img = Image.open(BytesIO(img_data))
                    img = img.resize((160, 90), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    label_thumbnail.config(image=photo)
                    label_thumbnail.image = photo
            except Exception:
                pass

            # Procesar formatos
            formatos_video = {}

            for f in info_video.get('formats', []):
                tiene_video = f.get('vcodec') not in ['none', None]
                height = f.get('height')

                if tiene_video and height:
                    vcodec = f.get('vcodec', 'unknown')
                    if '.' in vcodec:
                        vcodec = vcodec.split('.')[0]
                    vcodec = vcodec[:4]

                    fps = f.get('fps', 30) or 30
                    format_id = f['format_id']
                    key = f"{height}_{vcodec}_{fps}"

                    if key not in formatos_video:
                        formatos_video[key] = {
                            'height': height,
                            'format_id': format_id,
                            'fps': fps,
                            'vcodec': vcodec,
                            'label': f"{height}p ({vcodec}, {fps}fps)"
                        }

            formatos_disponibles = sorted(
                formatos_video.values(),
                key=lambda x: (x['height'], x['fps']),
                reverse=True
            )

            if not formatos_disponibles:
                raise Exception("No video formats found. The video may be restricted or unavailable.")

            formatos_disponibles.append({
                'height': 0,
                'format_id': 'bestaudio',
                'label': 'Audio Only (MP3)'
            })

            opciones = [f['label'] for f in formatos_disponibles]
            combo_resolucion["values"] = opciones
            if opciones:
                combo_resolucion.current(0)

            btn_descargar.config(state="normal")

        except Exception as e:
            error_msg = str(e)
            if not error_msg or error_msg == "None":
                error_msg = f"Unknown error occurred.\n\nDetails:\n{traceback.format_exc()}"
            messagebox.showerror("Error", f"Could not load video:\n\n{error_msg}")
        finally:
            cargando[0] = False
            btn_cargar.config(state="normal", text="Load Video")

    thread = threading.Thread(target=cargar, daemon=True)
    thread.start()


# ─── DESCARGAR VIDEO ───────────────────────────────────────────────
def descargar_video():
    """Descarga el video con el formato seleccionado."""
    if not info_video or not formatos_disponibles:
        messagebox.showwarning("Error", "Load a video first.")
        return

    seleccion_idx = combo_resolucion.current()
    if seleccion_idx < 0:
        messagebox.showwarning("Error", "Select a resolution.")
        return

    formato_sel = formatos_disponibles[seleccion_idx]
    url = entry_url.get().strip()
    carpeta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")

    btn_descargar.config(state="disabled", text="Downloading...")
    progressbar.pack(pady=5)
    label_progreso.pack(pady=2)
    progressbar['value'] = 0
    label_progreso.config(text="Starting download...")

    def hook_progreso(d):
        try:
            if d['status'] == 'downloading':
                if 'total_bytes' in d:
                    porcentaje = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif 'total_bytes_estimate' in d:
                    porcentaje = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                else:
                    porcentaje = 0

                progressbar['value'] = porcentaje

                if 'eta' in d and d['eta']:
                    eta = d['eta']
                    minutos = eta // 60
                    segundos = eta % 60
                    tiempo_str = f"{int(minutos)}m {int(segundos)}s" if minutos > 0 else f"{int(segundos)}s"
                    velocidad = d.get('speed', 0)
                    if velocidad:
                        velocidad_mb = velocidad / (1024 * 1024)
                        label_progreso.config(text=f"Downloading: {porcentaje:.1f}% | {velocidad_mb:.2f} MB/s | Remaining: {tiempo_str}")
                    else:
                        label_progreso.config(text=f"Downloading: {porcentaje:.1f}% | Remaining: {tiempo_str}")
                else:
                    label_progreso.config(text=f"Downloading: {porcentaje:.1f}%")

                root.update_idletasks()
            elif d['status'] == 'finished':
                progressbar['value'] = 100
                label_progreso.config(text="Processing file...")
                root.update_idletasks()
        except Exception:
            pass

    def descargar():
        try:
            if formato_sel['height'] == 0:  # Audio MP3
                opciones = obtener_opciones_ydl({
                    "format": "bestaudio/best",
                    "outtmpl": os.path.join(carpeta_descargas, "%(title)s.%(ext)s"),
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                    "noplaylist": True,
                    "nocheckcertificate": True,
                    "progress_hooks": [hook_progreso],
                })
            else:  # Video
                format_id = formato_sel['format_id']
                height = formato_sel['height']

                opciones = obtener_opciones_ydl({
                    "format": f"{format_id}+bestaudio/bestvideo[height={height}]+bestaudio/best[height={height}]",
                    "merge_output_format": "mkv",
                    "outtmpl": os.path.join(carpeta_descargas, f"%(title)s [{height}p].mkv"),
                    "noplaylist": True,
                    "nocheckcertificate": True,
                    "progress_hooks": [hook_progreso],
                })

            opciones.update({
                "noplaylist": True,
                "quiet": False,
                "nocheckcertificate": True,
                "geo_bypass": True,
            })

            with yt_dlp.YoutubeDL(opciones) as ydl:
                ydl.download([url])

            progressbar['value'] = 100
            label_progreso.config(text="✓ Download complete")
            messagebox.showinfo("Complete", f"Downloaded to:\n{carpeta_descargas}")

        except Exception as e:
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
                error_msg += "\n\nFFmpeg may not be installed correctly. Restart the app to reinstall it."
            elif "urlopen" in error_msg.lower() or "connection" in error_msg.lower():
                error_msg += "\n\nCheck your internet connection and try again."
            messagebox.showerror("Download Error", f"Error during download:\n\n{error_msg}")
        finally:
            btn_descargar.config(state="normal", text="Download")
            progressbar.pack_forget()
            label_progreso.pack_forget()

    thread = threading.Thread(target=descargar, daemon=True)
    thread.start()


# ─── INTERFAZ GRÁFICA ──────────────────────────────────────────────
root = tk.Tk()
root.title(f"YTDownloader4K v{__version__}")
root.geometry("520x420")
root.resizable(False, False)

tk.Label(root, text="YouTube 4K Downloader", font=("Arial", 14, "bold")).pack(pady=10)

tk.Label(root, text="Video URL:").pack()
entry_url = tk.Entry(root, width=60)
entry_url.pack(pady=5)

btn_cargar = tk.Button(
    root,
    text="Load Video",
    command=cargar_video,
    bg="#1976d2",
    fg="white",
    font=("Arial", 10, "bold"),
    width=15
)
btn_cargar.pack(pady=10)

label_thumbnail = tk.Label(root)
label_thumbnail.pack(pady=5)

tk.Label(root, text="Available resolution:").pack(pady=5)
combo_resolucion = ttk.Combobox(root, state="readonly", width=40)
combo_resolucion.pack()

btn_descargar = tk.Button(
    root,
    text="Download",
    command=descargar_video,
    bg="#d32f2f",
    fg="white",
    font=("Arial", 12, "bold"),
    width=20,
    state="disabled"
)
btn_descargar.pack(pady=10)

progressbar = ttk.Progressbar(root, length=400, mode='determinate')
label_progreso = tk.Label(root, text="", font=("Arial", 9), fg="#1976d2")

tk.Label(root, text="Folder: Downloads | Author: Alejandro Zabaleta", font=("Arial", 8), fg="gray").pack(side="bottom", pady=5)


def cerrar_app():
    """Cierra la app y mata todos los procesos hijos."""
    try:
        root.destroy()
    except Exception:
        pass
    os._exit(0)


root.protocol("WM_DELETE_WINDOW", cerrar_app)
root.mainloop()

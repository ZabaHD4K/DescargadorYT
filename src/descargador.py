#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YTDownloader4K - YouTube Video Downloader
Author: Alejandro Zabaleta
Description: A user-friendly YouTube downloader with GUI
License: MIT
"""

__version__ = "1.5.0"

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
import shutil
from pathlib import Path


# Directorio de datos de la app
APP_DATA_DIR = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / "YTDownloader4k"
FFMPEG_DIR = APP_DATA_DIR / "ffmpeg"

# Variable global para la ruta de ffmpeg
ffmpeg_location = None


# Evitar múltiples instancias
def instancia_unica():
    """Verifica que solo haya una instancia de la aplicación ejecutándose."""
    if getattr(sys, 'frozen', False):
        import tempfile
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


def ffmpeg_disponible():
    """Comprueba si ffmpeg está disponible en el sistema o en la carpeta de la app."""
    global ffmpeg_location

    # Comprobar en la carpeta de la app
    ffmpeg_exe = FFMPEG_DIR / "ffmpeg.exe"
    ffprobe_exe = FFMPEG_DIR / "ffprobe.exe"
    if ffmpeg_exe.exists() and ffprobe_exe.exists():
        ffmpeg_location = str(FFMPEG_DIR)
        return True

    # Comprobar en PATH
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        ffmpeg_location = None  # Está en PATH, no hace falta especificar
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
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

    label_estado = tk.Label(
        ventana,
        text="Downloading FFmpeg...",
        font=("Arial", 10)
    )
    label_estado.pack(pady=5)

    progress = ttk.Progressbar(ventana, length=400, mode='determinate')
    progress.pack(pady=10)

    label_detalle = tk.Label(
        ventana,
        text="This is a one-time setup",
        font=("Arial", 9),
        fg="gray"
    )
    label_detalle.pack(pady=5)

    instalacion_ok = [False]

    def descargar_ffmpeg():
        global ffmpeg_location
        try:
            APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
            zip_path = APP_DATA_DIR / "ffmpeg.zip"

            # Descargar con progreso
            req = urllib.request.Request(FFMPEG_URL)
            req.add_header('User-Agent', 'YTDownloader4K')

            with urllib.request.urlopen(req, timeout=60) as response:
                total = int(response.headers.get('Content-Length', 0))
                descargado = 0
                bloque = 1024 * 256  # 256KB

                with open(zip_path, 'wb') as f:
                    while True:
                        datos = response.read(bloque)
                        if not datos:
                            break
                        f.write(datos)
                        descargado += len(datos)

                        if total > 0:
                            porcentaje = (descargado / total) * 80  # 80% para descarga
                            progress['value'] = porcentaje
                            mb_desc = descargado / (1024 * 1024)
                            mb_total = total / (1024 * 1024)
                            label_detalle.config(
                                text=f"Downloading: {mb_desc:.1f} MB / {mb_total:.1f} MB"
                            )
                        ventana.update_idletasks()

            # Extraer
            label_estado.config(text="Extracting FFmpeg...")
            label_detalle.config(text="Almost done...")
            progress['value'] = 85
            ventana.update_idletasks()

            FFMPEG_DIR.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Buscar ffmpeg.exe y ffprobe.exe dentro del zip
                for nombre in zf.namelist():
                    basename = os.path.basename(nombre)
                    if basename in ('ffmpeg.exe', 'ffprobe.exe'):
                        # Extraer al directorio de ffmpeg
                        datos = zf.read(nombre)
                        destino = FFMPEG_DIR / basename
                        with open(destino, 'wb') as f:
                            f.write(datos)

            progress['value'] = 95
            ventana.update_idletasks()

            # Limpiar zip
            zip_path.unlink(missing_ok=True)

            # Verificar
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
            messagebox.showwarning(
                "Warning",
                "FFmpeg could not be installed.\n\n"
                "Video merging and MP3 conversion may not work.\n"
                "You can install it manually from:\n"
                "https://ffmpeg.org/download.html"
            )


def verificar_actualizacion_app():
    """Verifica si hay una nueva versión disponible en GitHub."""
    GITHUB_REPO = "ZabaHD4K/DescargadorYT"
    VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.txt"
    DOWNLOAD_URL = f"https://github.com/{GITHUB_REPO}/raw/main/YTDownloader4k.exe"

    if not getattr(sys, 'frozen', False):
        return

    try:
        req = urllib.request.Request(VERSION_URL)
        req.add_header('User-Agent', 'YTDownloader4K')

        with urllib.request.urlopen(req, timeout=5) as response:
            latest_version = response.read().decode().strip()
            current_version = __version__

            if latest_version != current_version:
                ventana_update = tk.Tk()
                ventana_update.title("Update Available")
                ventana_update.geometry("450x200")
                ventana_update.resizable(False, False)
                ventana_update.eval('tk::PlaceWindow . center')

                tk.Label(
                    ventana_update,
                    text="New version available!",
                    font=("Arial", 13, "bold"),
                    fg="#2e7d32"
                ).pack(pady=15)

                tk.Label(
                    ventana_update,
                    text=f"Current version: v{current_version}  →  New version: v{latest_version}",
                    font=("Arial", 10)
                ).pack(pady=5)

                tk.Label(
                    ventana_update,
                    text="Your browser will open to download the update.",
                    font=("Arial", 9),
                    fg="gray"
                ).pack(pady=5)

                def ir_a_descarga():
                    webbrowser.open(DOWNLOAD_URL)
                    ventana_update.destroy()

                def omitir():
                    ventana_update.destroy()

                frame_botones = tk.Frame(ventana_update)
                frame_botones.pack(pady=20)

                tk.Button(
                    frame_botones,
                    text="Download Update",
                    command=ir_a_descarga,
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

                ventana_update.mainloop()

    except Exception:
        pass


def verificar_actualizaciones():
    """Verifica y actualiza las librerías necesarias (solo cuando se ejecuta desde Python)."""
    if getattr(sys, 'frozen', False):
        return

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True, text=True, timeout=10
        ).check_returncode()
    except Exception:
        return

    ventana_actualizacion = tk.Tk()
    ventana_actualizacion.title("Checking Updates")
    ventana_actualizacion.geometry("500x200")
    ventana_actualizacion.resizable(False, False)
    ventana_actualizacion.eval('tk::PlaceWindow . center')

    tk.Label(
        ventana_actualizacion,
        text="Checking library updates",
        font=("Arial", 12, "bold")
    ).pack(pady=15)

    label_estado = tk.Label(
        ventana_actualizacion,
        text="Starting verification...",
        font=("Arial", 10)
    )
    label_estado.pack(pady=5)

    progress = ttk.Progressbar(
        ventana_actualizacion,
        length=400,
        mode='indeterminate'
    )
    progress.pack(pady=10)
    progress.start(10)

    label_detalle = tk.Label(
        ventana_actualizacion,
        text="",
        font=("Arial", 9),
        fg="gray"
    )
    label_detalle.pack(pady=5)

    def actualizar_librerias():
        dependencias = ['yt-dlp', 'Pillow']
        actualizaciones_realizadas = []

        try:
            for i, libreria in enumerate(dependencias):
                label_estado.config(text=f"Checking {libreria}...")
                label_detalle.config(text=f"Library {i+1} of {len(dependencias)}")
                ventana_actualizacion.update()

                try:
                    resultado = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--upgrade", libreria],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if "Successfully installed" in resultado.stdout:
                        actualizaciones_realizadas.append(libreria)
                        label_detalle.config(text=f"✓ {libreria} updated", fg="green")
                    else:
                        label_detalle.config(text=f"✓ {libreria} up to date", fg="blue")
                    ventana_actualizacion.update()
                except subprocess.TimeoutExpired:
                    label_detalle.config(text=f"⚠ Timeout updating {libreria}", fg="orange")
                    ventana_actualizacion.update()
                except Exception:
                    label_detalle.config(text=f"⚠ Error updating {libreria}", fg="orange")
                    ventana_actualizacion.update()

            progress.stop()
            progress.config(mode='determinate', value=100)

            if actualizaciones_realizadas:
                label_estado.config(
                    text=f"✓ Updates completed ({len(actualizaciones_realizadas)})",
                    fg="green"
                )
                label_detalle.config(
                    text=f"Updated: {', '.join(actualizaciones_realizadas)}",
                    fg="green"
                )
            else:
                label_estado.config(
                    text="✓ All libraries are up to date",
                    fg="blue"
                )
                label_detalle.config(text="No updates required", fg="blue")

            ventana_actualizacion.update()
            ventana_actualizacion.after(2000, ventana_actualizacion.destroy)

        except Exception as e:
            progress.stop()
            label_estado.config(text="⚠ Error during verification", fg="red")
            label_detalle.config(text=str(e)[:50], fg="red")
            ventana_actualizacion.update()
            ventana_actualizacion.after(3000, ventana_actualizacion.destroy)

    thread = threading.Thread(target=actualizar_librerias, daemon=True)
    thread.start()

    ventana_actualizacion.mainloop()


def obtener_opciones_ydl(extras=None):
    """Devuelve opciones base de yt-dlp con ffmpeg_location si es necesario."""
    opts = {}
    if ffmpeg_location:
        opts["ffmpeg_location"] = ffmpeg_location
    if extras:
        opts.update(extras)
    return opts


# Ejecutar verificaciones al inicio
verificar_actualizacion_app()
verificar_dependencias()
verificar_actualizaciones()


# Variables globales
formatos_disponibles = []
info_video = None


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

    def cargar():
        global formatos_disponibles, info_video
        try:
            ydl_opts = obtener_opciones_ydl({
                "quiet": True,
                "no_warnings": True,
                "nocheckcertificate": True,
                "geo_bypass": True,
                "socket_timeout": 15,
            })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_video = ydl.extract_info(url, download=False)

            # Cargar miniatura
            try:
                thumbnail_url = info_video.get('thumbnail')
                if thumbnail_url:
                    img_data = urllib.request.urlopen(thumbnail_url).read()
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

            formatos_disponibles.append({
                'height': 0,
                'format_id': 'bestaudio',
                'label': 'Audio Only (MP3)'
            })

            opciones = [f['label'] for f in formatos_disponibles]
            combo_resolucion["values"] = opciones
            if opciones:
                combo_resolucion.current(0)

            btn_cargar.config(state="normal", text="Load Video")
            btn_descargar.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"Could not load video:\n\n{str(e)}")
            btn_cargar.config(state="normal", text="Load Video")

    thread = threading.Thread(target=cargar, daemon=True)
    thread.start()


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
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                total = d['total_bytes']
                descargado = d['downloaded_bytes']
                porcentaje = (descargado / total) * 100
            elif 'total_bytes_estimate' in d:
                total = d['total_bytes_estimate']
                descargado = d['downloaded_bytes']
                porcentaje = (descargado / total) * 100
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
            btn_descargar.config(state="normal", text="Download")
            messagebox.showinfo("Complete", f"Downloaded to:\n{carpeta_descargas}")
            progressbar.pack_forget()
            label_progreso.pack_forget()

        except Exception as e:
            btn_descargar.config(state="normal", text="Download")
            progressbar.pack_forget()
            label_progreso.pack_forget()
            messagebox.showerror("Error", f"Error during download:\n\n{str(e)}")

    thread = threading.Thread(target=descargar, daemon=True)
    thread.start()


# Interfaz gráfica
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

root.mainloop()

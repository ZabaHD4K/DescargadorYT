#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YTDownloader4K - YouTube Video Downloader
Author: Alejandro Zabaleta
Description: A user-friendly YouTube downloader with GUI
License: MIT
"""

__version__ = "1.0.1"

import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import sys
import threading
import urllib.request
import json
import webbrowser


def verificar_actualizacion_app():
    """Verifica si hay una nueva versión disponible en GitHub."""
    GITHUB_REPO = "ZabaHD4K/DescargadorYT"
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    DOWNLOAD_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"
    
    # Solo verificar si se está ejecutando como .exe
    if not getattr(sys, 'frozen', False):
        return  # No hacer nada si se ejecuta desde Python directamente
    
    try:
        # Obtener la última versión desde GitHub
        req = urllib.request.Request(GITHUB_API_URL)
        req.add_header('User-Agent', 'YTDownloader4K')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            latest_version = data['tag_name'].lstrip('v')
            current_version = __version__
            
            # Comparar versiones
            if latest_version != current_version:
                # Hay una nueva versión disponible
                ventana_update = tk.Tk()
                ventana_update.title("Actualización disponible")
                ventana_update.geometry("450x200")
                ventana_update.resizable(False, False)
                ventana_update.eval('tk::PlaceWindow . center')
                
                tk.Label(
                    ventana_update,
                    text=f"¡Nueva versión disponible!",
                    font=("Arial", 13, "bold"),
                    fg="#2e7d32"
                ).pack(pady=15)
                
                tk.Label(
                    ventana_update,
                    text=f"Versión actual: v{current_version}  →  Nueva versión: v{latest_version}",
                    font=("Arial", 10)
                ).pack(pady=5)
                
                tk.Label(
                    ventana_update,
                    text="Se abrirá tu navegador para descargar la actualización.",
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
                    text="Descargar Actualización",
                    command=ir_a_descarga,
                    bg="#4CAF50",
                    fg="white",
                    font=("Arial", 10, "bold"),
                    width=20
                ).pack(side="left", padx=5)
                
                tk.Button(
                    frame_botones,
                    text="Omitir",
                    command=omitir,
                    bg="#757575",
                    fg="white",
                    font=("Arial", 10),
                    width=12
                ).pack(side="left", padx=5)
                
                ventana_update.mainloop()
                
    except Exception as e:
        # Si hay algún error al verificar, simplemente continuar sin actualizar
        pass


def verificar_actualizaciones():
    """Verifica y actualiza las librerías necesarias."""
    ventana_actualizacion = tk.Tk()
    ventana_actualizacion.title("Verificando actualizaciones")
    ventana_actualizacion.geometry("500x200")
    ventana_actualizacion.resizable(False, False)
    
    # Centrar ventana
    ventana_actualizacion.eval('tk::PlaceWindow . center')
    
    tk.Label(
        ventana_actualizacion,
        text="Verificando actualizaciones de librerías",
        font=("Arial", 12, "bold")
    ).pack(pady=15)
    
    label_estado = tk.Label(
        ventana_actualizacion,
        text="Iniciando verificación...",
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
        """Función que ejecuta la actualización en segundo plano."""
        librerias = ['yt-dlp', 'tkinter']
        actualizaciones_realizadas = []
        
        try:
            for i, libreria in enumerate(librerias):
                # Actualizar estado
                label_estado.config(text=f"Verificando {libreria}...")
                label_detalle.config(text=f"Librería {i+1} de {len(librerias)}")
                ventana_actualizacion.update()
                
                # Verificar versión actual e instalar/actualizar
                try:
                    if libreria == 'yt-dlp':
                        resultado = subprocess.run(
                            [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if "Successfully installed" in resultado.stdout or "Requirement already satisfied" in resultado.stdout:
                            if "Successfully installed" in resultado.stdout:
                                actualizaciones_realizadas.append(libreria)
                                label_detalle.config(text=f"✓ {libreria} actualizado", fg="green")
                            else:
                                label_detalle.config(text=f"✓ {libreria} ya está actualizado", fg="blue")
                        ventana_actualizacion.update()
                except subprocess.TimeoutExpired:
                    label_detalle.config(text=f"⚠ Timeout en {libreria}", fg="orange")
                    ventana_actualizacion.update()
                except Exception as e:
                    label_detalle.config(text=f"⚠ Error en {libreria}", fg="orange")
                    ventana_actualizacion.update()
            
            # Detener barra de progreso
            progress.stop()
            progress.config(mode='determinate', value=100)
            
            # Mensaje final
            if actualizaciones_realizadas:
                label_estado.config(
                    text=f"✓ Actualizaciones completadas ({len(actualizaciones_realizadas)})",
                    fg="green"
                )
                label_detalle.config(
                    text=f"Librerías actualizadas: {', '.join(actualizaciones_realizadas)}",
                    fg="green"
                )
            else:
                label_estado.config(
                    text="✓ Todas las librerías están actualizadas",
                    fg="blue"
                )
                label_detalle.config(text="No se requieren actualizaciones", fg="blue")
            
            ventana_actualizacion.update()
            ventana_actualizacion.after(2000, ventana_actualizacion.destroy)
            
        except Exception as e:
            progress.stop()
            label_estado.config(text="⚠ Error durante la verificación", fg="red")
            label_detalle.config(text=str(e)[:50], fg="red")
            ventana_actualizacion.update()
            ventana_actualizacion.after(3000, ventana_actualizacion.destroy)
    
    # Ejecutar en hilo separado para no bloquear la interfaz
    thread = threading.Thread(target=actualizar_librerias, daemon=True)
    thread.start()
    
    ventana_actualizacion.mainloop()


# Ejecutar verificación de actualizaciones de la aplicación
verificar_actualizacion_app()

# Ejecutar verificación de actualizaciones de librerías
verificar_actualizaciones()


def descargar_video():
    url = entry_url.get().strip()
    calidad = combo_calidad.get()

    if not url:
        messagebox.showwarning("Error", "Por favor introduce una URL de YouTube.")
        return

    carpeta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")

    if calidad == "Máxima calidad (video + audio)":
        formato = "bestvideo+bestaudio/best"
        merge_format = "mp4"
    elif calidad == "Solo audio (MP3)":
        formato = "bestaudio"
        merge_format = "mp3"
    else:
        formato = "bestvideo[height<=720]+bestaudio/best"
        merge_format = "mp4"

    # Configurar ruta de FFmpeg si está bundleado en el ejecutable
    ffmpeg_location = None
    if getattr(sys, 'frozen', False):
        # Ejecutando como .exe - buscar FFmpeg en el directorio temporal de PyInstaller
        base_path = sys._MEIPASS
        ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
        if os.path.exists(ffmpeg_path):
            ffmpeg_location = base_path

    opciones = {
        "format": formato,
        "merge_output_format": merge_format,
        "outtmpl": os.path.join(carpeta_descargas, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": False,
        "postprocessors": [],
        "nocheckcertificate": True,  # Evita errores de certificado SSL
        "geo_bypass": True,  # Intenta eludir restricciones geográficas
        "extractor_retries": 3,  # Reintentos en caso de fallo
    }

    # Añadir ubicación de FFmpeg si está disponible
    if ffmpeg_location:
        opciones["ffmpeg_location"] = ffmpeg_location

    if calidad == "Solo audio (MP3)":
        opciones["postprocessors"].append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        })

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([url])
        messagebox.showinfo(
            "Descarga completa",
            f" El video se ha descargado correctamente en:\n{carpeta_descargas}"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema durante la descarga:\n\n{e}")


root = tk.Tk()
root.title("Descargador de YouTube (yt-dlp)")
root.geometry("480x260")
root.resizable(False, False)

tk.Label(root, text="Descargador de YouTube", font=("Arial", 14, "bold")).pack(pady=10)
tk.Label(root, text="Introduce la URL del video:").pack()

entry_url = tk.Entry(root, width=60)
entry_url.pack(pady=5)

tk.Label(root, text="Selecciona calidad:").pack(pady=5)
combo_calidad = ttk.Combobox(root, values=[
    "Máxima calidad (video + audio)",
    "720p (video + audio)",
    "Solo audio (MP3)"
], state="readonly", width=30)
combo_calidad.current(0)
combo_calidad.pack()

btn_descargar = tk.Button(
    root,
    text="Descargar",
    command=descargar_video,
    bg="#d32f2f",
    fg="white",
    font=("Arial", 12, "bold"),
    relief="raised",
    width=20
)
btn_descargar.pack(pady=20)

tk.Label(root, text="Los archivos se guardarán en tu carpeta de Descargas", font=("Arial", 8), fg="gray").pack()
tk.Label(root, text="Desarrollado con yt-dlp + ffmpeg", font=("Arial", 8), fg="gray").pack(side="bottom", pady=5)

root.mainloop()

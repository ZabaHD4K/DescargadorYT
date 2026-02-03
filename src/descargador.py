#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YTDownloader4K - YouTube Video Downloader
Author: Alejandro Zabaleta
Description: A user-friendly YouTube downloader with GUI
License: MIT
"""

__version__ = "1.3.3"

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
import os
import subprocess
import sys
import threading
import urllib.request
import json
import webbrowser
import sys
from pathlib import Path
from io import BytesIO


# Evitar múltiples instancias
def instancia_unica():
    """Verifica que solo haya una instancia de la aplicación ejecutándose."""
    if getattr(sys, 'frozen', False):
        import tempfile
        lock_file = Path(tempfile.gettempdir()) / "ytdownloader4k.lock"
        
        if lock_file.exists():
            # Ya hay una instancia ejecutándose
            sys.exit(0)
        else:
            # Crear archivo lock
            lock_file.touch()
            import atexit
            atexit.register(lambda: lock_file.unlink(missing_ok=True))

instancia_unica()


def verificar_actualizacion_app():
    """Verifica si hay una nueva versión disponible en GitHub."""
    GITHUB_REPO = "ZabaHD4K/DescargadorYT"
    VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.txt"
    DOWNLOAD_URL = f"https://github.com/{GITHUB_REPO}/raw/main/YTDownloader4k.exe"
    
    # Solo verificar si se está ejecutando como .exe
    if not getattr(sys, 'frozen', False):
        return  # No hacer nada si se ejecuta desde Python directamente
    
    try:
        # Obtener la última versión desde GitHub
        req = urllib.request.Request(VERSION_URL)
        req.add_header('User-Agent', 'YTDownloader4K')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            latest_version = response.read().decode().strip()
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


# Variables globales
formatos_disponibles = []
info_video = None


def cargar_video():
    """Carga la información del video y muestra formatos disponibles."""
    global formatos_disponibles, info_video
    
    url = entry_url.get().strip()
    if not url:
        messagebox.showwarning("Error", "Por favor introduce una URL de YouTube.")
        return
    
    btn_cargar.config(state="disabled", text="Cargando...")
    combo_resolucion.set("")
    combo_resolucion["values"] = []
    
    def cargar():
        global formatos_disponibles, info_video
        try:
            # Ejecutar yt-dlp como subprocess para obtener TODOS los formatos incluyendo DASH
            cmd = [
                "yt-dlp",
                "-J",  # Output JSON con toda la info
                "--no-warnings",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode != 0:
                raise Exception(f"Error al obtener información del video")
            
            info_video = json.loads(result.stdout)
            
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
            except:
                pass
            
            # Procesar formatos - obtener TODOS los formatos de video disponibles
            formatos_video = {}
            
            for f in info_video.get('formats', []):
                # Solo formatos con video
                tiene_video = f.get('vcodec') not in ['none', None]
                height = f.get('height')
                
                if tiene_video and height:
                    vcodec = f.get('vcodec', 'unknown')
                    # Limpiar nombre del codec
                    if '.' in vcodec:
                        vcodec = vcodec.split('.')[0]
                    vcodec = vcodec[:4]
                    
                    fps = f.get('fps', 30) or 30
                    format_id = f['format_id']
                    
                    # Crear clave única por resolución, codec y fps
                    key = f"{height}_{vcodec}_{fps}"
                    
                    # Guardar si no existe o si tiene mejor bitrate
                    if key not in formatos_video:
                        formatos_video[key] = {
                            'height': height,
                            'format_id': format_id,
                            'fps': fps,
                            'vcodec': vcodec,
                            'label': f"{height}p ({vcodec}, {fps}fps)"
                        }
            
            # Ordenar por resolución descendente, luego por FPS
            formatos_disponibles = sorted(
                formatos_video.values(), 
                key=lambda x: (x['height'], x['fps']), 
                reverse=True
            )
            
            # Agregar opción de audio
            formatos_disponibles.append({
                'height': 0,
                'format_id': 'bestaudio',
                'label': 'Solo Audio (MP3)'
            })
            
            # Actualizar combobox
            opciones = [f['label'] for f in formatos_disponibles]
            combo_resolucion["values"] = opciones
            if opciones:
                combo_resolucion.current(0)
            
            btn_cargar.config(state="normal", text="Cargar Video")
            btn_descargar.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el video:\n\n{str(e)}")
            btn_cargar.config(state="normal", text="Cargar Video")
    
    thread = threading.Thread(target=cargar, daemon=True)
    thread.start()


def descargar_video():
    """Descarga el video con el formato seleccionado."""
    if not info_video or not formatos_disponibles:
        messagebox.showwarning("Error", "Primero carga un video.")
        return
    
    seleccion_idx = combo_resolucion.current()
    if seleccion_idx < 0:
        messagebox.showwarning("Error", "Selecciona una resolución.")
        return
    
    formato_sel = formatos_disponibles[seleccion_idx]
    url = entry_url.get().strip()
    carpeta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")
    
    btn_descargar.config(state="disabled", text="Descargando...")
    progressbar.pack(pady=5)
    label_progreso.pack(pady=2)
    progressbar['value'] = 0
    label_progreso.config(text="Iniciando descarga...")
    
    def hook_progreso(d):
        if d['status'] == 'downloading':
            # Calcular porcentaje
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
            
            # Actualizar barra
            progressbar['value'] = porcentaje
            
            # Calcular tiempo estimado
            if 'eta' in d and d['eta']:
                eta = d['eta']
                minutos = eta // 60
                segundos = eta % 60
                tiempo_str = f"{int(minutos)}m {int(segundos)}s" if minutos > 0 else f"{int(segundos)}s"
                velocidad = d.get('speed', 0)
                if velocidad:
                    velocidad_mb = velocidad / (1024 * 1024)
                    label_progreso.config(text=f"Descargando: {porcentaje:.1f}% | {velocidad_mb:.2f} MB/s | Quedan: {tiempo_str}")
                else:
                    label_progreso.config(text=f"Descargando: {porcentaje:.1f}% | Quedan: {tiempo_str}")
            else:
                label_progreso.config(text=f"Descargando: {porcentaje:.1f}%")
            
            root.update_idletasks()
        elif d['status'] == 'finished':
            progressbar['value'] = 100
            label_progreso.config(text="Procesando archivo...")
            root.update_idletasks()
    
    def descargar():
        try:
            # Configurar opciones según selección
            if formato_sel['height'] == 0:  # Audio MP3
                opciones = {
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
                }
            else:  # Video
                # Intentar descargar el formato específico + mejor audio
                format_id = formato_sel['format_id']
                height = formato_sel['height']
                
                opciones = {
                    # Intentar formato específico + audio, si falla usar bestvideo de esa altura + audio
                    "format": f"{format_id}+bestaudio/bestvideo[height={height}]+bestaudio/best[height={height}]",
                    "merge_output_format": "mkv",
                    "outtmpl": os.path.join(carpeta_descargas, f"%(title)s [{height}p].mkv"),
                    "noplaylist": True,
                    "nocheckcertificate": True,
                    "progress_hooks": [hook_progreso],
                }
            
            # Opciones comunes
            opciones.update({
                "noplaylist": True,
                "quiet": False,
                "nocheckcertificate": True,
                "geo_bypass": True,
                # NO usar ios/android en descarga, dejar que yt-dlp use el método por defecto
            })
            
            # Descargar
            with yt_dlp.YoutubeDL(opciones) as ydl:
                ydl.download([url])
            
            progressbar['value'] = 100
            label_progreso.config(text="✓ Descarga completa")
            btn_descargar.config(state="normal", text="Descargar")
            messagebox.showinfo("Completo", f"Descargado en:\n{carpeta_descargas}")
            progressbar.pack_forget()
            label_progreso.pack_forget()
            
        except Exception as e:
            btn_descargar.config(state="normal", text="Descargar")
            progressbar.pack_forget()
            label_progreso.pack_forget()
            messagebox.showerror("Error", f"Error durante la descarga:\n\n{str(e)}")
    
    thread = threading.Thread(target=descargar, daemon=True)
    thread.start()


# Interfaz gráfica
root = tk.Tk()
root.title(f"YTDownloader4K v{__version__}")
root.geometry("520x420")
root.resizable(False, False)

# Título
tk.Label(root, text="Descargador de YouTube 4K", font=("Arial", 14, "bold")).pack(pady=10)

# URL
tk.Label(root, text="URL del video:").pack()
entry_url = tk.Entry(root, width=60)
entry_url.pack(pady=5)

# Botón cargar
btn_cargar = tk.Button(
    root,
    text="Cargar Video",
    command=cargar_video,
    bg="#1976d2",
    fg="white",
    font=("Arial", 10, "bold"),
    width=15
)
btn_cargar.pack(pady=10)

# Miniatura
label_thumbnail = tk.Label(root)
label_thumbnail.pack(pady=5)

# Selector de resolución
tk.Label(root, text="Resolución disponible:").pack(pady=5)
combo_resolucion = ttk.Combobox(root, state="readonly", width=40)
combo_resolucion.pack()

# Botón descargar
btn_descargar = tk.Button(
    root,
    text="Descargar",
    command=descargar_video,
    bg="#d32f2f",
    fg="white",
    font=("Arial", 12, "bold"),
    width=20,
    state="disabled"
)
btn_descargar.pack(pady=10)

# Barra de progreso (oculta por defecto)
progressbar = ttk.Progressbar(root, length=400, mode='determinate')
label_progreso = tk.Label(root, text="", font=("Arial", 9), fg="#1976d2")

# Footer
tk.Label(root, text="Carpeta: Descargas | Autor: Alejandro Zabaleta", font=("Arial", 8), fg="gray").pack(side="bottom", pady=5)

root.mainloop()

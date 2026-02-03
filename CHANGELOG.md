# 📝 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [1.4.0] - 2026-02-03

### ✨ Added
- **Full English interface**: Complete translation of the application to English
- **Real-time progress bar**: Shows exact download progress with continuously updated percentage
- **Download speed indicator**: Displays current download speed in MB/s
- **Estimated time remaining**: Shows time left to complete download in smart format (minutes and seconds)
- **Processing indicator**: Visual message when processing the final file after download
- **Enhanced progress hook**: Callback system that updates the interface in real-time with detailed information

### 🔧 Improved
- Interface now displays detailed information throughout the entire download process
- Better visual feedback for users with informative messages
- Progress bar update optimization to prevent flickering

### 🐛 Fixed
- Better handling of cases where estimated time information is unavailable
- Correction in percentage calculation when only total bytes estimation is available

---

## [1.3.3] - 2026-02-03

### ✨ Added
- Real-time progress bar during download
- Download speed indicator (MB/s)
- Estimated time remaining (smart format)
- Visual processing indicator at completion
- Enhanced progress hook system

### 🔧 Improved
- Interface shows detailed information during the entire download process
- Better visual feedback with informative messages
- Optimized progress bar updates

### 🐛 Fixed
- Better handling when ETA information is unavailable
- Fixed percentage calculation with byte estimation

---

## [1.3.2] - 2026-01-XX

### ✨ Añadido
- Verificación automática de actualizaciones de librerías al inicio
- Ventana de estado para mostrar el progreso de las actualizaciones
- Sistema de notificación de actualizaciones de la aplicación

### 🔧 Mejorado
- Optimización del proceso de extracción de formatos de video
- Mejor manejo de códecs y fps en la lista de resoluciones

---

## [1.3.1] - 2025-12-XX

### ✨ Añadido
- Soporte para formatos DASH de YouTube
- Detección de múltiples códecs (VP9, AVC1, etc.)
- Información detallada de FPS para cada resolución

### 🔧 Mejorado
- Extracción de información de video usando subprocess con JSON
- Mejor ordenamiento de formatos disponibles por resolución y FPS

---

## [1.3.0] - 2025-11-XX

### ✨ Añadido
- Selector inteligente de resoluciones con todos los formatos disponibles
- Vista previa de miniatura del video
- Información detallada de códecs para cada formato
- Opción de descarga de solo audio en formato MP3
- Carpeta de descargas automática (Downloads)

### 🔧 Mejorado
- Interfaz gráfica completamente rediseñada
- Mejor manejo de errores y mensajes informativos
- Optimización del proceso de descarga

---

## [1.2.0] - 2025-10-XX

### ✨ Añadido
- Interfaz gráfica con Tkinter
- Sistema de descarga con yt-dlp
- Bypass geográfico automático
- Soporte para descargas de video y audio

### 🔧 Características iniciales
- Descarga de videos de YouTube
- Interfaz simple y funcional
- Guardar en carpeta Downloads

---

## [1.1.0] - 2025-09-XX

### ✨ Añadido
- Primera versión funcional
- Descarga básica de videos

---

## Leyenda

- ✨ **Añadido** - para nuevas características
- 🔧 **Mejorado** - para cambios en funcionalidad existente
- 🐛 **Corregido** - para corrección de errores
- 🗑️ **Eliminado** - para características eliminadas
- 🔒 **Seguridad** - en caso de vulnerabilidades
- ⚠️ **Deprecado** - para características que serán eliminadas

---

*Para más información sobre nuevas versiones, visita el [repositorio oficial](https://github.com/ZabaHD4K/DescargadorYT)*

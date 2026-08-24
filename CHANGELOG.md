# 📝 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [1.7.3] - 2026-08-24

### 🔧 Changed
- **Auto-actualización más limpia**: los archivos temporales del proceso de update
  (`.bat`, exe descargado y backup `.bak`) se crean ahora en `%TEMP%` en vez de en la
  carpeta del exe, así que **ya no aparecen en el escritorio** del usuario.
- **Relanzado vía `explorer.exe`** en lugar de `start`: el exe nuevo cuelga de un padre
  válido (el Explorador), lo que evita avisos de antivirus/EDR del tipo
  "Security validation failure: failed to obtain executable path for parent process".

---

## [1.7.2] - 2026-08-24

### 🐛 Fixed
- **Menos "Failed to load Python DLL" al auto-actualizar**: el `.bat` de reemplazo espera
  ahora ~5s (antes ~2s) antes de relanzar el exe nuevo, dando tiempo a que el sistema de
  archivos y el antivirus liberen el binario recién movido antes de que el bootloader
  onefile extraiga sus DLLs. Si aun así apareciera el aviso, basta con reabrir la app.

---

## [1.7.1] - 2026-08-24

### 🐛 Fixed
- **Error "Failed to load Python DLL" durante la auto-actualización**: el updater ahora
  verifica que la descarga del nuevo exe coincide **exactamente** con el tamaño anunciado
  por el servidor (antes solo comprobaba que pesara >1 MB, y un exe truncado se instalaba
  y fallaba al arrancar). Además, el `.bat` de reemplazo espera un instante antes de
  relanzar, para que el sistema de archivos y el antivirus liberen el exe antes de que el
  bootloader extraiga sus DLLs.

### 📝 Docs
- README: el botón de descarga apunta al asset del último Release
  (`releases/latest/download/…`) en vez de a `raw/main`, y el badge de versión se actualiza.

---

## [1.7.0] - 2026-08-24

### 🐛 Fixed
- **Fallo de merge a MKV en 1080p/4K** (`Postprocessing: Conversion failed!`): yt-dlp
  empezó a exponer formatos HLS (m3u8) duplicados de los DASH, con bitrate estimado
  inflado que ganaba el desempate; su mp4 llega con timestamps sin definir y el
  contenedor MKV lo rechazaba. Ahora se descartan los formatos HLS y se usan los DASH.
- Fallback de descarga blindado con `[protocol^=http]` para no caer nunca en HLS.

### 🔒 Security
- **Verificación de certificados TLS activada**: se quitó `nocheckcertificate` de todas
  las llamadas a yt-dlp. Antes el tráfico iba cifrado pero sin verificar el certificado
  (riesgo de *man-in-the-middle* en WiFi pública).

### ✨ Added
- **Aviso claro cuando YouTube bloquea un vídeo** ("Sign in to confirm you're not a
  bot"): en vez de un error técnico, la app muestra un mensaje amable pidiendo esperar
  o probar otro vídeo, avisa de que está en desarrollo e invita a colaborar en GitHub.

### 🔧 Changed
- **Distribución vía GitHub Releases**: el .exe ya no se versiona en `main`; se publica
  como asset del Release. El auto-updater lee la última versión de la API de releases.
- **Comparación de versión semver** en el auto-updater (antes era igualdad de string):
  solo actualiza si la versión remota es realmente mayor.
- **Auto-update más seguro**: el .bat renombra el exe viejo a `.bak` y solo lo borra si
  el reemplazo va bien; si falla, restaura el backup (el usuario nunca se queda sin app).
- Dependencias actualizadas: yt-dlp 2026.8.19, pillow 12.3.0.

### 🧰 Internal
- Lógica de formatos extraída a `src/formatos.py` con tests de regresión
  (`tests/test_formatos.py`).
- CI: workflow que compila y publica el Release al pushear un tag `vX.Y.Z`.

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

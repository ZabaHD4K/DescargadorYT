# 📝 Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.3.3] - 2026-02-03

### ✨ Añadido
- **Barra de progreso en tiempo real**: Ahora puedes ver el progreso exacto de la descarga con porcentaje actualizado continuamente
- **Velocidad de descarga**: Indicador de velocidad en MB/s durante la descarga
- **Tiempo estimado restante**: Muestra el tiempo que falta para completar la descarga en formato inteligente (minutos y segundos)
- **Indicador de procesamiento**: Mensaje visual cuando se está procesando el archivo final después de la descarga
- **Hook de progreso mejorado**: Sistema de callbacks que actualiza la interfaz en tiempo real con información detallada

### 🔧 Mejorado
- La interfaz ahora muestra información detallada durante todo el proceso de descarga
- Mejor feedback visual para el usuario con mensajes informativos
- Optimización de la actualización de la barra de progreso para evitar parpadeos

### 🐛 Corregido
- Mejor manejo de casos donde no hay información de tiempo estimado disponible
- Corrección en el cálculo del porcentaje cuando solo hay estimación de bytes totales

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

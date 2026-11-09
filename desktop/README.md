# YTDownloader4K — desktop (nueva arquitectura)

Reescritura de la app con **backend Python local + frontend Electron**, manteniendo
la lógica de descarga probada de la app clásica (`src/`).

```
desktop/
├── backend/          # FastAPI en 127.0.0.1:8765
│   ├── server.py     # /api/load, /api/download, WS /ws (progreso en vivo)
│   └── requirements.txt
└── frontend/         # Electron, UI neomórfica (claro/oscuro)
    ├── main.js       # lanza/mata el backend automáticamente
    └── ...
```

El backend **reutiliza `src/formatos.py`** (lógica de formatos testeada) y replica
los puntos duros de `src/descargador.py`: ffmpeg auto-descargado a
`%LOCALAPPDATA%\YTDownloader4k\ffmpeg`, detección del muro anti-bot de YouTube,
format string con fallbacks `[protocol^=http]` y merge a MKV / extracción MP3.
Descarga a `~/Downloads`, como siempre.

## Ejecutar

```bash
# 1) dependencias (una vez)
pip install -r desktop/backend/requirements.txt
cd desktop/frontend && npm install

# 2) arrancar (Electron lanza el backend él solo y lo mata al cerrar)
cd desktop/frontend && npm start
```

Para desarrollo del backend a pelo: `python desktop/backend/server.py` y abrir
`http://127.0.0.1:8765/docs` (swagger de FastAPI). Si ya hay un backend en el
puerto, Electron lo reutiliza en vez de lanzar otro.

## Empaquetado y releases (CI/CD)

**Local**: `pyinstaller ytd4k-backend.spec` (desde `backend/`) y luego
`npm run dist` (desde `frontend/`) → instalador en `frontend/dist/`.

**CI**: pushear un tag `v2.x.y` dispara `.github/workflows/release-desktop.yml`,
que compila backend (PyInstaller) + frontend (electron-builder) y publica el
instalador como **prerelease** en GitHub. La app instalada se auto-actualiza
con electron-updater (`allowPrerelease`).

⚠️ Los tags `v1.*` siguen siendo de la app clásica (`release.yml`). Las releases
v2 se publican como *prerelease* a propósito: si fueran `latest`, los exes
clásicos (que comparan semver contra `releases/latest`) intentarían
"actualizarse" a la v2 y fallarían.

Detalles duros ya resueltos (no simplificar):
- El backend congelado redirige stdout/stderr a `%TEMP%\ytd4k-backend.log`
  (con `console=False` PyInstaller deja `sys.stdout=None` y uvicorn revienta).
- Anti-huérfanos doble: Electron mata el **árbol** del backend con
  `taskkill /T` (el onefile de PyInstaller son bootloader + hijo), y el backend
  lleva un watchdog `--parent-pid` que lo autocierra si Electron muere/crashea.

## Estado

- [x] Extracción real (chips = 2 mejores alturas + MP3)
- [x] Descarga real con progreso por WebSocket (MKV / MP3)
- [x] Modo claro/oscuro, ventana frameless
- [x] Empaquetado (PyInstaller backend + electron-builder, instalador NSIS)
- [x] Auto-update (electron-updater, canal prerelease)
- [x] CI: workflow `release-desktop.yml` con tags `v2.*`
- [ ] Selector avanzado de formatos (códec/fps/HDR)
- [ ] Firma de código (SmartScreen avisará al instalar, como con el exe clásico)

La app clásica de `src/` sigue siendo **la versión en producción** hasta que esto
madure.

# -*- mode: python ; coding: utf-8 -*-
# Backend de YTDownloader4K desktop -> exe onefile sin consola.
# Se compila DESDE desktop/backend:  pyinstaller ytd4k-backend.spec
# formatos.py (lógica compartida con la app clásica) se empaqueta como módulo
# vía pathex, así `import formatos` funciona igual congelado que desde fuente.

a = Analysis(
    ['server.py'],
    pathex=['../../src'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'formatos',
        # submódulos que uvicorn carga dinámicamente (PyInstaller no los ve)
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ytd4k-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['../frontend/icon.ico'],
)

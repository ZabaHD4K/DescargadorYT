// Proceso main: lanza el backend Python local, espera a que responda y abre
// la ventana. Al cerrar la app, mata el backend. Si ya hay un backend en el
// puerto (p. ej. lanzado a mano en desarrollo), lo reutiliza y no lo toca.
const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');

const PORT = 8765;
const BACKEND_PY = path.join(__dirname, '..', 'backend', 'server.py');
// empaquetado: el backend va como exe dentro de resources/ (ver extraResources)
const BACKEND_EXE = path.join(process.resourcesPath || '', 'backend', 'ytd4k-backend.exe');
let procesoBackend = null;

// auto-update (solo tiene efecto empaquetado; los Releases v2 van como
// prerelease para no pisar el canal de la app clásica)
let autoUpdater = null;
try {
  ({ autoUpdater } = require('electron-updater'));
  autoUpdater.allowPrerelease = true;
} catch {}

function ping() {
  return new Promise((resolve, reject) => {
    const req = http.get(`http://127.0.0.1:${PORT}/api/health`, (res) => {
      res.resume();
      res.statusCode === 200 ? resolve() : reject(new Error('status ' + res.statusCode));
    });
    req.on('error', reject);
    req.setTimeout(1500, () => req.destroy(new Error('timeout')));
  });
}

async function asegurarBackend() {
  try { await ping(); return 'reutilizado'; } catch {}
  // --parent-pid: el backend se autocierra si este proceso muere (anti-huérfanos)
  const args = ['--port', String(PORT), '--parent-pid', String(process.pid)];
  procesoBackend = app.isPackaged
    ? spawn(BACKEND_EXE, args, { stdio: 'ignore', windowsHide: true })
    : spawn('python', [BACKEND_PY, ...args], { stdio: 'ignore', windowsHide: true });
  // hasta ~20s de margen (la primera vez uvicorn tarda un poco en importar)
  for (let i = 0; i < 80; i++) {
    try { await ping(); return 'lanzado'; } catch {}
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error('El backend no respondió en el puerto ' + PORT);
}

function createWindow() {
  const win = new BrowserWindow({
    width: 500,
    height: 600,
    resizable: false,
    autoHideMenuBar: true,
    backgroundColor: '#e3edf7',
    title: 'YTDownloader4K',
    icon: path.join(__dirname, 'icon.ico'), // taskbar/ventana también en dev
    frame: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      backgroundThrottling: false, // el progreso sigue fluido al minimizar
    },
  });

  ipcMain.on('win:min', () => win.minimize());
  ipcMain.on('win:close', () => win.close());

  const shotMode = !!process.env.PROTO_SHOT;
  win.loadFile('index.html', { query: shotMode ? { demo: '1' } : {} });

  if (shotMode) {
    const dir = process.env.PROTO_SHOT_DIR || __dirname;
    const snap = (nombre, ms) =>
      setTimeout(async () => {
        try {
          const img = await win.webContents.capturePage();
          fs.writeFileSync(path.join(dir, nombre), img.toPNG());
          console.log('guardada', nombre);
        } catch (e) {
          console.error('error capturando', nombre, e.message);
        }
      }, ms);
    snap('app_1_inicio.png', 1500);
    snap('app_2_cargado.png', 9000); // la carga real tarda unos segundos
    setTimeout(() => app.quit(), 10000);
  }
}

// Identidad de la app en Windows: agrupa bien en la barra de tareas y hace
// que notificaciones/jump-list usen nuestro icono (mismo id que appId del build)
app.setAppUserModelId('com.zabalex.ytdownloader4k');

app.whenReady().then(async () => {
  try {
    await asegurarBackend();
  } catch (e) {
    console.error(e.message);
  }
  createWindow();
  if (app.isPackaged && autoUpdater) {
    autoUpdater.checkForUpdatesAndNotify().catch(() => {});
  }
});

app.on('window-all-closed', () => app.quit());
app.on('will-quit', () => {
  if (procesoBackend && !procesoBackend.killed) {
    // taskkill /T: el onefile de PyInstaller son DOS procesos (bootloader +
    // hijo); matar solo al padre dejaba el backend real huérfano.
    try {
      require('child_process').spawnSync('taskkill',
        ['/pid', String(procesoBackend.pid), '/T', '/F'], { windowsHide: true });
    } catch {
      procesoBackend.kill();
    }
  }
});

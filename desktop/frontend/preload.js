// Puente seguro renderer -> main para los botones de la barra de título custom.
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('wctl', {
  minimizar: () => ipcRenderer.send('win:min'),
  cerrar: () => ipcRenderer.send('win:close'),
});

// updater interactivo: eventos del main y acciones del usuario
contextBridge.exposeInMainWorld('updater', {
  onEvento: (cb) => ipcRenderer.on('update:evento', (_e, datos) => cb(datos)),
  descargar: () => ipcRenderer.send('update:descargar'),
  instalar: () => ipcRenderer.send('update:instalar'),
});

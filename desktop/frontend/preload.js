// Puente seguro renderer -> main para los botones de la barra de título custom.
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('wctl', {
  minimizar: () => ipcRenderer.send('win:min'),
  cerrar: () => ipcRenderer.send('win:close'),
});

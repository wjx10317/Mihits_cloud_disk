import { contextBridge, ipcRenderer } from 'electron'

// 暴露安全 API 到渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 文件系统操作
  selectFolder: () => ipcRenderer.invoke('dialog:selectFolder'),
  selectFile: () => ipcRenderer.invoke('dialog:selectFile'),

  // 系统信息
  getAppVersion: () => ipcRenderer.invoke('app:getVersion'),
  getPlatform: () => ipcRenderer.invoke('app:getPlatform'),

  // 窗口控制
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),

  // 系统托盘
  setTrayVisible: (visible: boolean) => ipcRenderer.send('tray:setVisible', visible),
})

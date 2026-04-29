import { contextBridge } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

const api = {
  // 预留：后续添加 IPC 通信接口
}

if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  // @ts-ignore
  window.electron = electronAPI
  // @ts-ignore
  window.api = api
}

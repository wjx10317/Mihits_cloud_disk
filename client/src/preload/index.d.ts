export interface ElectronAPI {
  selectFolder: () => Promise<string | null>
  selectFile: () => Promise<string | null>
  getAppVersion: () => Promise<string>
  getPlatform: () => Promise<string>
  minimize: () => void
  maximize: () => void
  close: () => void
  setTrayVisible: (visible: boolean) => void
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}

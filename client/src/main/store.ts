import Store from 'electron-store'

interface StoreSchema {
  accessToken: string | null
  refreshToken: string | null
  userId: string | null
  username: string | null
  windowBounds: { x: number; y: number; width: number; height: number } | null
  sidebarCollapsed: boolean
  theme: 'light' | 'dark'
}

const store = new Store<StoreSchema>({
  defaults: {
    accessToken: null,
    refreshToken: null,
    userId: null,
    username: null,
    windowBounds: null,
    sidebarCollapsed: false,
    theme: 'light',
  },
  encryptionKey: 'mihits-cloud-disk-2024',
})

export default store

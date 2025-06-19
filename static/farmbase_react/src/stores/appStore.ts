import { create } from 'zustand'

interface RefreshState {
  show: boolean
  message: string
}

interface AppState {
  toggleDrawer: boolean
  drawerHovered: boolean
  refresh: RefreshState
  loading: boolean
  currentVersion: string | undefined
  
  // Actions
  setDrawerOpen: (value: boolean) => void
  setDrawerHovered: (value: boolean) => void
  performRefresh: () => void
  setLoading: (value: boolean) => void
  setRefresh: (value: RefreshState) => void
  resetRefresh: () => void
  showCommitMessage: () => void
}

const getDefaultRefreshState = (): RefreshState => ({
  show: false,
  message: '',
})

const latestCommitHash = import.meta.env.VITE_DISPATCH_COMMIT_HASH
const latestCommitMessage = import.meta.env.VITE_DISPATCH_COMMIT_MESSAGE

export const useAppStore = create<AppState>((set) => ({
  toggleDrawer: true,
  drawerHovered: false,
  refresh: getDefaultRefreshState(),
  loading: false,
  currentVersion: latestCommitHash,

  setDrawerOpen: (value: boolean) => set({ toggleDrawer: value }),
  setDrawerHovered: (value: boolean) => set({ drawerHovered: value }),
  
  performRefresh: () => {
    window.location.reload()
    set({ refresh: getDefaultRefreshState() })
  },
  
  setLoading: (value: boolean) => set({ loading: value }),
  
  setRefresh: (value: RefreshState) => set({ 
    refresh: { ...value, show: true } 
  }),
  
  resetRefresh: () => set({ refresh: getDefaultRefreshState() }),
  
  showCommitMessage: () => {
    // This will be connected to notification store
    console.log(`Hash: ${latestCommitHash} | Message: ${latestCommitMessage}`)
  },
}))
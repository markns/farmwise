import React, { createContext, useContext } from 'react'
import { create } from 'zustand'
import { startTransition } from 'react'
import { createFarmApi, type Farm, type FarmListOptions, type Note } from '@/api/farm'
import { type ApiClient } from '@/api/client'
import { useNotificationStore } from './notificationStore'
import { debounce } from '@/utils'

export interface Contact {
  id: string
  name: string
  role: string
}

export interface FarmWithContacts extends Farm {
  farm_name: string
  contacts?: Contact[]
}

interface TableOptions {
  q: string
  page: number
  itemsPerPage: number
  sortBy: string[]
  descending: boolean[]
  filters: Record<string, any>
}

interface TableRows {
  items: FarmWithContacts[]
  total: number | null
}

interface NotesState {
  items: Note[]
  total: number | null
  loading: boolean
}

interface FarmState {
  selected: FarmWithContacts | null
  dialogs: {
    showCreateEdit: boolean
    showRemove: boolean
    showNotes: boolean
  }
  table: {
    rows: TableRows
    options: TableOptions
    loading: boolean
  }
  notes: NotesState

  // Actions
  getAll: () => void
  getFarm: (farmId: string) => Promise<void>
  getNotes: () => void
  createEditShow: (farm?: FarmWithContacts) => void
  showNotes: (farm: FarmWithContacts) => void
  removeShow: (farm: FarmWithContacts) => void
  closeCreateEdit: () => void
  closeRemove: () => void
  closeNotes: () => void
  save: () => Promise<void>
  remove: () => Promise<void>
  setSelected: (farm: FarmWithContacts | null) => void
  updateTableOptions: (options: Partial<TableOptions>) => void
}

const getDefaultSelectedState = (): FarmWithContacts => ({
  id: '',
  name: '',
  farm_name: '',
  description: '',
  location: undefined,
  area: undefined,
  owner: '',
  contacts: [],
  created_at: '',
  updated_at: '',
})

// Factory function to create farm store with authenticated API client
export const createFarmStore = (apiClient: ApiClient) => {
  const farmApi = createFarmApi(apiClient)
  
  return create<FarmState>((set, get) => ({
  selected: null,
  dialogs: {
    showCreateEdit: false,
    showRemove: false,
    showNotes: false,
  },
  table: {
    rows: {
      items: [],
      total: null,
    },
    options: {
      q: '',
      page: 1,
      itemsPerPage: 25,
      sortBy: ['farm_name'],
      descending: [false],
      filters: {},
    },
    loading: false,
  },
  notes: {
    items: [],
    total: null,
    loading: false,
  },

  // Debounced getAll function
  getAll: debounce(async () => {
    const state = get()
    
    startTransition(() => {
      set(prevState => ({
        table: { ...prevState.table, loading: true }
      }))
    })

    try {
      const options: FarmListOptions = {
        q: state.table.options.q || undefined,
        page: state.table.options.page,
        itemsPerPage: state.table.options.itemsPerPage,
        sortBy: state.table.options.sortBy,
        descending: state.table.options.descending,
      }

      const response = await farmApi.getAll(options)
      
      startTransition(() => {
        set(prevState => ({
          table: {
            ...prevState.table,
            loading: false,
            rows: {
              items: response.items.map(farm => ({
                ...farm,
                farm_name: farm.name,
                contacts: [] // This would be populated from the actual API response
              })),
              total: response.total
            }
          }
        }))
      })
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Failed to load farms',
        type: 'error',
      })
      startTransition(() => {
        set(prevState => ({
          table: { ...prevState.table, loading: false }
        }))
      })
    }
  }, 500),

  getFarm: async (farmId: string) => {
    try {
      const farm = await farmApi.getFarm(farmId)
      set({
        selected: {
          ...farm,
          farm_name: farm.name,
          contacts: [] // This would be populated from the actual API response
        }
      })
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Failed to load farm details',
        type: 'error',
      })
    }
  },

  getNotes: debounce(async () => {
    const state = get()
    if (!state.selected?.id) return

    set(prevState => ({
      notes: { ...prevState.notes, loading: true }
    }))

    try {
      const response = await farmApi.getNotes(state.selected.id)
      set(prevState => ({
        notes: {
          ...prevState.notes,
          loading: false,
          items: response.items,
          total: response.total
        }
      }))
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Failed to load farm notes',
        type: 'error',
      })
      set(prevState => ({
        notes: { ...prevState.notes, loading: false }
      }))
    }
  }, 500),

  createEditShow: (farm?: FarmWithContacts) => {
    set({
      selected: farm || getDefaultSelectedState(),
      dialogs: { ...get().dialogs, showCreateEdit: true }
    })
  },

  showNotes: (farm: FarmWithContacts) => {
    set({
      selected: farm,
      dialogs: { ...get().dialogs, showNotes: true }
    })
    get().getNotes()
  },

  removeShow: (farm: FarmWithContacts) => {
    set({
      selected: farm,
      dialogs: { ...get().dialogs, showRemove: true }
    })
  },

  closeCreateEdit: () => {
    set({
      dialogs: { ...get().dialogs, showCreateEdit: false },
      selected: null
    })
  },

  closeRemove: () => {
    set({
      dialogs: { ...get().dialogs, showRemove: false },
      selected: null
    })
  },

  closeNotes: () => {
    set({
      dialogs: { ...get().dialogs, showNotes: false },
      selected: null
    })
  },

  save: async () => {
    const state = get()
    const { addNotification } = useNotificationStore.getState()
    
    if (!state.selected) return

    try {
      if (!state.selected.id) {
        // Create new farm
        const farmData = {
          name: state.selected.farm_name,
          description: state.selected.description,
          location: state.selected.location,
          area: state.selected.area,
          owner: state.selected.owner,
        }
        
        await farmApi.createFarm(farmData)
        addNotification({
          text: 'Farm created successfully.',
          type: 'success',
        })
      } else {
        // Update existing farm
        const farmData = {
          name: state.selected.farm_name,
          description: state.selected.description,
          location: state.selected.location,
          area: state.selected.area,
          owner: state.selected.owner,
        }
        
        await farmApi.updateFarm(state.selected.id, farmData)
        addNotification({
          text: 'Farm updated successfully.',
          type: 'success',
        })
      }

      get().closeCreateEdit()
      get().getAll()
    } catch (error) {
      addNotification({
        text: 'Failed to save farm.',
        type: 'error',
      })
    }
  },

  remove: async () => {
    const state = get()
    const { addNotification } = useNotificationStore.getState()
    
    if (!state.selected?.id) return

    try {
      await farmApi.deleteFarm(state.selected.id)
      addNotification({
        text: 'Farm deleted successfully.',
        type: 'success',
      })
      get().closeRemove()
      get().getAll()
    } catch (error) {
      addNotification({
        text: 'Failed to delete farm.',
        type: 'error',
      })
    }
  },

  setSelected: (farm: FarmWithContacts | null) => {
    set({ selected: farm })
  },

  updateTableOptions: (options: Partial<TableOptions>) => {
    startTransition(() => {
      set(prevState => ({
        table: {
          ...prevState.table,
          options: { ...prevState.table.options, ...options }
        }
      }))
      
      // Reset to page 1 when changing filters/search
      if ('q' in options || 'filters' in options) {
        set(prevState => ({
          table: {
            ...prevState.table,
            options: { ...prevState.table.options, page: 1 }
          }
        }))
      }
    })
    
    // Trigger new data fetch
    get().getAll()
  },
  }))
}

// Create context for sharing the store instance
type FarmStoreType = ReturnType<typeof createFarmStore>
const FarmStoreContext = createContext<FarmStoreType | null>(null)

// Provider component that creates and shares a single store instance
interface FarmStoreProviderProps {
  apiClient: ApiClient
  children: React.ReactNode
}

export const FarmStoreProvider: React.FC<FarmStoreProviderProps> = ({ apiClient, children }) => {
  const storeRef = React.useRef<FarmStoreType>()
  
  if (!storeRef.current) {
    storeRef.current = createFarmStore(apiClient)
  }
  
  return React.createElement(
    FarmStoreContext.Provider,
    { value: storeRef.current },
    children
  )
}

// Hook to use the shared farm store
export const useFarmStore = () => {
  const store = useContext(FarmStoreContext)
  if (!store) {
    throw new Error('useFarmStore must be used within a FarmStoreProvider')
  }
  return store()
}

// Example usage:
// 1. Wrap your app section with the provider:
// const AppWithFarmStore = ({ apiClient }) => (
//   <FarmStoreProvider apiClient={apiClient}>
//     <Farms />
//     <NotesDrawer />
//     <FarmCreateEditDialog />
//   </FarmStoreProvider>
// )
//
// 2. Use the hook in components:
// const Farms = () => {
//   const { table, getAll, updateTableOptions } = useFarmStore()
//   // ... component logic
// }

export default createFarmStore
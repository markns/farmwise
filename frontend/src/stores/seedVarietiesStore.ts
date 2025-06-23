import React, { createContext, useContext } from 'react'
import { create } from 'zustand'
import { startTransition } from 'react'
import { CropVarietiesApi, type CropVariety, type CropVarietiesResponse } from '@/api/cropVarieties'
import { type ApiClient } from '@/api/client'
import { useNotificationStore } from './notificationStore'

interface TableOptions {
  q: string
  page: number
  itemsPerPage: number
  sortBy: string[]
  descending: boolean[]
}

interface TableRows {
  items: CropVariety[]
  total: number | null
}

interface SeedVarietiesState {
  cropVarietiesData: CropVarietiesResponse | null
  instanceTable: {
    rows: TableRows
    options: TableOptions
    loading: boolean
  }
}

interface SeedVarietiesActions {
  loadCropVarieties: () => Promise<void>
  getAllInstances: () => Promise<void>
  updateInstanceTableOptions: (newOptions: Partial<TableOptions>) => void
}

type SeedVarietiesStore = SeedVarietiesState & SeedVarietiesActions

const defaultTableOptions: TableOptions = {
  q: '',
  page: 1,
  itemsPerPage: 25,
  sortBy: ['variety'],
  descending: [false],
}

const createSeedVarietiesStore = (apiClient: ApiClient) => {
  const cropVarietiesApi = new CropVarietiesApi(apiClient)

  return create<SeedVarietiesStore>((set, get) => ({
    cropVarietiesData: null,
    instanceTable: {
      rows: { items: [], total: null },
      options: defaultTableOptions,
      loading: false,
    },

    loadCropVarieties: async () => {
      set(state => ({
        instanceTable: { ...state.instanceTable, loading: true },
      }))
      
      try {
        const response = await cropVarietiesApi.getMaizeVarieties()
        set({ cropVarietiesData: response })
        
        // Update table data immediately after loading
        get().getAllInstances()
      } catch (error) {
        const { addNotification } = useNotificationStore.getState()
        addNotification({
          text: 'Failed to load crop varieties',
          type: 'error',
        })
        console.error('Failed to load crop varieties:', error)
        set(state => ({
          instanceTable: { ...state.instanceTable, loading: false },
        }))
      }
    },

    getAllInstances: async () => {
      const { cropVarietiesData, instanceTable } = get()
      const { options } = instanceTable

      if (!cropVarietiesData) {
        return
      }

      set(state => ({
        instanceTable: { ...state.instanceTable, loading: true },
      }))

      try {
        let filteredVarieties = cropVarietiesData.varieties

        // Apply search filter
        if (options.q) {
          const searchTerm = options.q.toLowerCase()
          filteredVarieties = filteredVarieties.filter(variety =>
            variety.variety.toLowerCase().includes(searchTerm) ||
            variety.producer.toLowerCase().includes(searchTerm) ||
            variety.description.toLowerCase().includes(searchTerm) ||
            variety.maturity_category.toLowerCase().includes(searchTerm)
          )
        }

        // Apply sorting
        if (options.sortBy.length > 0) {
          const sortField = options.sortBy[0]
          const isDescending = options.descending[0]
          
          filteredVarieties.sort((a, b) => {
            let aValue = a[sortField as keyof CropVariety]
            let bValue = b[sortField as keyof CropVariety]
            
            if (typeof aValue === 'string') {
              aValue = aValue.toLowerCase()
            }
            if (typeof bValue === 'string') {
              bValue = bValue.toLowerCase()
            }
            
            if (aValue < bValue) return isDescending ? 1 : -1
            if (aValue > bValue) return isDescending ? -1 : 1
            return 0
          })
        }

        // Apply pagination
        const startIndex = (options.page - 1) * options.itemsPerPage
        const endIndex = startIndex + options.itemsPerPage
        const paginatedVarieties = filteredVarieties.slice(startIndex, endIndex)

        set(state => ({
          instanceTable: {
            ...state.instanceTable,
            rows: {
              items: paginatedVarieties,
              total: filteredVarieties.length,
            },
            loading: false,
          },
        }))
      } catch (error) {
        const { addNotification } = useNotificationStore.getState()
        addNotification({
          text: 'Failed to process crop varieties data',
          type: 'error',
        })
        console.error('Failed to process crop varieties data:', error)
        set(state => ({
          instanceTable: { ...state.instanceTable, loading: false },
        }))
      }
    },

    updateInstanceTableOptions: (newOptions: Partial<TableOptions>) => {
      set(state => ({
        instanceTable: {
          ...state.instanceTable,
          options: { ...state.instanceTable.options, ...newOptions },
        },
      }))

      // Trigger data reload for most option changes
      const triggerReload = ['page', 'itemsPerPage', 'sortBy', 'descending', 'q']
      if (Object.keys(newOptions).some(key => triggerReload.includes(key))) {
        startTransition(() => {
          get().getAllInstances()
        })
      }
    },
  }))
}

// Context for the store
const SeedVarietiesStoreContext = createContext<ReturnType<typeof createSeedVarietiesStore> | null>(null)

// Provider component
interface SeedVarietiesStoreProviderProps {
  children: React.ReactNode
  apiClient: ApiClient
}

export const SeedVarietiesStoreProvider: React.FC<SeedVarietiesStoreProviderProps> = ({ children, apiClient }) => {
  const storeRef = React.useRef<ReturnType<typeof createSeedVarietiesStore>>()
  
  if (!storeRef.current) {
    storeRef.current = createSeedVarietiesStore(apiClient)
  }

  return React.createElement(
    SeedVarietiesStoreContext.Provider,
    { value: storeRef.current },
    children
  )
}

// Hook to use the store
export const useSeedVarietiesStore = () => {
  const store = useContext(SeedVarietiesStoreContext)
  if (!store) {
    throw new Error('useSeedVarietiesStore must be used within SeedVarietiesStoreProvider')
  }
  return store
}

// Export types
export type { CropVariety, CropVarietiesResponse, SeedVarietiesStore, TableOptions }
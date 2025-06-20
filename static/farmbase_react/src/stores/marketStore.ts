import React, { createContext, useContext } from 'react'
import { create } from 'zustand'
import { startTransition } from 'react'
import { MarketApi, type Market, type Commodity, type MarketPrice, type MarketPriceParams } from '@/api/market'
import { type ApiClient } from '@/api/client'
import { useNotificationStore } from './notificationStore'

interface TableOptions {
  q: string
  page: number
  itemsPerPage: number
  sortBy: string[]
  descending: boolean[]
  queryType: 'market' | 'commodity'
  selectedMarketId: number | null
  selectedCommodityId: number | null
}

interface TableRows {
  items: MarketPrice[]
  total: number | null
}

interface MarketState {
  markets: Market[]
  commodities: Commodity[]
  instanceTable: {
    rows: TableRows
    options: TableOptions
    loading: boolean
  }
  loading: {
    markets: boolean
    commodities: boolean
  }
}

interface MarketActions {
  loadMarkets: () => Promise<void>
  loadCommodities: () => Promise<void>
  getAllInstances: () => Promise<void>
  updateInstanceTableOptions: (newOptions: Partial<TableOptions>) => void
}

type MarketStore = MarketState & MarketActions

const defaultTableOptions: TableOptions = {
  q: '',
  page: 1,
  itemsPerPage: 25,
  sortBy: ['price_date'],
  descending: [true],
  queryType: 'commodity',
  selectedMarketId: null,
  selectedCommodityId: null,
}

const createMarketStore = (apiClient: ApiClient) => {
  const marketApi = new MarketApi(apiClient)

  return create<MarketStore>((set, get) => ({
    markets: [],
    commodities: [],
    instanceTable: {
      rows: { items: [], total: null },
      options: defaultTableOptions,
      loading: false,
    },
    loading: {
      markets: false,
      commodities: false,
    },

    loadMarkets: async () => {
      set(state => ({ loading: { ...state.loading, markets: true } }))
      try {
        const response = await marketApi.getMarkets()
        const sortedMarkets = response.items.sort((a, b) => a.name.localeCompare(b.name))
        set({ markets: sortedMarkets })
      } catch (error) {
        const { addNotification } = useNotificationStore.getState()
        addNotification({
          text: 'Failed to load markets',
          type: 'error',
        })
        console.error('Failed to load markets:', error)
      } finally {
        set(state => ({ loading: { ...state.loading, markets: false } }))
      }
    },

    loadCommodities: async () => {
      set(state => ({ loading: { ...state.loading, commodities: true } }))
      try {
        const commodities = await marketApi.getAllCommodities()
        const sortedCommodities = commodities.sort((a, b) => a.name.localeCompare(b.name))
        set({ commodities: sortedCommodities })
      } catch (error) {
        const { addNotification } = useNotificationStore.getState()
        addNotification({
          text: 'Failed to load commodities',
          type: 'error',
        })
        console.error('Failed to load commodities:', error)
      } finally {
        set(state => ({ loading: { ...state.loading, commodities: false } }))
      }
    },

    getAllInstances: async () => {
      const { instanceTable } = get()
      const { options } = instanceTable

      // Don't fetch if no selection is made
      if (!options.selectedMarketId && !options.selectedCommodityId) {
        return
      }

      set(state => ({
        instanceTable: { ...state.instanceTable, loading: true },
      }))

      try {
        const params: MarketPriceParams = {
          page: options.page,
          items_per_page: options.itemsPerPage,
        }

        if (options.queryType === 'market' && options.selectedMarketId) {
          params.market_id = options.selectedMarketId
        } else if (options.queryType === 'commodity' && options.selectedCommodityId) {
          params.commodity_id = options.selectedCommodityId
        }

        const response = await marketApi.getMarketPrices(params)
        
        set(state => ({
          instanceTable: {
            ...state.instanceTable,
            rows: {
              items: response.items,
              total: response.total,
            },
            loading: false,
          },
        }))
      } catch (error) {
        const { addNotification } = useNotificationStore.getState()
        addNotification({
          text: 'Failed to load market prices',
          type: 'error',
        })
        console.error('Failed to load market prices:', error)
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

      // Trigger data reload if certain options changed
      const triggerReload = ['page', 'itemsPerPage', 'selectedMarketId', 'selectedCommodityId', 'queryType']
      if (Object.keys(newOptions).some(key => triggerReload.includes(key))) {
        startTransition(() => {
          get().getAllInstances()
        })
      }
    },
  }))
}

// Context for the store
const MarketStoreContext = createContext<ReturnType<typeof createMarketStore> | null>(null)

// Provider component
interface MarketStoreProviderProps {
  children: React.ReactNode
  apiClient: ApiClient
}

export const MarketStoreProvider: React.FC<MarketStoreProviderProps> = ({ children, apiClient }) => {
  const storeRef = React.useRef<ReturnType<typeof createMarketStore>>()
  
  if (!storeRef.current) {
    storeRef.current = createMarketStore(apiClient)
  }

  return React.createElement(
    MarketStoreContext.Provider,
    { value: storeRef.current },
    children
  )
}

// Hook to use the store
export const useMarketStore = () => {
  const store = useContext(MarketStoreContext)
  if (!store) {
    throw new Error('useMarketStore must be used within MarketStoreProvider')
  }
  return store
}

// Export types
export type { Market, Commodity, MarketPrice, MarketStore, TableOptions }
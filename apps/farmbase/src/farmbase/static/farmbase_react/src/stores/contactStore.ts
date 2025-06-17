import React, { createContext, useContext } from 'react'
import { create } from 'zustand'
import { startTransition } from 'react'
import { 
  createContactApi, 
  type Contact, 
  type ContactListOptions, 
  type ContactListResponse,
  type ContactEngagement,
  type ContactFilter,
  type ChatState,
  type ContactInstance
} from '@/api/contact'
import { type ApiClient } from '@/api/client'
import { useNotificationStore } from './notificationStore'
import { debounce } from '@/utils'

interface TableOptions {
  q: string
  page: number
  itemsPerPage: number
  sortBy: string[]
  descending: boolean[]
  filters: Record<string, any>
}

interface TableRows {
  items: Contact[]
  total: number | null
}

interface InstanceTableRows {
  items: Contact[]
  total: number | null
}

interface ContactState {
  selected: Contact | null
  dialogs: {
    showCreateEdit: boolean
    showRemove: boolean
    showHistory: boolean
    showChat: boolean
    showFilter: boolean
  }
  table: {
    rows: TableRows
    options: TableOptions
    loading: boolean
  }
  instanceTable: {
    rows: InstanceTableRows
    options: TableOptions
    loading: boolean
  }
  engagements: ContactEngagement[]
  filters: ContactFilter[]
  chatState: ChatState | null
  availableFilters: Record<string, string[]>
  
  // Actions
  getAll: () => void
  getAllInstances: () => void
  getContact: (id: string) => Promise<void>
  save: () => Promise<void>
  remove: () => Promise<void>
  
  // Dialog actions
  createEditShow: (contact?: Contact) => void
  closeCreateEdit: () => void
  removeShow: (contact: Contact) => void
  closeRemove: () => void
  historyShow: (contact: Contact) => void
  closeHistory: () => void
  chatShow: (contact: Contact) => void
  closeChat: () => void
  filterShow: () => void
  closeFilter: () => void
  
  // Table actions
  updateTableOptions: (options: Partial<TableOptions>) => void
  updateInstanceTableOptions: (options: Partial<TableOptions>) => void
  setSelected: (contact: Contact | null) => void
  
  // Engagement actions
  loadEngagements: (contactId: string) => Promise<void>
  
  // Filter actions
  loadFilters: () => Promise<void>
  loadFilterOptions: () => Promise<void>
  applyFilters: (filters: Record<string, any>) => void
  
  // Chat actions
  loadChatState: (contactId: string) => Promise<void>
}

// Factory function to create contact store with authenticated API client
export const createContactStore = (apiClient: ApiClient) => {
  const contactApi = createContactApi(apiClient)
  
  return create<ContactState>((set, get) => ({
  selected: null,
  dialogs: {
    showCreateEdit: false,
    showRemove: false,
    showHistory: false,
    showChat: false,
    showFilter: false,
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
      sortBy: ['name'],
      descending: [false],
      filters: {},
    },
    loading: false,
  },
  instanceTable: {
    rows: {
      items: [],
      total: null,
    },
    options: {
      q: '',
      page: 1,
      itemsPerPage: 25,
      sortBy: ['created_at'],
      descending: [true],
      filters: {},
    },
    loading: false,
  },
  engagements: [],
  filters: [],
  chatState: null,
  availableFilters: {},

  // Debounced getAll function
  getAll: debounce(async () => {
    const state = get()
    
    startTransition(() => {
      set(prevState => ({
        table: { ...prevState.table, loading: true }
      }))
    })

    try {
      const options: ContactListOptions = {
        q: state.table.options.q || undefined,
        page: state.table.options.page,
        itemsPerPage: state.table.options.itemsPerPage,
        sortBy: state.table.options.sortBy,
        descending: state.table.options.descending,
        filters: Object.keys(state.table.options.filters).length > 0 
          ? state.table.options.filters 
          : undefined,
      }

      const response: ContactListResponse = await contactApi.getAll(options)
      
      startTransition(() => {
        set(prevState => ({
          table: {
            ...prevState.table,
            loading: false,
            rows: {
              items: response.items,
              total: response.total
            }
          }
        }))
      })
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Failed to load contacts',
        type: 'error',
      })
      startTransition(() => {
        set(prevState => ({
          table: { ...prevState.table, loading: false }
        }))
      })
    }
  }, 500),

  // Debounced getAllInstances function
  getAllInstances: debounce(async () => {
    const state = get()
    
    startTransition(() => {
      set(prevState => ({
        instanceTable: { ...prevState.instanceTable, loading: true }
      }))
    })

    try {
      const options: ContactListOptions = {
        q: state.instanceTable.options.q || undefined,
        page: state.instanceTable.options.page,
        itemsPerPage: state.instanceTable.options.itemsPerPage,
        sortBy: state.instanceTable.options.sortBy,
        descending: state.instanceTable.options.descending,
      }

      const response: ContactListResponse = await contactApi.getAllInstances(options)
      
      startTransition(() => {
        set(prevState => ({
          instanceTable: {
            ...prevState.instanceTable,
            loading: false,
            rows: {
              items: response.items,
              total: response.total
            }
          }
        }))
      })
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Failed to load contact instances',
        type: 'error',
      })
      startTransition(() => {
        set(prevState => ({
          instanceTable: { ...prevState.instanceTable, loading: false }
        }))
      })
    }
  }, 500),

  getContact: async (id: string) => {
    try {
      const contact = await contactApi.getContact(id)
      set({ selected: contact })
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Failed to load contact',
        type: 'error',
      })
    }
  },

  save: async () => {
    const state = get()
    const { addNotification } = useNotificationStore.getState()
    
    if (!state.selected) return

    try {
      if (state.selected.id) {
        // Update existing contact
        const contactData = {
          name: state.selected.name,
          external_id: state.selected.external_id,
          external_url: state.selected.external_url,
          phone_number: state.selected.phone_number,
          email: state.selected.email,
          preferred_form_of_address: state.selected.preferred_form_of_address,
          gender: state.selected.gender,
          date_of_birth: state.selected.date_of_birth,
          estimated_age: state.selected.estimated_age,
          role: state.selected.role,
          experience: state.selected.experience,
          organization: state.selected.organization,
          product_interests: state.selected.product_interests,
        }
        
        await contactApi.updateContact(state.selected.id, contactData)
        addNotification({
          text: 'Contact updated successfully.',
          type: 'success',
        })
      } else {
        // Create new contact
        const contactData = {
          name: state.selected.name,
          external_id: state.selected.external_id,
          external_url: state.selected.external_url,
          phone_number: state.selected.phone_number,
          email: state.selected.email,
          preferred_form_of_address: state.selected.preferred_form_of_address,
          gender: state.selected.gender,
          date_of_birth: state.selected.date_of_birth,
          estimated_age: state.selected.estimated_age,
          role: state.selected.role,
          experience: state.selected.experience,
          organization: state.selected.organization,
          product_interests: state.selected.product_interests,
        }
        
        await contactApi.createContact(contactData)
        addNotification({
          text: 'Contact created successfully.',
          type: 'success',
        })
      }

      get().closeCreateEdit()
      get().getAll()
    } catch (error) {
      addNotification({
        text: 'Failed to save contact.',
        type: 'error',
      })
    }
  },

  remove: async () => {
    const state = get()
    const { addNotification } = useNotificationStore.getState()
    
    if (!state.selected?.id) return

    try {
      await contactApi.deleteContact(state.selected.id)
      addNotification({
        text: 'Contact deleted successfully.',
        type: 'success',
      })
      get().closeRemove()
      get().getAll()
    } catch (error) {
      addNotification({
        text: 'Failed to delete contact.',
        type: 'error',
      })
    }
  },

  // Dialog actions
  createEditShow: (contact?: Contact) => {
    set({ 
      selected: contact || {
        id: '',
        external_id: '',
        name: '',
        created_at: '',
        updated_at: '',
      } as Contact,
      dialogs: { ...get().dialogs, showCreateEdit: true }
    })
  },

  closeCreateEdit: () => {
    set({ 
      selected: null,
      dialogs: { ...get().dialogs, showCreateEdit: false }
    })
  },

  removeShow: (contact: Contact) => {
    set({ 
      selected: contact,
      dialogs: { ...get().dialogs, showRemove: true }
    })
  },

  closeRemove: () => {
    set({ 
      selected: null,
      dialogs: { ...get().dialogs, showRemove: false }
    })
  },

  historyShow: (contact: Contact) => {
    set({ 
      selected: contact,
      dialogs: { ...get().dialogs, showHistory: true }
    })
  },

  closeHistory: () => {
    set({ 
      selected: null,
      dialogs: { ...get().dialogs, showHistory: false }
    })
  },

  chatShow: (contact: Contact) => {
    set({ 
      selected: contact,
      dialogs: { ...get().dialogs, showChat: true }
    })
    get().loadChatState(contact.id)
  },

  closeChat: () => {
    set({ 
      selected: null,
      chatState: null,
      dialogs: { ...get().dialogs, showChat: false }
    })
  },

  filterShow: () => {
    set({ 
      dialogs: { ...get().dialogs, showFilter: true }
    })
  },

  closeFilter: () => {
    set({ 
      dialogs: { ...get().dialogs, showFilter: false }
    })
  },

  setSelected: (contact: Contact | null) => {
    set({ selected: contact })
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

  updateInstanceTableOptions: (options: Partial<TableOptions>) => {
    startTransition(() => {
      set(prevState => ({
        instanceTable: {
          ...prevState.instanceTable,
          options: { ...prevState.instanceTable.options, ...options }
        }
      }))
      
      // Reset to page 1 when changing filters/search
      if ('q' in options || 'filters' in options) {
        set(prevState => ({
          instanceTable: {
            ...prevState.instanceTable,
            options: { ...prevState.instanceTable.options, page: 1 }
          }
        }))
      }
    })
    
    // Trigger new data fetch
    get().getAllInstances()
  },

  loadEngagements: async (contactId: string) => {
    try {
      const engagements = await contactApi.getEngagements(contactId)
      set({ engagements })
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Failed to load contact engagements',
        type: 'error',
      })
    }
  },

  loadFilters: async () => {
    try {
      const filters = await contactApi.getFilters()
      set({ filters })
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Failed to load contact filters',
        type: 'error',
      })
    }
  },

  loadFilterOptions: async () => {
    try {
      const availableFilters = await contactApi.getFilterOptions()
      set({ availableFilters })
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Failed to load filter options',
        type: 'error',
      })
    }
  },

  applyFilters: (filters: Record<string, any>) => {
    get().updateTableOptions({ filters })
  },

  loadChatState: async (contactId: string) => {
    try {
      const chatState = await contactApi.getChatState(contactId)
      set({ chatState })
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Failed to load chat history',
        type: 'error',
      })
    }
  },
  }))
}

// Create context for sharing the store instance
type ContactStoreType = ReturnType<typeof createContactStore>
const ContactStoreContext = createContext<ContactStoreType | null>(null)

// Provider component that creates and shares a single store instance
interface ContactStoreProviderProps {
  apiClient: ApiClient
  children: React.ReactNode
}

export const ContactStoreProvider: React.FC<ContactStoreProviderProps> = ({ apiClient, children }) => {
  const storeRef = React.useRef<ContactStoreType>()
  
  if (!storeRef.current) {
    storeRef.current = createContactStore(apiClient)
  }
  
  return React.createElement(
    ContactStoreContext.Provider,
    { value: storeRef.current },
    children
  )
}

// Hook to use the shared contact store
export const useContactStore = () => {
  const store = useContext(ContactStoreContext)
  if (!store) {
    throw new Error('useContactStore must be used within a ContactStoreProvider')
  }
  return store()
}

// Example usage:
// 1. Wrap your app section with the provider:
// const AppWithContactStore = ({ apiClient }) => (
//   <ContactStoreProvider apiClient={apiClient}>
//     <TableInstance />
//     <ChatDrawer />
//     <ContactFilterDialog />
//   </ContactStoreProvider>
// )
//
// 2. Use the hook in components:
// const TableInstance = () => {
//   const { table, getAll, updateTableOptions } = useContactStore()
//   // ... component logic
// }

export type { Contact, ContactListOptions, ContactEngagement, ContactFilter, ChatState, ContactInstance }
export default createContactStore
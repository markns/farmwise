import { create } from 'zustand'
import { jwtDecode } from 'jwt-decode'
import { differenceInMilliseconds, fromUnixTime, subMinutes } from 'date-fns'
import { authApi, type LoginCredentials, type RegisterCredentials, type UserListOptions } from '@/api/auth'
import { useNotificationStore } from './notificationStore'
import { useAppStore } from './appStore'

interface User {
  id?: string
  email: string
  role: string | null
  password?: string
  loading?: boolean
}

interface CurrentUser {
  loggedIn: boolean
  token: string | null
  email: string
  role: string | null
  experimental_features: boolean
  exp?: number
}

interface TableOptions {
  q: string
  page: number
  itemsPerPage: number
  sortBy: string[]
  descending: boolean[]
}

interface TableRows {
  items: User[]
  total: number | null
}

interface AuthState {
  currentUser: CurrentUser
  selected: User
  loading: boolean
  dialogs: {
    showCreateEdit: boolean
  }
  table: {
    rows: TableRows
    options: TableOptions
    loading: boolean
  }

  // Actions
  setUserLogin: (token: string) => void
  setUserLogout: () => void
  basicLogin: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
  createExpirationCheck: () => void
  getExperimentalFeatures: () => Promise<void>
  loginRedirect: (redirectUri: string) => void
  
  // Table actions
  getAll: () => Promise<void>
  createEditShow: (user?: User) => void
  closeCreateEdit: () => void
  save: () => Promise<void>
  remove: () => Promise<void>
  setSelected: (user: User) => void
  resetSelected: () => void
}

const getDefaultSelectedState = (): User => ({
  id: undefined,
  email: '',
  loading: false,
  role: null,
  password: '',
})

const avatarTemplate = import.meta.env.VITE_DISPATCH_AVATAR_TEMPLATE

export const useAuthStore = create<AuthState>((set, get) => ({
  currentUser: {
    loggedIn: false,
    token: null,
    email: '',
    role: null,
    experimental_features: false,
  },
  selected: getDefaultSelectedState(),
  loading: false,
  dialogs: {
    showCreateEdit: false,
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
      sortBy: ['email'],
      descending: [true],
    },
    loading: false,
  },

  setUserLogin: (token: string) => {
    const decoded = jwtDecode(token) as any
    set({
      currentUser: {
        ...get().currentUser,
        ...decoded,
        token,
        loggedIn: true,
      }
    })
    localStorage.setItem('token', token)
  },

  setUserLogout: () => {
    localStorage.removeItem('token')
    set({
      currentUser: {
        loggedIn: false,
        token: null,
        email: '',
        role: null,
        experimental_features: false,
      }
    })
    window.location.reload()
  },

  basicLogin: async (email: string, password: string) => {
    set({ loading: true })
    try {
      const credentials: LoginCredentials = { email, password }
      const response = await authApi.login(credentials)
      get().setUserLogin(response.token)
      
      // Add success notification
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Login successful',
        type: 'success',
      })
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Login failed. Please check your credentials.',
        type: 'error',
      })
      throw error
    } finally {
      set({ loading: false })
    }
  },

  register: async (email: string, password: string) => {
    try {
      const credentials: RegisterCredentials = { email, password }
      const response = await authApi.register(credentials)
      get().setUserLogin(response.token)
      
      // Add success notification
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Registration successful',
        type: 'success',
      })
    } catch (error) {
      const { addNotification } = useNotificationStore.getState()
      addNotification({
        text: 'Registration failed. Please try again.',
        type: 'error',
      })
      throw error
    }
  },

  logout: () => {
    get().setUserLogout()
  },

  createExpirationCheck: () => {
    const { currentUser } = get()
    if (!currentUser.exp) return

    const expireAt = subMinutes(fromUnixTime(currentUser.exp), 10)
    const now = new Date()

    setTimeout(() => {
      const { setRefresh } = useAppStore.getState()
      setRefresh({
        show: true,
        message: 'Your credentials have expired. Please refresh the page.',
      })
    }, differenceInMilliseconds(expireAt, now))
  },

  getExperimentalFeatures: async () => {
    try {
      const userInfo = await authApi.getUserInfo()
      set(state => ({
        currentUser: {
          ...state.currentUser,
          experimental_features: userInfo.experimental_features || false
        }
      }))
    } catch (error) {
      console.error('Error occurred while updating experimental features:', error)
    }
  },

  loginRedirect: (redirectUri: string) => {
    const redirectUrl = new URL(redirectUri)
    const queryMap: Record<string, string[]> = {}
    
    for (const [key, value] of redirectUrl.searchParams.entries()) {
      if (key in queryMap) {
        queryMap[key].push(value)
      } else {
        queryMap[key] = [value]
      }
    }
    
    // This will be implemented with React Router navigation
    console.log('Redirect to:', redirectUrl.pathname, queryMap)
  },

  // Table actions
  getAll: async () => {
    const state = get()
    set(prevState => ({
      table: { ...prevState.table, loading: true }
    }))
    
    try {
      const options: UserListOptions = {
        q: state.table.options.q,
        page: state.table.options.page,
        itemsPerPage: state.table.options.itemsPerPage,
        sortBy: state.table.options.sortBy,
        descending: state.table.options.descending,
      }
      const response = await authApi.getAll(options)
      set(prevState => ({
        table: {
          ...prevState.table,
          loading: false,
          rows: response
        }
      }))
    } catch (error) {
      set(prevState => ({
        table: { ...prevState.table, loading: false }
      }))
    }
  },

  createEditShow: (user?: User) => {
    set(prevState => ({
      dialogs: { ...prevState.dialogs, showCreateEdit: true },
      selected: user || getDefaultSelectedState()
    }))
  },

  closeCreateEdit: () => {
    set(prevState => ({
      dialogs: { ...prevState.dialogs, showCreateEdit: false },
      selected: getDefaultSelectedState()
    }))
  },

  save: async () => {
    const state = get()
    const { selected } = state
    const { addNotification } = useNotificationStore.getState()
    
    set(prevState => ({
      selected: { ...prevState.selected, loading: true }
    }))

    try {
      if (!selected.id) {
        await authApi.createUser(selected)
        addNotification({
          text: 'User created successfully.',
          type: 'success',
        })
      } else {
        await authApi.updateUser(selected.id, selected)
        addNotification({
          text: 'User updated successfully.',
          type: 'success',
        })
      }
      
      state.closeCreateEdit()
      state.getAll()
    } catch (error) {
      addNotification({
        text: 'Failed to save user.',
        type: 'error',
      })
    } finally {
      set(prevState => ({
        selected: { ...prevState.selected, loading: false }
      }))
    }
  },

  remove: async () => {
    const state = get()
    const { selected } = state
    const { addNotification } = useNotificationStore.getState()
    
    if (!selected.id) return
    
    try {
      await authApi.deleteUser(selected.id)
      addNotification({
        text: 'User deleted successfully.',
        type: 'success',
      })
      state.getAll()
    } catch (error) {
      addNotification({
        text: 'Failed to delete user.',
        type: 'error',
      })
    }
  },

  setSelected: (user: User) => {
    set({ selected: { ...get().selected, ...user } })
  },

  resetSelected: () => {
    set({ selected: getDefaultSelectedState() })
  },
}))

// Computed values (equivalent to getters)
export const getUserAvatarUrl = (email: string): string => {
  if (!avatarTemplate) return ''
  const userId = email.split('@')[0]
  if (userId) {
    const stem = avatarTemplate.replace('*', userId)
    return `${window.location.protocol}//${window.location.host}${stem}`
  }
  return ''
}
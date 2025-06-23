import { create } from 'zustand'

export interface Notification {
  id: string
  text: string
  type: 'success' | 'error' | 'warning' | 'info'
  timeout?: number
  timestamp: number
}

interface NotificationState {
  notifications: Notification[]
  
  // Actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void
  removeNotification: (id: string) => void
  clearAllNotifications: () => void
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],

  addNotification: (notification) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: Date.now(),
    }

    set(state => ({
      notifications: [...state.notifications, newNotification]
    }))

    // Auto-remove notification after timeout (default 5 seconds)
    const timeout = notification.timeout ?? 5000
    if (timeout > 0) {
      setTimeout(() => {
        get().removeNotification(newNotification.id)
      }, timeout)
    }
  },

  removeNotification: (id) => {
    set(state => ({
      notifications: state.notifications.filter(n => n.id !== id)
    }))
  },

  clearAllNotifications: () => {
    set({ notifications: [] })
  },
}))

// Helper function for backward compatibility with Vuex notifications
export const addBeNotification = (notification: { text: string; type: 'success' | 'error' | 'warning' | 'info' }) => {
  useNotificationStore.getState().addNotification(notification)
}
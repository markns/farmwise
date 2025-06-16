import { useAuthStore } from '@/stores/authStore'

export interface AuthProviderConfig {
  redirectPath?: string
}

export const basicAuthProvider = {
  /**
   * Initialize authentication state from localStorage
   */
  initialize(): boolean {
    const token = localStorage.getItem('token')
    
    if (token) {
      try {
        const { setUserLogin, createExpirationCheck, getExperimentalFeatures } = useAuthStore.getState()
        setUserLogin(token)
        createExpirationCheck()
        getExperimentalFeatures()
        return true
      } catch (error) {
        console.error('Invalid token found in localStorage:', error)
        localStorage.removeItem('token')
        return false
      }
    }
    
    return false
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const { currentUser } = useAuthStore.getState()
    return currentUser.loggedIn
  },

  /**
   * Handle login redirect logic
   */
  handleAuthRequired(currentPath: string, organization: string = 'default'): string | null {
    const loginPath = `/${organization}/auth/login`
    
    // Prevent redirect loop
    if (currentPath === loginPath) {
      return null
    }
    
    // Check if user is authenticated
    if (this.isAuthenticated()) {
      return null
    }
    
    // Redirect to login
    return loginPath
  },

  /**
   * Get the default redirect path after login
   */
  getDefaultRedirectPath(organization: string = 'default'): string {
    return `/${organization}/farms`
  },

  /**
   * Handle logout
   */
  logout(): void {
    const { logout } = useAuthStore.getState()
    logout()
  }
}

export default basicAuthProvider
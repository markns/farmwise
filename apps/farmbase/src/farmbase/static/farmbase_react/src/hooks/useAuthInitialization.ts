import { useEffect } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { basicAuthProvider } from '@/auth/providers/basicAuthProvider'

/**
 * Hook to initialize authentication state on app startup
 * This checks for existing tokens and sets up the auth state
 */
export const useAuthInitialization = () => {
  const currentUser = useAuthStore(state => state.currentUser)

  useEffect(() => {
    // Only initialize if not already logged in
    if (!currentUser.loggedIn) {
      basicAuthProvider.initialize()
    }
  }, [currentUser.loggedIn])

  return {
    isAuthenticated: currentUser.loggedIn,
    isLoading: false, // You could add a loading state here if needed
  }
}
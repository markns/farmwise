import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useAppStore } from '@/stores/appStore'

interface ProtectedRouteProps {
  children: React.ReactNode
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const location = useLocation()
  const currentUser = useAuthStore(state => state.currentUser)
  const setLoading = useAppStore(state => state.setLoading)
  
  React.useEffect(() => {
    setLoading(true)
    
    // Cleanup loading state
    const timer = setTimeout(() => {
      setLoading(false)
    }, 100)
    
    return () => {
      clearTimeout(timer)
      setLoading(false)
    }
  }, [location, setLoading])
  
  if (!currentUser.loggedIn) {
    // Extract organization from current path
    const pathParts = location.pathname.split('/')
    const organization = pathParts[1] || 'default'
    
    // Redirect to login with return URL
    return (
      <Navigate 
        to={`/${organization}/auth/login`} 
        state={{ from: location }} 
        replace 
      />
    )
  }
  
  return <>{children}</>
}

export default ProtectedRoute
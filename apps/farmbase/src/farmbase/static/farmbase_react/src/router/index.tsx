import React from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { allRoutes, RouteConfig } from './config'
// import { useAuthStore } from '@/stores/authStore'
// import { useAppStore } from '@/stores/appStore'
import ProtectedRoute from './ProtectedRoute'

// Convert our custom RouteConfig to React Router's RouteObject
const convertRoutes = (routes: RouteConfig[]): any[] => {
  return routes.map(route => {
    const { meta, ...routeProps } = route
    
    let element = routeProps.element
    
    // Wrap protected routes
    if (meta?.requiresAuth) {
      element = <ProtectedRoute>{element}</ProtectedRoute>
    }
    
    // Handle redirects
    if (route.path === '/') {
      element = <Navigate to="/default/farms" replace />
    }
    
    const converted: any = {
      ...routeProps,
      element,
    }
    
    // Convert children recursively
    if (route.children) {
      converted.children = convertRoutes(route.children)
    }
    
    return converted
  })
}

export const router = createBrowserRouter(convertRoutes(allRoutes))

// Auth provider configuration
const authProviderSlug = 
  import.meta.env.VITE_DISPATCH_AUTHENTICATION_PROVIDER_SLUG || 'dispatch-auth-provider-basic'

// Router guards equivalent - we'll handle this in components and hooks
export const useRouterGuards = () => {
  React.useEffect(() => {
    // This will be implemented with React Router's navigation events
    // For now, we'll handle loading states in individual components
  }, [])
}

export { authProviderSlug }
export default router
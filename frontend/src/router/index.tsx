import React from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { allRoutes, RouteConfig } from './config'

// Convert our custom RouteConfig to React Router's RouteObject
const convertRoutes = (routes: RouteConfig[]): any[] => {
  return routes.map(route => {
    const { meta, ...routeProps } = route
    
    let element = routeProps.element

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

// Router guards equivalent - we'll handle this in components and hooks
export const useRouterGuards = () => {
  React.useEffect(() => {
    // This will be implemented with React Router's navigation events
    // For now, we'll handle loading states in individual components
  }, [])
}

export {  }
export default router
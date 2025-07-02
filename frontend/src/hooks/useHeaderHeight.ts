import { useLocation, useParams } from 'react-router-dom'

export const useHeaderHeight = () => {
  const location = useLocation()
  const { organization = 'default' } = useParams()
  
  // Generate breadcrumbs based on current path to determine if breadcrumb bar is shown
  const generateBreadcrumbs = () => {
    const pathSegments = location.pathname.split('/').filter(segment => segment)
    const breadcrumbs = []
    
    if (pathSegments.length > 1) {
      breadcrumbs.push({
        label: pathSegments[0],
        path: `/${pathSegments[0]}`
      })
      
      if (pathSegments[1]) {
        breadcrumbs.push({
          label: pathSegments[1],
          path: location.pathname
        })
      }
    }
    
    return breadcrumbs
  }

  const breadcrumbs = generateBreadcrumbs()
  const baseToolbarHeight = 64
  const breadcrumbHeight = breadcrumbs.length > 0 ? 40 : 0 // Approximate height of breadcrumb bar
  const organizationBannerHeight = organization && organization !== 'default' ? 48 : 0 // Approximate height of organization banner
  
  return baseToolbarHeight + breadcrumbHeight + organizationBannerHeight
}
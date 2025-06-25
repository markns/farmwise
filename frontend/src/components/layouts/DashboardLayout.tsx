import React from 'react'
import { Outlet } from 'react-router-dom'
import { Box } from '@mui/material'
import AppDrawer from '../AppDrawer'
import AppToolbar from '../AppToolbar'
import NotificationSnackbarsWrapper from '../NotificationSnackbarsWrapper'
import OrganizationBanner from '../../organization/OrganizationBanner'
import { useAppStore } from '../../stores/appStore'
import { useHeaderHeight } from '../../hooks/useHeaderHeight'

const DashboardLayout: React.FC = () => {
  const toggleDrawer = useAppStore(state => state.toggleDrawer)
  const drawerHovered = useAppStore(state => state.drawerHovered)
  const headerHeight = useHeaderHeight()
  
  // Calculate dynamic margin based on drawer state
  const isExpanded = toggleDrawer || drawerHovered
  const drawerWidth = isExpanded ? 256 : 72

  return (
    <Box id="farmbase-dashboard" sx={{ position: 'relative', height: '100vh', overflow: 'hidden' }}>
      {/* Fixed Headers */}
      <Box sx={{ 
        position: 'fixed', 
        top: 0, 
        left: 0, 
        right: 0, 
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: '#ffffff'
      }}>
        <OrganizationBanner />
        <AppToolbar />
      </Box>
      
      {/* Main Layout Area - positioned below fixed headers */}
      <Box sx={{ 
        display: 'flex', 
        height: '100vh',
        paddingTop: `${headerHeight}px`, // Space for all fixed headers
      }}>
        {/* Fixed Navigation Drawer */}
        <Box sx={{ 
          width: drawerWidth,
          transition: 'width 0.2s ease-in-out',
          flexShrink: 0,
          height: '100%',
        }}>
          <AppDrawer />
        </Box>
        
        {/* Scrollable Main Content */}
        <Box 
          component="main" 
          sx={{ 
            flex: 1,
            overflow: 'auto', // Only this area scrolls
            backgroundColor: '#f8f9fa',
            height: '100%',
          }}
        >
          <Outlet />
        </Box>
      </Box>
      
      <NotificationSnackbarsWrapper />
    </Box>
  )
}

export default DashboardLayout
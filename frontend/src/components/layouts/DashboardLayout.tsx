import React from 'react'
import { Outlet } from 'react-router-dom'
import { Box } from '@mui/material'
import AppDrawer from '../AppDrawer'
import AppToolbar from '../AppToolbar'
import NotificationSnackbarsWrapper from '../NotificationSnackbarsWrapper'
import OrganizationBanner from '../../organization/OrganizationBanner'
import { useAppStore } from '../../stores/appStore'

const DashboardLayout: React.FC = () => {
  const toggleDrawer = useAppStore(state => state.toggleDrawer)
  const drawerHovered = useAppStore(state => state.drawerHovered)
  
  // Calculate dynamic margin based on drawer state
  const isExpanded = toggleDrawer || drawerHovered
  const drawerWidth = isExpanded ? 256 : 72

  return (
    <Box id="farmbase-dashboard" sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <OrganizationBanner />
      <AppToolbar />
      <Box sx={{ display: 'flex', flex: 1 }}>
        <AppDrawer />
        <Box 
          component="main" 
          sx={{ 
            flexGrow: 1,
            overflow: 'auto', 
            backgroundColor: '#f8f9fa',
            minHeight: 'calc(100vh - 64px)',
            marginLeft: 0, // Drawer handles its own positioning
            transition: 'width 0.2s ease-in-out',
            width: `calc(100vw - ${drawerWidth}px)`,
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
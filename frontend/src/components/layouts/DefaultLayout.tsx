import React from 'react'
import { Outlet } from 'react-router-dom'
import { Box, Container } from '@mui/material'
import AppDrawer from '../AppDrawer'
import AppToolbar from '../AppToolbar'
import Refresh from '../Refresh'
import NotificationSnackbarsWrapper from '../NotificationSnackbarsWrapper'
import OrganizationBanner from '../../organization/OrganizationBanner'
import { useAppStore } from '@/stores/appStore'
import { useHeaderHeight } from '@/hooks/useHeaderHeight'

const DefaultLayout: React.FC = () => {
  const toggleDrawer = useAppStore(state => state.toggleDrawer)
  const drawerHovered = useAppStore(state => state.drawerHovered)
  const headerHeight = useHeaderHeight()
  const isExpanded = toggleDrawer || drawerHovered
  const drawerWidth = isExpanded ? 256 : 72

  return (
    <Box id="farmbase" sx={{ position: 'relative', height: '100vh', overflow: 'hidden' }}>
      <Box sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: '#ffffff',
      }}>
        <OrganizationBanner />
        <AppToolbar />
      </Box>
      <Box sx={{ display: 'flex', height: '100vh', paddingTop: `${headerHeight}px` }}>
        <Box sx={{ width: drawerWidth, transition: 'width 0.2s ease-in-out', flexShrink: 0 }}>
          <AppDrawer />
        </Box>
        <Box
          component="main"
          sx={{ flex: 1, overflow: 'auto', height: '100%' }}
        >
          <Container maxWidth={false} sx={{ margin: 0, padding: 0 }}>
            <Outlet />
          </Container>
        </Box>
      </Box>
      <NotificationSnackbarsWrapper />
      <Refresh />
    </Box>
  )
}

export default DefaultLayout
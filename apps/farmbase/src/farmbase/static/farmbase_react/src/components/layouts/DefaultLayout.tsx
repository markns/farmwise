import React from 'react'
import { Outlet } from 'react-router-dom'
import { Box, Container } from '@mui/material'
import AppDrawer from '../AppDrawer'
import AppToolbar from '../AppToolbar'
import Refresh from '../Refresh'
import NotificationSnackbarsWrapper from '../NotificationSnackbarsWrapper'
import OrganizationBanner from '../../organization/OrganizationBanner'

const DefaultLayout: React.FC = () => {
  return (
    <Box id="farmbase" sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <OrganizationBanner />
      <AppToolbar />
      <Box sx={{ display: 'flex', flex: 1 }}>
        <AppDrawer />
        <Box component="main" sx={{ flex: 1, overflow: 'auto' }}>
          <Container 
            maxWidth={false} 
            sx={{ 
              margin: 0, 
              padding: 0,
              height: '100%'
            }}
          >
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
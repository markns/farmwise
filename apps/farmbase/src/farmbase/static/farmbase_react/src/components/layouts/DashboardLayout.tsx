import React from 'react'
import { Outlet } from 'react-router-dom'
import { Box, Container, Grid } from '@mui/material'
import AppDrawer from '../AppDrawer'
import AppToolbar from '../AppToolbar'
import NotificationSnackbarsWrapper from '../NotificationSnackbarsWrapper'
import OrganizationBanner from '../../organization/OrganizationBanner'

const DashboardLayout: React.FC = () => {
  return (
    <Box id="farmbase-dashboard" sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <OrganizationBanner />
      <AppToolbar />
      <Box sx={{ display: 'flex', flex: 1 }}>
        <AppDrawer />
        <Box component="main" sx={{ flex: 1, overflow: 'auto', padding: 2 }}>
          <Container maxWidth={false}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Outlet />
              </Grid>
            </Grid>
          </Container>
        </Box>
      </Box>
      <NotificationSnackbarsWrapper />
    </Box>
  )
}

export default DashboardLayout
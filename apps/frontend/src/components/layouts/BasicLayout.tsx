import React from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Box } from '@mui/material'
import NotificationSnackbarsWrapper from '../NotificationSnackbarsWrapper'
import OrganizationBanner from '../../organization/OrganizationBanner'

const BasicLayout: React.FC = () => {
  const location = useLocation()

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <NotificationSnackbarsWrapper />
      <OrganizationBanner />
      
      <AppBar 
        position="static" 
        elevation={0}
        sx={{ 
          borderBottom: '1px solid #d2d2d2',
          backgroundColor: 'background.paper',
          color: 'text.primary'
        }}
      >
        <Toolbar>
          <Typography 
            variant="h6" 
            component={Link}
            to="/default/farms"
            sx={{ 
              fontWeight: 'bold',
              textDecoration: 'none',
              color: 'inherit',
              letterSpacing: '0.1em'
            }}
          >
            F A R M W I S E
          </Typography>
        </Toolbar>
      </AppBar>

      <Box component="main" sx={{ flex: 1 }}>
        <Outlet key={location.pathname} />
      </Box>
    </Box>
  )
}

export default BasicLayout
import React from 'react'
import { Alert, Box } from '@mui/material'
import { useParams } from 'react-router-dom'

const OrganizationBanner: React.FC = () => {
  const { organization } = useParams()

  // This is a placeholder - in the real implementation, this would
  // fetch organization data and show relevant banners/notifications
  if (organization && organization !== 'default') {
    return (
      <Box sx={{ width: '100%' }}>
        <Alert severity="info" sx={{ borderRadius: 0 }}>
          Organization: {organization}
        </Alert>
      </Box>
    )
  }

  return null
}

export default OrganizationBanner
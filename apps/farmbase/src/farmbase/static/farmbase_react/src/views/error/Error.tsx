import React from 'react'
import { Box, Typography, Button, Container } from '@mui/material'
import { useNavigate } from 'react-router-dom'

const Error: React.FC = () => {
  const navigate = useNavigate()

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          textAlign: 'center',
        }}
      >
        <Typography variant="h1" component="h1" gutterBottom>
          500
        </Typography>
        <Typography variant="h4" component="h2" gutterBottom>
          Server Error
        </Typography>
        <Typography variant="body1" sx={{ mb: 4 }}>
          Something went wrong on our end. Please try again later.
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => navigate('/default/farms')}
        >
          Go Home
        </Button>
      </Box>
    </Container>
  )
}

export default Error
import React from 'react'
import { Container, Typography, Box, Paper } from '@mui/material'

const ResultList: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Search Results
      </Typography>
      
      <Paper sx={{ p: 3 }}>
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="text.secondary">
            Search results will be displayed here
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This is a placeholder component for the search functionality.
          </Typography>
        </Box>
      </Paper>
    </Container>
  )
}

export default ResultList
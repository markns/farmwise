import React from 'react'
import { 
  Box, 
  Card, 
  CardContent, 
  Container, 
  TextField, 
  Button, 
  Typography 
} from '@mui/material'

const Mfa: React.FC = () => {
  const [code, setCode] = React.useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // MFA verification logic would go here
    console.log('MFA code:', code)
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Card>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Multi-Factor Authentication
          </Typography>
          
          <Typography variant="body1" sx={{ mb: 3 }} align="center">
            Please enter the verification code from your authenticator app.
          </Typography>

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="code"
              label="Verification Code"
              autoComplete="off"
              autoFocus
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              Verify
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  )
}

export default Mfa
import React from 'react'
import { RouterProvider } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { Snackbar, Alert } from '@mui/material'
import router from './router'
import { useNotificationStore } from './stores/notificationStore'
import { useUpdateDetection } from './hooks/useUpdateDetection'

// Create Material-UI theme matching Google Cloud Console
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2', // Google Blue
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#9c27b0',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
    text: {
      primary: '#3c4043',
      secondary: '#5f6368',
    },
    divider: '#e0e0e0',
  },
  typography: {
    fontFamily: '"Google Sans", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontFamily: '"Google Sans", "Roboto", sans-serif',
      fontWeight: 400,
    },
    h2: {
      fontFamily: '"Google Sans", "Roboto", sans-serif',
      fontWeight: 400,
    },
    h3: {
      fontFamily: '"Google Sans", "Roboto", sans-serif',
      fontWeight: 400,
    },
    h4: {
      fontFamily: '"Google Sans", "Roboto", sans-serif',
      fontWeight: 400,
    },
    h5: {
      fontFamily: '"Google Sans", "Roboto", sans-serif',
      fontWeight: 500,
    },
    h6: {
      fontFamily: '"Google Sans", "Roboto", sans-serif',
      fontWeight: 500,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '4px',
          fontSize: '14px',
          fontWeight: 500,
          padding: '8px 16px',
        },
        contained: {
          boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
          '&:hover': {
            boxShadow: '0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
          borderRadius: '8px',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: '16px',
          fontSize: '12px',
        },
      },
    },
  },
})

const App: React.FC = () => {
  const { updateExists, refreshApp } = useUpdateDetection()
  const notifications = useNotificationStore(state => state.notifications)
  const removeNotification = useNotificationStore(state => state.removeNotification)
  

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="app-root">
        <RouterProvider router={router} />
        
        {/* Update notification snackbar */}
        <Snackbar
          open={updateExists}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          autoHideDuration={null}
          action={
            <button onClick={refreshApp} style={{ color: 'white', background: 'none', border: 'none', cursor: 'pointer' }}>
              Update
            </button>
          }
        >
          <Alert severity="info" onClose={() => {}}>
            An update is available
          </Alert>
        </Snackbar>

        {/* General notifications */}
        {notifications.map((notification) => (
          <Snackbar
            key={notification.id}
            open={true}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            autoHideDuration={notification.timeout || 5000}
            onClose={() => removeNotification(notification.id)}
          >
            <Alert 
              severity={notification.type} 
              onClose={() => removeNotification(notification.id)}
            >
              {notification.text}
            </Alert>
          </Snackbar>
        ))}
      </div>
    </ThemeProvider>
  )
}

export default App
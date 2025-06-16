import React from 'react'
import { RouterProvider } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { Snackbar, Alert } from '@mui/material'
import router from './router'
import { useNotificationStore } from './stores/notificationStore'
import { useUpdateDetection } from './hooks/useUpdateDetection'
import { useAuthInitialization } from './hooks/useAuthInitialization'

// Create Material-UI theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

const App: React.FC = () => {
  const { updateExists, refreshApp } = useUpdateDetection()
  const notifications = useNotificationStore(state => state.notifications)
  const removeNotification = useNotificationStore(state => state.removeNotification)
  
  // Initialize authentication state
  useAuthInitialization()

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
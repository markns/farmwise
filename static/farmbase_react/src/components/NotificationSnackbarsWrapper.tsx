import React from 'react'
import { Snackbar, Alert, Portal } from '@mui/material'
import { useNotificationStore } from '../stores/notificationStore'

const NotificationSnackbarsWrapper: React.FC = () => {
  const notifications = useNotificationStore(state => state.notifications)
  const removeNotification = useNotificationStore(state => state.removeNotification)

  return (
    <Portal>
      {notifications.map((notification, index) => (
        <Snackbar
          key={notification.id}
          open={true}
          anchorOrigin={{ 
            vertical: 'bottom', 
            horizontal: 'right' 
          }}
          style={{ 
            marginBottom: index * 60 // Stack notifications
          }}
          autoHideDuration={notification.timeout || 5000}
          onClose={() => removeNotification(notification.id)}
        >
          <Alert 
            severity={notification.type} 
            onClose={() => removeNotification(notification.id)}
            variant="filled"
          >
            {notification.text}
          </Alert>
        </Snackbar>
      ))}
    </Portal>
  )
}

export default NotificationSnackbarsWrapper
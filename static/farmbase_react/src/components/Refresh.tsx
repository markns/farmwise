import React from 'react'
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography } from '@mui/material'
import { useAppStore } from '../stores/appStore'

const Refresh: React.FC = () => {
  const refresh = useAppStore(state => state.refresh)
  const performRefresh = useAppStore(state => state.performRefresh)
  const resetRefresh = useAppStore(state => state.resetRefresh)

  const handleRefresh = () => {
    performRefresh()
  }

  const handleClose = () => {
    resetRefresh()
  }

  return (
    <Dialog open={refresh.show} onClose={handleClose}>
      <DialogTitle>Refresh Required</DialogTitle>
      <DialogContent>
        <Typography>
          {refresh.message || 'The application needs to be refreshed.'}
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} color="secondary">
          Cancel
        </Button>
        <Button onClick={handleRefresh} color="primary" variant="contained">
          Refresh
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default Refresh
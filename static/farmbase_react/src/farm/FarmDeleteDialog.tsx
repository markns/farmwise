import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert,
} from '@mui/material'
import {
  Warning as WarningIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'
import { useFarmStore } from '@/stores/farmStore'

const FarmDeleteDialog: React.FC = () => {
  const {
    dialogs,
    selected,
    closeRemove,
    remove,
  } = useFarmStore()

  const [isDeleting, setIsDeleting] = React.useState(false)

  const handleDelete = async () => {
    if (!selected) return

    setIsDeleting(true)
    try {
      await remove()
    } finally {
      setIsDeleting(false)
    }
  }

  const handleClose = () => {
    if (!isDeleting) {
      closeRemove()
    }
  }

  return (
    <Dialog
      open={dialogs.showRemove}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <WarningIcon color="warning" />
          <Typography variant="h6">
            Delete Farm
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Alert severity="warning" sx={{ mb: 2 }}>
          This action cannot be undone. All data associated with this farm will be permanently deleted.
        </Alert>

        <Typography variant="body1">
          Are you sure you want to delete the farm{' '}
          <strong>"{selected?.farm_name}"</strong>?
        </Typography>

        {selected?.description && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Description:
            </Typography>
            <Typography variant="body2">
              {selected.description}
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button
          onClick={handleClose}
          disabled={isDeleting}
          variant="outlined"
        >
          Cancel
        </Button>
        <Button
          onClick={handleDelete}
          disabled={isDeleting}
          variant="contained"
          color="error"
          startIcon={isDeleting ? undefined : <DeleteIcon />}
        >
          {isDeleting ? 'Deleting...' : 'Delete Farm'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default FarmDeleteDialog
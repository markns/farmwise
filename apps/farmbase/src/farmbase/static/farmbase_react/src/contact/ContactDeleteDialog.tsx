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
import { useContactStore } from '@/stores/contactStore'

const ContactDeleteDialog: React.FC = () => {
  const {
    dialogs,
    selected,
    closeRemove,
    remove,
  } = useContactStore()

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
            Delete Contact
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Alert severity="warning" sx={{ mb: 2 }}>
          This action cannot be undone. All data associated with this contact will be permanently deleted.
        </Alert>

        <Typography variant="body1">
          Are you sure you want to delete the contact{' '}
          <strong>"{selected?.name}"</strong>?
        </Typography>

        {selected?.external_id && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              External ID:
            </Typography>
            <Typography variant="body2">
              {selected.external_id}
            </Typography>
          </Box>
        )}

        {selected?.role && (
          <Box sx={{ mt: 1, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Role:
            </Typography>
            <Typography variant="body2">
              {selected.role}
            </Typography>
          </Box>
        )}

        {selected?.organization && (
          <Box sx={{ mt: 1, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Organization:
            </Typography>
            <Typography variant="body2">
              {selected.organization}
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
          {isDeleting ? 'Deleting...' : 'Delete Contact'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default ContactDeleteDialog
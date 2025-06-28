import React from 'react'
import {
  Popover,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Box,
  Chip
} from '@mui/material'
import { Psychology as MemoryIcon, Close as CloseIcon } from '@mui/icons-material'
import { useContactStore } from '@/stores/contactStore'

const ContactMemoriesPopover: React.FC = () => {
  const { 
    dialogs, 
    selected, 
    memories, 
    closeMemories 
  } = useContactStore()

  const open = dialogs.showMemories
  const contact = selected

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never updated'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <Popover
      open={open}
      onClose={closeMemories}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'left'
      }}
      transformOrigin={{
        vertical: 'top',
        horizontal: 'left'
      }}
      PaperProps={{
        sx: { maxWidth: 500, maxHeight: 600 }
      }}
    >
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box display="flex" alignItems="center" gap={1}>
              <MemoryIcon color="primary" />
              <Typography variant="h6">Contact Memories</Typography>
              <Chip 
                label={memories.length} 
                size="small" 
                color="primary" 
                variant="outlined"
              />
            </Box>
            <IconButton onClick={closeMemories} size="small">
              <CloseIcon />
            </IconButton>
          </Box>

          {!contact && (
            <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
              No contact selected.
            </Typography>
          )}

          {contact && memories.length === 0 && (
            <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
              No memories found for {contact.name}.
            </Typography>
          )}

          {contact && memories.length > 0 && (
            <List sx={{ maxHeight: 400, overflow: 'auto', p: 0 }}>
              {memories.map((memory, index) => (
                <ListItem
                  key={memory.id}
                  divider={index < memories.length - 1}
                  sx={{ 
                    px: 0,
                    alignItems: 'flex-start',
                    flexDirection: 'column',
                    py: 1.5
                  }}
                >
                  <ListItemText
                    primary={memory.memory}
                    primaryTypographyProps={{
                      variant: 'body1',
                      sx: { mb: 0.5 }
                    }}
                  />
                  <Box display="flex" gap={1} alignItems="center">
                    <Typography variant="caption" color="text.secondary">
                      Created: {formatDate(memory.created_at)}
                    </Typography>
                    {memory.updated_at && memory.updated_at !== memory.created_at && (
                      <Typography variant="caption" color="text.secondary">
                        • Updated: {formatDate(memory.updated_at)}
                      </Typography>
                    )}
                  </Box>
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>
    </Popover>
  )
}

export default ContactMemoriesPopover
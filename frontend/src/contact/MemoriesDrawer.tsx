import React from 'react'
import {
  Drawer,
  Typography,
  List,
  ListItem,
  IconButton,
  Box,
  Chip,
  Divider,
  Avatar,
  Paper
} from '@mui/material'
import { Psychology as MemoryIcon, Close as CloseIcon } from '@mui/icons-material'
import { useContactStore } from '@/stores/contactStore'

const MemoriesDrawer: React.FC = () => {
  const { 
    dialogs, 
    selected, 
    memories, 
    closeMemories 
  } = useContactStore()

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
    <Drawer
      anchor="right"
      open={dialogs.showMemories}
      onClose={closeMemories}
      PaperProps={{
        sx: { 
          width: 500, 
          maxWidth: '90vw',
          zIndex: 1300 // Ensure it appears above the top navigation
        }
      }}
      sx={{
        zIndex: 1300 // Ensure the backdrop also has proper z-index
      }}
    >
      <Box sx={{ p: 2 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
              <MemoryIcon />
            </Avatar>
            <Typography variant="h6">
              Contact Memories - {selected?.name}
            </Typography>
            <Chip 
              label={memories.length} 
              size="small" 
              color="primary" 
              variant="outlined"
            />
          </Box>
          <IconButton onClick={closeMemories}>
            <CloseIcon />
          </IconButton>
        </Box>

        <Divider />

        {/* Memories List */}
        <Box sx={{ mt: 2, height: 'calc(100vh - 120px)', overflow: 'auto' }}>
          {!selected ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No contact selected
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Select a contact to view their memories.
              </Typography>
            </Box>
          ) : memories.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No memories found
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                This contact doesn't have any memories yet.
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {memories.map((memory, index) => (
                <ListItem key={memory.id} sx={{ px: 0, py: 1, alignItems: 'flex-start' }}>
                  <Box sx={{ width: '100%' }}>
                    {/* Memory Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Avatar 
                        sx={{ 
                          width: 24, 
                          height: 24, 
                          bgcolor: 'primary.light',
                          fontSize: '0.75rem'
                        }}
                      >
                        <MemoryIcon fontSize="small" />
                      </Avatar>
                      <Typography variant="caption" color="text.secondary">
                        Memory #{index + 1}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                        {formatDate(memory.created_at)}
                      </Typography>
                    </Box>

                    {/* Memory Content */}
                    <Paper 
                      sx={{ 
                        p: 2, 
                        ml: 4,
                        backgroundColor: '#f5f5f5',
                        border: '1px solid rgba(25, 118, 210, 0.12)',
                      }}
                    >
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                        {memory.memory}
                      </Typography>
                      
                      {/* Memory Metadata */}
                      <Box sx={{ mt: 1, pt: 1, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                          <Typography variant="caption" color="text.secondary">
                            Score: {memory.score !== null ? memory.score.toFixed(3) : 'N/A'}
                          </Typography>
                          {memory.updated_at && memory.updated_at !== memory.created_at && (
                            <Typography variant="caption" color="text.secondary">
                              Updated: {formatDate(memory.updated_at)}
                            </Typography>
                          )}
                        </Box>
                        {memory.metadata && Object.keys(memory.metadata).length > 0 && (
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                            Metadata: {JSON.stringify(memory.metadata)}
                          </Typography>
                        )}
                      </Box>
                    </Paper>
                  </Box>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      </Box>
    </Drawer>
  )
}

export default MemoriesDrawer
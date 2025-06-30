import React from 'react'
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  Divider,
  List,
  ListItem,
  Avatar,
  Paper,
  Chip,
} from '@mui/material'
import {
  Close as CloseIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  VideoFile as VideoIcon,
  AudioFile as AudioIcon,
} from '@mui/icons-material'
import { useContactStore } from '@/stores/contactStore'
import type { MessageSummary } from '@/stores/contactStore'

const ChatDrawer: React.FC = () => {
  const { dialogs, selected, messages, closeChat } = useContactStore()

  const getDirectionColor = (direction: MessageSummary['direction']) => {
    switch (direction) {
      case 'inbound':
        return '#1976d2' // Blue for user/inbound
      case 'outbound':
        return '#388e3c' // Green for Farmwise/outbound
      default:
        return '#757575'
    }
  }

  const getDirectionIcon = (direction: MessageSummary['direction']) => {
    switch (direction) {
      case 'inbound':
        return <PersonIcon />
      case 'outbound':
        return <BotIcon />
      default:
        return <PersonIcon />
    }
  }

  const getDirectionLabel = (direction: MessageSummary['direction']) => {
    switch (direction) {
      case 'inbound':
        return 'User'
      case 'outbound':
        return 'Farmwise'
      default:
        return 'Unknown'
    }
  }

  const formatTimestamp = (timestamp: string): string => {
    try {
      return new Date(timestamp).toLocaleString()
    } catch {
      return 'Unknown time'
    }
  }

  return (
    <Drawer
      anchor="right"
      open={dialogs.showChat}
      onClose={closeChat}
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
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'between', mb: 2 }}>
          <Typography variant="h6">
            Chat History - {selected?.name}
          </Typography>
          <IconButton onClick={closeChat} sx={{ ml: 'auto' }}>
            <CloseIcon />
          </IconButton>
        </Box>

        <Divider />

        {/* Chat Messages */}
        <Box sx={{ mt: 2, height: 'calc(100vh - 120px)', overflow: 'auto' }}>
          {!messages || messages.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No messages available
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Start a conversation to see messages here.
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {messages.map((message, _) => (
                <ListItem key={message.id} sx={{ px: 0, py: 1, alignItems: 'flex-start' }}>
                  <Box sx={{ width: '100%' }}>
                    {/* Message Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Avatar 
                        sx={{ 
                          width: 24, 
                          height: 24, 
                          bgcolor: getDirectionColor(message.direction),
                          fontSize: '0.75rem'
                        }}
                      >
                        {getDirectionIcon(message.direction)}
                      </Avatar>
                      <Chip
                        label={getDirectionLabel(message.direction)}
                        size="small"
                        sx={{
                          backgroundColor: getDirectionColor(message.direction),
                          color: 'white',
                          fontSize: '0.75rem',
                          height: 20,
                        }}
                      />
                      <Chip
                        label={message.type.toUpperCase()}
                        size="small"
                        variant="outlined"
                        sx={{
                          fontSize: '0.65rem',
                          height: 16,
                        }}
                      />
                      <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                        {formatTimestamp(message.timestamp)}
                      </Typography>
                    </Box>

                    {/* Message Content */}
                    <Paper 
                      sx={{ 
                        p: 2, 
                        ml: 4,
                        backgroundColor: message.direction === 'inbound' ? '#e3f2fd' : '#e8f5e8',
                        border: `1px solid ${getDirectionColor(message.direction)}20`,
                      }}
                    >
                      {/* Handle different message types */}
                      {message.type === 'image' && message.storage_url ? (
                        <Box>
                          <img
                            src={message.storage_url}
                            alt="Message image"
                            style={{
                              maxWidth: '100%',
                              maxHeight: '300px',
                              borderRadius: '4px',
                              objectFit: 'contain'
                            }}
                            onError={(e) => {
                              const target = e.currentTarget as HTMLImageElement
                              target.style.display = 'none'
                              const nextElement = target.nextElementSibling as HTMLElement
                              if (nextElement) {
                                nextElement.style.display = 'block'
                              }
                            }}
                          />
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ display: 'none', fontStyle: 'italic', mt: 1 }}
                          >
                            [Image failed to load]
                          </Typography>
                          {message.caption && (
                            <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                              {message.caption}
                            </Typography>
                          )}
                        </Box>
                      ) : message.type === 'video' ? (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <VideoIcon color="action" />
                          <Typography variant="body2" color="text.secondary">
                            [Video message - Player not yet implemented]
                          </Typography>
                          {message.caption && (
                            <Typography variant="body2" sx={{ ml: 2, fontStyle: 'italic' }}>
                              {message.caption}
                            </Typography>
                          )}
                        </Box>
                      ) : message.type === 'audio' ? (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <AudioIcon color="action" />
                          <Typography variant="body2" color="text.secondary">
                            [Audio message - Player not yet implemented]
                          </Typography>
                        </Box>
                      ) : (
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                          {message.text || '[No text content]'}
                        </Typography>
                      )}
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

export default ChatDrawer
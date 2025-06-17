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
  Settings as SystemIcon,
} from '@mui/icons-material'
import { useContactStore } from '@/stores/contactStore'

const ChatDrawer: React.FC = () => {
  const { dialogs, selected, chatState, closeChat } = useContactStore()

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'user':
        return '#1976d2'
      case 'assistant':
        return '#388e3c'
      case 'system':
        return '#f57c00'
      default:
        return '#757575'
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'user':
        return <PersonIcon />
      case 'assistant':
        return <BotIcon />
      case 'system':
        return <SystemIcon />
      default:
        return <PersonIcon />
    }
  }

  const formatTimestamp = (timestamp: string): string => {
    try {
      return new Date(timestamp).toLocaleString()
    } catch {
      return 'Unknown time'
    }
  }

  // const isImageUrl = (content: string): boolean => {
  //   console.log(content)
  //   return /\.(jpg|jpeg|png|gif|webp)$/i.test(content) || content.startsWith('data:image/')
  // }

  return (
    <Drawer
      anchor="right"
      open={dialogs.showChat}
      onClose={closeChat}
      PaperProps={{
        sx: { width: 500, maxWidth: '90vw' }
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
          {!chatState?.messages || chatState.messages.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No chat history available
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Start a conversation to see messages here.
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {chatState.messages
                  .filter(message => message.role !== undefined)
                  .map((message, index) => (
                <ListItem key={index} sx={{ px: 0, py: 1, alignItems: 'flex-start' }}>
                  <Box sx={{ width: '100%' }}>
                    {/* Message Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Avatar 
                        sx={{ 
                          width: 24, 
                          height: 24, 
                          bgcolor: getRoleColor(message.role),
                          fontSize: '0.75rem'
                        }}
                      >
                        {getRoleIcon(message.role)}
                      </Avatar>
                      <Chip
                        label={message.role.charAt(0).toUpperCase() + message.role.slice(1)}
                        size="small"
                        sx={{
                          backgroundColor: getRoleColor(message.role),
                          color: 'white',
                          fontSize: '0.75rem',
                          height: 20,
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
                        backgroundColor: message.role === 'user' ? '#e3f2fd' : 
                                        message.role === 'assistant' ? '#e8f5e8' : '#fff3e0',
                        border: `1px solid ${getRoleColor(message.role)}20`,
                      }}
                    >

                      {message.content.map((content, _) => (

                      // isImageUrl(content) ? (
                      //   <Box>
                      //     <img
                      //       src={message.content}
                      //       alt="Chat image"
                      //       style={{
                      //         maxWidth: '100%',
                      //         maxHeight: '200px',
                      //         borderRadius: '4px'
                      //       }}
                      //       onError={(e) => {
                      //         // Fallback for broken images
                      //         const target = e.currentTarget as HTMLImageElement
                      //         target.style.display = 'none'
                      //         const nextElement = target.nextElementSibling as HTMLElement
                      //         if (nextElement) {
                      //           nextElement.style.display = 'block'
                      //         }
                      //       }}
                      //     />
                      //     <Typography
                      //       variant="body2"
                      //       color="text.secondary"
                      //       sx={{ display: 'none', fontStyle: 'italic' }}
                      //     >
                      //       [Image failed to load: {message.content}]
                      //     </Typography>
                      //   </Box>
                      // ) : (
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                          {content.text}
                        </Typography>
                      // )}

                      ))

                      }



                      {/* Message Metadata */}
                      {message.metadata && Object.keys(message.metadata).length > 0 && (
                        <Box sx={{ mt: 1, pt: 1, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                          <Typography variant="caption" color="text.secondary">
                            Metadata: {JSON.stringify(message.metadata)}
                          </Typography>
                        </Box>
                      )}
                    </Paper>
                  </Box>
                </ListItem>
              ))}
            </List>
          )}
        </Box>

        {/* Agent State */}
        {chatState?.agent_state && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Agent State: <strong>{chatState.agent_state}</strong>
            </Typography>
          </Box>
        )}
      </Box>
    </Drawer>
  )
}

export default ChatDrawer
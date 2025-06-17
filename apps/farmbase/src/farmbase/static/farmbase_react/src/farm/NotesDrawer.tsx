import React from 'react'
import {
  Drawer,
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  CircularProgress,
  Chip,
  Divider,
} from '@mui/material'
import {
  Close as CloseIcon,
  StickyNote2 as NoteIcon,
  EventBusy as NoteOffIcon,
} from '@mui/icons-material'
import { useParams } from 'react-router-dom'
import {useFarmStore} from '@/stores/farmStore'
import type { Note } from '@/api/farm'
import LocationChip from './LocationChip'

const NotesDrawer: React.FC = () => {
  const { organization = 'default' } = useParams()
  const { 
    dialogs, 
    selected, 
    notes, 
    closeNotes 
  } = useFarmStore()

  const getImageUrl = (imagePath: string): string => {
    // If the image path is already a full URL, return it as is
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
      return imagePath
    }
    
    // If it's a relative path, assume it's relative to the API base
    if (imagePath.startsWith('/')) {
      return `file://${imagePath}`
    }
    
    // For paths without leading slash, prepend with standard path
    return `/api/v1/${organization}/files/${imagePath}`
  }

  const handleImageError = (error: any) => {
    console.warn('Failed to load image:', error)
  }

  return (
    <Drawer
      anchor="right"
      open={dialogs.showNotes}
      onClose={closeNotes}
      PaperProps={{
        sx: { width: 600 }
      }}
    >
      <Card sx={{ height: '100%', borderRadius: 0 }}>
        <CardContent>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <NoteIcon />
              Farm Notes
            </Typography>
            <IconButton onClick={closeNotes}>
              <CloseIcon />
            </IconButton>
          </Box>

          <Divider sx={{ mb: 2 }} />

          {/* Farm name */}
          {selected?.farm_name && (
            <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
              {selected.farm_name || 'Unknown Farm'}
            </Typography>
          )}

          {/* Loading state */}
          {notes.loading && (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
              <CircularProgress />
              <Typography variant="body2" sx={{ mt: 2 }}>
                Loading notes...
              </Typography>
            </Box>
          )}

          {/* Notes content */}
          {!notes.loading && (
            <Box sx={{ maxHeight: '70vh', overflowY: 'auto' }}>
              {notes.items.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 8, color: 'text.secondary' }}>
                  <NoteOffIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                  <Typography variant="body1">
                    No notes found for this farm
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ pb: 2 }}>
                  {notes.items.map((note: Note) => (
                    <Card key={note.id} variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        {/* Note content */}
                        <Typography
                          variant="body2"
                          sx={{
                            lineHeight: 1.5,
                            whiteSpace: 'pre-wrap',
                            wordWrap: 'break-word',
                            mb: 2,
                          }}
                        >
                          {note.content}
                        </Typography>

                        {/* Tags - if the note has tags */}
                        {(note as any).tags && (
                          <Box sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                              {(note as any).tags.split(',').map((tag: string, index: number) => (
                                <Chip
                                  key={index}
                                  label={tag.trim()}
                                  size="small"
                                  color="primary"
                                  variant="outlined"
                                />
                              ))}
                            </Box>
                          </Box>
                        )}

                        {/* Location - if the note has location */}
                        {(note as any).location && (
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                              Location
                            </Typography>
                            <LocationChip location={(note as any).location} />
                          </Box>
                        )}

                        {/* Image - if the note has an image */}
                        {(note as any).image_path && (
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                              Attached Image
                            </Typography>
                            <Box
                              component="img"
                              src={getImageUrl((note as any).image_path)}
                              alt={`Image for note ${note.id}`}
                              onError={handleImageError}
                              sx={{
                                maxHeight: 300,
                                maxWidth: '100%',
                                borderRadius: 1,
                                display: 'block',
                              }}
                              onLoad={() => {
                                // Handle successful load if needed
                              }}
                              style={{
                                objectFit: 'contain',
                              }}
                            />
                          </Box>
                        )}

                        {/* Note metadata */}
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', pt: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Note ID: {note.id}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  ))}

                  {/* Show total count if there are more notes */}
                  {notes.total !== null && notes.total > notes.items.length && (
                    <Box sx={{ textAlign: 'center', mt: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Showing {notes.items.length} of {notes.total} notes
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    </Drawer>
  )
}

export default NotesDrawer
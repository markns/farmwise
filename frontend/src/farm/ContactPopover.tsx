import React, { useState } from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Popover,
  IconButton,
  Chip,
} from '@mui/material'
import {
  Person as PersonIcon,
  Close as CloseIcon,
  Phone as PhoneIcon,
  Work as WorkIcon,
} from '@mui/icons-material'

interface Contact {
  id: string
  name: string
  role: string
  phone_number?: string
}

interface ContactPopoverProps {
  contact: Contact
  chipColor?: 'success' | 'info' | 'warning' | 'default'
}

const ContactPopover: React.FC<ContactPopoverProps> = ({ contact, chipColor = 'default' }) => {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null)

  // const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
  //   event.stopPropagation()
  //   setAnchorEl(event.currentTarget)
  // }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const open = Boolean(anchorEl)

  return (
    <>
      <Chip
        label={contact.name}
        size="small"
        color={chipColor}
        // click={handleClick}
        sx={{ cursor: 'pointer', margin: 0.25 }}
      />

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
      >
        <Card sx={{ minWidth: 280, maxWidth: 350 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" component="div" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <PersonIcon />
                Contact Details
              </Typography>
              <IconButton size="small" onClick={handleClose}>
                <CloseIcon />
              </IconButton>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Name
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                {contact.name}
              </Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Role
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                <WorkIcon fontSize="small" color="action" />
                <Typography variant="body2">
                  {contact.role || 'Not specified'}
                </Typography>
              </Box>
            </Box>

            {contact.phone_number && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Phone Number
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                  <PhoneIcon fontSize="small" color="action" />
                  <Typography variant="body2">
                    {contact.phone_number}
                  </Typography>
                </Box>
              </Box>
            )}

            {!contact.phone_number && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Phone Number
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Not provided
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      </Popover>
    </>
  )
}

export default ContactPopover
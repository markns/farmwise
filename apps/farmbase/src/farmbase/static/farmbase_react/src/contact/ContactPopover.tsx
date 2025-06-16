import React, { useState } from 'react'
import {
  Popover,
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip,
  Divider,
} from '@mui/material'
import {
  Person as PersonIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  Work as WorkIcon,
  Cake as CakeIcon,
  Business as BusinessIcon,
  Agriculture as FarmIcon,
  Interests as InterestsIcon,
} from '@mui/icons-material'
import type { Contact } from '@/stores/contactStore'

interface ContactPopoverProps {
  contact: Contact
  children: React.ReactElement
}

const ContactPopover: React.FC<ContactPopoverProps> = ({ contact, children }) => {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const open = Boolean(anchorEl)

  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map(word => word.charAt(0).toUpperCase())
      .slice(0, 2)
      .join('')
  }

  const getAvatarColor = (name: string): string => {
    const colors = [
      '#e3f2fd', '#f3e5f5', '#e8f5e8', '#fff3e0', '#fce4ec',
      '#e0f2f1', '#f1f8e9', '#e8eaf6', '#fff8e1', '#fde7e7'
    ]
    const index = name.charCodeAt(0) % colors.length
    return colors[index]
  }

  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'Not specified'
    try {
      return new Date(dateString).toLocaleDateString()
    } catch {
      return 'Invalid date'
    }
  }

  const calculateAge = (dateOfBirth?: string, estimatedAge?: number): string => {
    if (estimatedAge) return `~${estimatedAge} years`
    if (!dateOfBirth) return 'Not specified'
    
    try {
      const birth = new Date(dateOfBirth)
      const today = new Date()
      const age = today.getFullYear() - birth.getFullYear()
      const monthDiff = today.getMonth() - birth.getMonth()
      
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        return `${age - 1} years`
      }
      return `${age} years`
    } catch {
      return 'Not specified'
    }
  }

  const InfoRow: React.FC<{ icon: React.ReactNode; label: string; value?: string }> = ({ icon, label, value }) => {
    if (!value) return null
    
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <Box sx={{ color: 'text.secondary', fontSize: '1rem' }}>
          {icon}
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ minWidth: 80 }}>
          {label}:
        </Typography>
        <Typography variant="body2" fontWeight="medium">
          {value}
        </Typography>
      </Box>
    )
  }

  const renderProductInterests = () => {
    const interests = contact.product_interests
    if (!interests || (!interests.crops?.length && !interests.livestock?.length && !interests.other?.length)) {
      return null
    }

    const chips: React.ReactNode[] = []
    
    // Crops (green)
    if (interests.crops && interests.crops.length > 0) {
      interests.crops.forEach((crop, index) => (
        chips.push(
          <Chip
            key={`crop-${index}`}
            label={crop}
            size="small"
            sx={{
              bgcolor: '#c8e6c9',
              color: '#2e7d32',
              fontSize: '0.75rem',
              height: 20,
              margin: 0.25,
            }}
          />
        )
      ))
    }
    
    // Livestock (brown)
    if (interests.livestock && interests.livestock.length > 0) {
      interests.livestock.forEach((livestock, index) => (
        chips.push(
          <Chip
            key={`livestock-${index}`}
            label={livestock}
            size="small"
            sx={{
              bgcolor: '#d7ccc8',
              color: '#5d4037',
              fontSize: '0.75rem',
              height: 20,
              margin: 0.25,
            }}
          />
        )
      ))
    }
    
    // Other (blue)
    if (interests.other && interests.other.length > 0) {
      interests.other.forEach((other, index) => (
        chips.push(
          <Chip
            key={`other-${index}`}
            label={other}
            size="small"
            sx={{
              bgcolor: '#bbdefb',
              color: '#1976d2',
              fontSize: '0.75rem',
              height: 20,
              margin: 0.25,
            }}
          />
        )
      ))
    }

    return (
      <Box sx={{ mt: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <InterestsIcon sx={{ color: 'text.secondary', fontSize: '1rem' }} />
          <Typography variant="body2" color="text.secondary" fontWeight="medium">
            Product Interests:
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', ml: 3 }}>
          {chips}
        </Box>
      </Box>
    )
  }

  const renderFarms = () => {
    if (!contact.farms || contact.farms.length === 0) return null

    return (
      <Box sx={{ mt: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <FarmIcon sx={{ color: 'text.secondary', fontSize: '1rem' }} />
          <Typography variant="body2" color="text.secondary" fontWeight="medium">
            Associated Farms:
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, ml: 3 }}>
          {contact.farms.map((farm, index) => (
            <Chip
              key={index}
              label={farm.name || farm.farm_name}
              size="small"
              variant="outlined"
              sx={{ fontSize: '0.75rem', height: 20 }}
            />
          ))}
        </Box>
      </Box>
    )
  }

  return (
    <>
      {React.cloneElement(children, {
        onClick: handleClick,
        style: { cursor: 'pointer' }
      })}
      
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
        PaperProps={{
          sx: { maxWidth: 400, boxShadow: 3 }
        }}
      >
        <Card elevation={0}>
          <CardContent sx={{ p: 3 }}>
            {/* Header with avatar and name */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Avatar
                sx={{
                  width: 48,
                  height: 48,
                  bgcolor: getAvatarColor(contact.name),
                  color: 'text.primary',
                  fontSize: '1.125rem',
                }}
              >
                {getInitials(contact.name)}
              </Avatar>
              <Box>
                <Typography variant="h6" fontWeight="bold">
                  {contact.name}
                </Typography>
                {contact.role && (
                  <Typography variant="body2" color="text.secondary">
                    {contact.role}
                  </Typography>
                )}
              </Box>
            </Box>

            <Divider sx={{ mb: 2 }} />

            {/* Contact Information */}
            <Typography variant="subtitle2" color="primary" gutterBottom>
              Contact Details
            </Typography>
            
            <InfoRow 
              icon={<PhoneIcon />} 
              label="Phone" 
              value={contact.phone_number} 
            />
            <InfoRow 
              icon={<EmailIcon />} 
              label="Email" 
              value={contact.email} 
            />
            <InfoRow 
              icon={<PersonIcon />} 
              label="Preferred Address" 
              value={contact.preferred_form_of_address} 
            />

            {/* Personal Information */}
            {(contact.gender || contact.date_of_birth || contact.estimated_age || contact.experience || contact.organization) && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" color="primary" gutterBottom>
                  Personal Information
                </Typography>
                
                <InfoRow 
                  icon={<PersonIcon />} 
                  label="Gender" 
                  value={contact.gender} 
                />
                <InfoRow 
                  icon={<CakeIcon />} 
                  label="Date of Birth" 
                  value={formatDate(contact.date_of_birth)} 
                />
                <InfoRow 
                  icon={<CakeIcon />} 
                  label="Age" 
                  value={calculateAge(contact.date_of_birth, contact.estimated_age)} 
                />
                <InfoRow 
                  icon={<WorkIcon />} 
                  label="Experience" 
                  value={contact.experience ? `${contact.experience} years` : undefined} 
                />
                <InfoRow 
                  icon={<BusinessIcon />} 
                  label="Organization" 
                  value={contact.organization} 
                />
              </>
            )}

            {/* Product Interests */}
            {renderProductInterests()}

            {/* Associated Farms */}
            {renderFarms()}

            {/* External Reference */}
            {contact.external_id && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  External ID: <strong>{contact.external_id}</strong>
                </Typography>
              </>
            )}
          </CardContent>
        </Card>
      </Popover>
    </>
  )
}

export default ContactPopover
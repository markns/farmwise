import React, { useState } from 'react'
import {
  Button,
  Card,
  CardContent,
  Typography,
  Box,
  Popover,
  IconButton,
} from '@mui/material'
import {
  LocationOn as LocationIcon,
  Map as MapIcon,
  OpenInNew as OpenInNewIcon,
  Close as CloseIcon,
} from '@mui/icons-material'

interface Location {
  latitude: number
  longitude: number
  address?: string
}

interface LocationPopoverProps {
  location: Location
  farmName: string
}

const LocationPopover: React.FC<LocationPopoverProps> = ({ location, farmName }) => {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null)

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const open = Boolean(anchorEl)

  const formatLocation = (loc: Location): string => {
    return `${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)}`
  }

  const getGoogleMapsLink = (): string => {
    return `https://www.google.com/maps?q=${location.latitude},${location.longitude}`
  }

  return (
    <>
      <Button
        variant="text"
        color="primary"
        size="small"
        startIcon={<LocationIcon />}
        onClick={handleClick}
        sx={{ textTransform: 'none' }}
      >
        {formatLocation(location)}
      </Button>

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
        <Card sx={{ minWidth: 350, maxWidth: 400 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" component="div" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocationIcon />
                {farmName} Location
              </Typography>
              <IconButton size="small" onClick={handleClose}>
                <CloseIcon />
              </IconButton>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography variant="caption" color="text.secondary">
                Coordinates
              </Typography>
              <Typography variant="body2">
                <strong>Latitude:</strong> {location.latitude.toFixed(6)}<br />
                <strong>Longitude:</strong> {location.longitude.toFixed(6)}
              </Typography>
            </Box>

            {location.address && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="caption" color="text.secondary">
                  Address
                </Typography>
                <Typography variant="body2">
                  {location.address}
                </Typography>
              </Box>
            )}

            {/* Map placeholder */}
            <Box
              sx={{
                height: 150,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%)',
                color: 'text.secondary',
                mb: 2,
              }}
            >
              <MapIcon sx={{ fontSize: 64 }} />
              <Typography variant="body2" sx={{ mt: 1 }}>
                Map View
              </Typography>
              <Typography variant="caption">
                {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
              </Typography>
            </Box>

            <Button
              href={getGoogleMapsLink()}
              target="_blank"
              rel="noopener noreferrer"
              variant="outlined"
              color="primary"
              size="small"
              fullWidth
              startIcon={<OpenInNewIcon />}
            >
              View in Google Maps
            </Button>
          </CardContent>
        </Card>
      </Popover>
    </>
  )
}

export default LocationPopover
import React, { useState, useEffect, useRef } from 'react'
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
  Close as CloseIcon,
} from '@mui/icons-material'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

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
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
    if (map.current) {
      map.current.remove()
      map.current = null
    }
  }

  const open = Boolean(anchorEl)

  useEffect(() => {
    mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
  }, [])

  useEffect(() => {
    if (open && !map.current) {
      // Use a longer delay and check multiple times for the container
      const initMap = () => {
        if (mapContainer.current) {
          try {
            map.current = new mapboxgl.Map({
              container: mapContainer.current,
              style: 'mapbox://styles/mapbox/satellite-v9',
              center: [location.longitude, location.latitude],
              zoom: 15
            })

            // Add a marker at the location
            new mapboxgl.Marker()
              .setLngLat([location.longitude, location.latitude])
              .addTo(map.current)

            // Add navigation controls
            map.current.addControl(new mapboxgl.NavigationControl(), 'top-right')
            
            // Ensure map resizes properly
            map.current.on('load', () => {
              map.current?.resize()
            })
          } catch (error) {
            console.error('Error initializing map:', error)
          }
        } else {
          // If container is not ready, try again after a short delay
          setTimeout(initMap, 50)
        }
      }

      // Start initialization after popover is fully rendered
      setTimeout(initMap, 200)
    }
  }, [open, location.latitude, location.longitude])

  const formatLocation = (loc: Location): string => {
    return `${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)}`
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

            {/* Mapbox GL Map */}
            <Box
              ref={mapContainer}
              sx={{
                height: 200,
                width: '100%',
                minHeight: 200,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                mb: 2,
                position: 'relative',
                overflow: 'hidden',
                '& .mapboxgl-canvas': {
                  borderRadius: 1,
                },
                '& .mapboxgl-ctrl-top-right': {
                  top: '10px',
                  right: '10px',
                },
              }}
            />

          </CardContent>
        </Card>
      </Popover>
    </>
  )
}

export default LocationPopover
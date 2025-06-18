import React from 'react'
import { Chip } from '@mui/material'
import { LocationOn as LocationIcon } from '@mui/icons-material'

interface Location {
  latitude: number
  longitude: number
  address?: string
}

interface LocationChipProps {
  location: Location
}

const LocationChip: React.FC<LocationChipProps> = ({ location }) => {
  const formatLocation = (loc: Location): string => {
    if (loc.address) {
      return loc.address
    }
    return `${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)}`
  }

  const handleClick = () => {
    const mapsUrl = `https://www.google.com/maps?q=${location.latitude},${location.longitude}`
    window.open(mapsUrl, '_blank', 'noopener,noreferrer')
  }

  return (
    <Chip
      icon={<LocationIcon />}
      label={formatLocation(location)}
      variant="outlined"
      size="small"
      onClick={handleClick}
      sx={{ cursor: 'pointer' }}
    />
  )
}

export default LocationChip
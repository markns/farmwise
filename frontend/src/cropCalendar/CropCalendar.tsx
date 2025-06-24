import React, { useState, useEffect, useMemo } from 'react'
import { Calendar, momentLocalizer, Event } from 'react-big-calendar'
import moment from 'moment'
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Paper,
  Grid,
  SelectChangeEvent,
} from '@mui/material'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFnsV3'
import 'react-big-calendar/lib/css/react-big-calendar.css'
import './CropCalendar.scss'
import { withApiClient, type ApiClient } from '@/api/client'

const localizer = momentLocalizer(moment)

interface CropStage {
  order: number
  name: string
  duration: number
  id: number
  cycle_id: number
  created_at: string
  updated_at: string
}

interface CropEvent {
  event_identifier: string
  start_day: number
  end_day: number
  original_event_id: number
  id: number
  crop_cycle_id: number
  created_at: string
  updated_at: string
  event: {
    identifier: string
    title: string
    description: string
    nutshell: string
    event_category: string
    event_type: string
    importance: number
  }
}

interface CropCycleData {
  crop_id: string
  koppen_climate_classification: string
  id: number
  stages: CropStage[]
  events: CropEvent[]
}

interface CalendarEvent extends Event {
  title: string
  start: Date
  end: Date
  resource?: {
    type: 'stage' | 'event'
    data: CropStage | CropEvent
  }
}

interface CropCalendarProps {
  apiClient: ApiClient
}

const CropCalendar: React.FC<CropCalendarProps> = ({ apiClient }) => {
  const [selectedCrop, setSelectedCrop] = useState<string>('MAIZE')
  const [selectedClimate, setSelectedClimate] = useState<string>('Cfb')
  const [plantingDate, setPlantingDate] = useState<Date | null>(new Date())
  const [cropData, setCropData] = useState<CropCycleData | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const crops = [
    { value: 'MAIZE', label: 'Maize' },
    { value: 'RICE', label: 'Rice' },
    { value: 'WHEAT', label: 'Wheat' },
    { value: 'SORGHUM', label: 'Sorghum' },
    { value: 'BEANS', label: 'Beans' },
  ]

  const climateClassifications = [
    { value: 'Cfb', label: 'Cfb - Temperate oceanic' },
    { value: 'Cfa', label: 'Cfa - Humid subtropical' },
    { value: 'BSh', label: 'BSh - Hot semi-arid' },
    { value: 'BSk', label: 'BSk - Cold semi-arid' },
    { value: 'Aw', label: 'Aw - Tropical savanna' },
  ]

  useEffect(() => {
    fetchCropData()
  }, [selectedCrop, selectedClimate])

  const fetchCropData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await apiClient.get(
        `/agronomy/crop-cycles/crop/${selectedCrop}?koppen_climate_classification=${selectedClimate}`
      )
      
      if (response.data && response.data.length > 0) {
        setCropData(response.data[0])
      } else {
        setCropData(null)
        setError('No crop cycle data found for the selected crop and climate')
      }
    } catch (err) {
      setError('Failed to fetch crop cycle data')
      console.error('Error fetching crop data:', err)
    } finally {
      setLoading(false)
    }
  }

  const calendarEvents: CalendarEvent[] = useMemo(() => {
    if (!cropData || !plantingDate) return []

    const events: CalendarEvent[] = []
    const plantingMoment = moment(plantingDate)

    // Add stage events
    let cumulativeDays = 0
    cropData.stages.forEach((stage) => {
      const stageStart = plantingMoment.clone().add(cumulativeDays, 'days')
      const stageEnd = stageStart.clone().add(stage.duration - 1, 'days')
      
      events.push({
        title: `${stage.name} (${stage.duration} days)`,
        start: stageStart.toDate(),
        end: stageEnd.toDate(),
        resource: {
          type: 'stage',
          data: stage,
        },
      })
      
      cumulativeDays += stage.duration
    })

    // Add single-day events
    cropData.events.forEach((eventData) => {
      const eventDate = plantingMoment.clone().add(eventData.start_day, 'days')
      
      events.push({
        title: eventData.event.title,
        start: eventDate.toDate(),
        end: eventDate.toDate(),
        resource: {
          type: 'event',
          data: eventData,
        },
      })
    })

    return events
  }, [cropData, plantingDate])

  const handleCropChange = (event: SelectChangeEvent<string>) => {
    setSelectedCrop(event.target.value)
  }

  const handleClimateChange = (event: SelectChangeEvent<string>) => {
    setSelectedClimate(event.target.value)
  }

  const eventStyleGetter = (event: CalendarEvent) => {
    const style = {
      backgroundColor: event.resource?.type === 'stage' ? '#3174ad' : '#f57c00',
      borderRadius: '3px',
      opacity: 0.8,
      color: 'white',
      border: '0px',
      display: 'block',
    }
    return { style }
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Crop Calendar
        </Typography>
        
        <Paper sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Crop</InputLabel>
                <Select
                  value={selectedCrop}
                  label="Crop"
                  onChange={handleCropChange}
                >
                  {crops.map((crop) => (
                    <MenuItem key={crop.value} value={crop.value}>
                      {crop.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Climate Classification</InputLabel>
                <Select
                  value={selectedClimate}
                  label="Climate Classification"
                  onChange={handleClimateChange}
                >
                  {climateClassifications.map((climate) => (
                    <MenuItem key={climate.value} value={climate.value}>
                      {climate.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <DatePicker
                label="Planting Date"
                value={plantingDate}
                onChange={(newValue) => setPlantingDate(newValue)}
                slotProps={{
                  textField: {
                    fullWidth: true,
                  },
                }}
              />
            </Grid>
          </Grid>
        </Paper>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <Typography>Loading crop data...</Typography>
          </Box>
        )}

        {error && (
          <Box sx={{ p: 3 }}>
            <Typography color="error">{error}</Typography>
          </Box>
        )}

        {cropData && plantingDate && (
          <Paper sx={{ p: 2, height: '600px' }}>
            <Calendar
              localizer={localizer}
              events={calendarEvents}
              startAccessor="start"
              endAccessor="end"
              style={{ height: '100%' }}
              eventPropGetter={eventStyleGetter}
              views={['month', 'week', 'day', 'agenda']}
              defaultView="month"
              popup
              tooltipAccessor={(event) => 
                event.resource?.type === 'stage' 
                  ? `Stage: ${event.title}` 
                  : `Event: ${event.title}`
              }
            />
          </Paper>
        )}

        {cropData && (
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Crop Cycle Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Stages ({cropData.stages.length}):
                </Typography>
                {cropData.stages.map((stage, index) => (
                  <Typography key={stage.id} variant="body2" sx={{ ml: 2 }}>
                    {index + 1}. {stage.name} - {stage.duration} days
                  </Typography>
                ))}
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Events ({cropData.events.length}):
                </Typography>
                {cropData.events.slice(0, 5).map((event) => (
                  <Typography key={event.id} variant="body2" sx={{ ml: 2 }}>
                    Day {event.start_day}: {event.event.title}
                  </Typography>
                ))}
                {cropData.events.length > 5 && (
                  <Typography variant="body2" sx={{ ml: 2, fontStyle: 'italic' }}>
                    ... and {cropData.events.length - 5} more events
                  </Typography>
                )}
              </Grid>
            </Grid>
          </Paper>
        )}
      </Box>
    </LocalizationProvider>
  )
}

export default withApiClient(CropCalendar)
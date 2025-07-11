import React from 'react'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  CardActions,
  Alert,
  Chip,
} from '@mui/material'
import {
  CloudQueue as WeatherIcon,
  BugReport as PestIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import {apiBaseUrl, environment} from '@/config/env'
import { withAuthInfo, WithAuthInfoProps } from '@propelauth/react'

const Development: React.FC<WithAuthInfoProps> = ({ accessToken }) => {
  const [logs, setLogs] = React.useState<string[]>([])
  const [loading, setLoading] = React.useState(false)

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`])
  }

  const handleWeatherWorkflow = async () => {
    setLoading(true)
    addLog('Calling weather forecast workflow...')
    
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      
      if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`
      }
      
      const response = await fetch(`${apiBaseUrl}/default/workflows/weather-forecast`, {
        method: 'POST',
        headers,
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      addLog(`Weather workflow successful: ${data.workflow_id}`)
    } catch (error) {
      addLog(`Weather workflow failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  const handlePestAlertWorkflow = async () => {
    setLoading(true)
    addLog('Calling pest alert workflow...')
    
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      
      if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`
      }
      
      const response = await fetch(`${apiBaseUrl}/default/workflows/pest-alert`, {
        method: 'POST',
        headers,
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      addLog(`Pest alert workflow successful: ${data.workflow_id}`)
    } catch (error) {
      addLog(`Pest alert workflow failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleClearLogs = () => {
    setLogs([])
  }

  const developmentTools = [
    {
      title: 'Weather Forecast',
      description: 'Trigger weather forecast workflow',
      icon: <WeatherIcon />,
      action: handleWeatherWorkflow,
      color: '#1976d2',
    },
    {
      title: 'Pest Alert',
      description: 'Trigger pest alert workflow',
      icon: <PestIcon />,
      action: handlePestAlertWorkflow,
      color: '#d32f2f',
    },
  ]

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Development Tools
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        This section provides development utilities and testing tools for the application.
      </Alert>

      <Grid container spacing={3}>
        {/* Development Tools Grid */}
        <Grid item xs={12} md={8}>
          <Typography variant="h6" gutterBottom>
            Available Tools
          </Typography>
          <Grid container spacing={2}>
            {developmentTools.map((tool, index) => (
              <Grid item xs={12} sm={6} key={index}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box sx={{ 
                        color: tool.color, 
                        mr: 1,
                        display: 'flex',
                        alignItems: 'center'
                      }}>
                        {tool.icon}
                      </Box>
                      <Typography variant="h6" component="div">
                        {tool.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {tool.description}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button
                      size="small"
                      onClick={tool.action}
                      disabled={loading}
                      startIcon={tool.icon}
                      sx={{ color: tool.color }}
                    >
                      Run
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* System Information */}
        <Grid item xs={12} md={4}>
          <Typography variant="h6" gutterBottom>
            System Information
          </Typography>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              <strong>Environment:</strong> {environment}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Version:</strong> 1.0.0
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Build:</strong> {new Date().toLocaleDateString()}
            </Typography>
            <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip label="React" size="small" />
              {/*<Chip labels="TypeScript" size="small" />*/}
              {/*<Chip label="Material-UI" size="small" />*/}
              {/*<Chip label="Vite" size="small" />*/}
            </Box>
          </Paper>

          {/* Activity Logs */}
          <Typography variant="h6" gutterBottom>
            Activity Logs
          </Typography>
          <Paper 
            sx={{ 
              p: 2, 
              height: '300px', 
              overflow: 'auto',
              backgroundColor: '#f5f5f5',
              fontFamily: 'monospace'
            }}
          >
            {logs.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No activity logs yet...
              </Typography>
            ) : (
              logs.map((log, index) => (
                <Typography 
                  key={index} 
                  variant="body2" 
                  sx={{ 
                    fontSize: '12px',
                    fontFamily: 'monospace',
                    mb: 0.5
                  }}
                >
                  {log}
                </Typography>
              ))
            )}
          </Paper>
          <Box sx={{ mt: 1 }}>
            <Button 
              size="small" 
              onClick={handleClearLogs}
              startIcon={<RefreshIcon />}
              disabled={logs.length === 0}
            >
              Clear Logs
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  )
}

export default withAuthInfo(Development)
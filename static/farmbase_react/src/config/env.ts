// Environment configuration
export interface AppConfig {
  apiBaseUrl: string
  appTitle: string
  environment: 'development' | 'staging' | 'production'
  authUrl: string
}

// Get environment variables with defaults
const getEnvVar = (key: string, defaultValue?: string): string => {
  const value = import.meta.env[key]
  if (value === undefined && defaultValue === undefined) {
    throw new Error(`Environment variable ${key} is required but not defined`)
  }
  return value || defaultValue || ''
}

// Application configuration
export const config: AppConfig = {
  apiBaseUrl: getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000/api/v1'),
  appTitle: getEnvVar('VITE_APP_TITLE', 'FarmBase Console'),
  environment: getEnvVar('VITE_APP_ENVIRONMENT', 'development') as AppConfig['environment'],
  authUrl: getEnvVar('VITE_AUTH_URL'),
}

// Export individual config values for convenience
export const {
  apiBaseUrl,
  appTitle,
  environment,
  authUrl,
} = config

// Helper functions
export const isDevelopment = () => environment === 'development'
export const isProduction = () => environment === 'production'
export const isStaging = () => environment === 'staging'

// Debug logging in development
if (isDevelopment()) {
  console.log('🔧 App Configuration:', config)
}
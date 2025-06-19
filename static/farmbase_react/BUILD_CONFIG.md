# Build Configuration Guide

This document explains how to configure and build the FarmBase React application for different environments.

## Environment Configuration

The application uses environment variables to configure different settings for various deployment environments.

### Environment Files

- `.env` - Default development environment
- `.env.staging` - Staging environment configuration
- `.env.production` - Production environment configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Base URL for the FarmBase API | `http://localhost:8000/api/v1` |
| `VITE_APP_TITLE` | Application title shown in browser tab | `FarmBase Console` |
| `VITE_APP_ENVIRONMENT` | Current environment | `development` |
| `VITE_AUTH_URL` | PropelAuth URL for authentication | Required |

## Build Commands

### Development
```bash
npm run dev
```
Starts the development server using `.env` configuration.

### Production Build
```bash
npm run build:production
```
Builds the application for production using `.env.production` configuration.

### Staging Build
```bash
npm run build:staging
```
Builds the application for staging using `.env.staging` configuration.

### Default Build
```bash
npm run build
```
Builds using the current environment or `.env` if no mode is specified.

## Deployment Commands

### Production Deployment
```bash
npm run deploy
```
Builds for production and deploys to Firebase hosting.

### Staging Deployment
```bash
npm run deploy:staging
```
Builds for staging and deploys to Firebase hosting.

## Configuration Usage

The application configuration is centralized in `src/config/env.ts`:

```typescript
import { config, apiBaseUrl, appTitle, environment } from '@/config/env'

// Use individual values
console.log(apiBaseUrl) // "https://farmbase-519829651234.europe-west4.run.app/api/v1"

// Or use the full config object
console.log(config.environment) // "production"
```

## API URLs by Environment

- **Development**: `http://localhost:8000/api/v1`
- **Staging**: `https://farmbase-staging-519829651234.europe-west4.run.app/api/v1`
- **Production**: `https://farmbase-519829651234.europe-west4.run.app/api/v1`

## Example Custom Build

To build with a custom API URL:

```bash
VITE_API_BASE_URL=https://my-custom-api.com/api/v1 npm run build
```

## Notes

- All environment variables must be prefixed with `VITE_` to be accessible in the browser
- The HTML title tag automatically uses `VITE_APP_TITLE`
- Environment variables are baked into the build at compile time
- Never commit sensitive values to `.env` files in version control
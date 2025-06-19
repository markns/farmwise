# Farmbase React

This is the React conversion of the Farmbase Vue.js application.

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Material-UI (MUI)** - Component library (replacing Vuetify)
- **React Router** - Client-side routing
- **Zustand** - State management (replacing Vuex)
- **React Hook Form** - Form handling (replacing FormKit)
- **Sentry** - Error monitoring

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## Deploy

```bash
npm install -g firebase-tools

TODO:

```

## Project Structure

```
src/
├── components/         # Reusable UI components
│   └── layouts/       # Layout components
├── stores/            # Zustand state stores
├── router/            # React Router configuration
├── auth/              # Authentication components
├── farm/              # Farm management features
├── contact/           # Contact management features
├── organization/      # Organization features
├── search/            # Search functionality
├── views/             # Page components
├── hooks/             # Custom React hooks
├── utils/             # Utility functions
└── styles/            # Global styles

## Migration Status

This is a fully converted React application from the original Vue.js codebase with complete API integration and authentication system.

### ✅ Completed
- ✅ Project setup and configuration
- ✅ Complete routing structure with protected routes
- ✅ State management with Zustand stores
- ✅ Layout components (Default, Basic, Dashboard)
- ✅ Complete authentication system with login/register
- ✅ API client with axios interceptors
- ✅ Auth API integration with JWT handling
- ✅ Farm and Organization API modules
- ✅ Utility functions and helpers
- ✅ Error handling and notifications
- ✅ TypeScript configuration and type safety
- ✅ Material-UI component integration
- ✅ Build system and production optimization

### 🔄 In Progress / Next Steps
- [ ] Convert remaining business logic components (forms, contacts, etc.)
- [ ] Implement data tables with full CRUD operations
- [ ] Add comprehensive form validation
- [ ] Convert complex UI components
- [ ] Add unit and integration tests
- [ ] Performance optimization and code splitting
- [ ] Accessibility improvements

## Configuration

The app uses the same environment variables as the Vue version:

- `VITE_DISPATCH_SENTRY_ENABLED` - Enable Sentry error tracking
- `VITE_DISPATCH_SENTRY_DSN` - Sentry DSN
- `VITE_DISPATCH_AUTH_REGISTRATION_ENABLED` - Enable user registration
- `VITE_DISPATCH_AUTHENTICATION_PROVIDER_SLUG` - Auth provider configuration
- `VITE_DISPATCH_AVATAR_TEMPLATE` - Avatar URL template
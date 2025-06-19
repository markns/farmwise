/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_ENVIRONMENT: string
  readonly VITE_AUTH_URL: string
  readonly VITE_DISPATCH_SENTRY_ENABLED?: string
  readonly VITE_DISPATCH_SENTRY_DSN?: string
  readonly VITE_DISPATCH_AUTH_REGISTRATION_ENABLED?: string
  readonly VITE_DISPATCH_AUTHENTICATION_PROVIDER_SLUG?: string
  readonly VITE_DISPATCH_AVATAR_TEMPLATE?: string
  readonly VITE_DISPATCH_COMMIT_HASH?: string
  readonly VITE_DISPATCH_COMMIT_MESSAGE?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
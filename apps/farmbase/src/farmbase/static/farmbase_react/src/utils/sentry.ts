import * as Sentry from '@sentry/react'

export const initializeSentry = () => {
  const SENTRY_ENABLED = import.meta.env.VITE_DISPATCH_SENTRY_ENABLED
  const SENTRY_DSN = import.meta.env.VITE_DISPATCH_SENTRY_DSN

  if (SENTRY_ENABLED) {
    const APP_HOSTNAME = document.location.host
    let DSN = `https://1:1@${APP_HOSTNAME}/api/0`

    // Allow global override
    if (SENTRY_DSN) {
      DSN = SENTRY_DSN
    }

    Sentry.init({
      dsn: DSN,
      integrations: [
        Sentry.browserTracingIntegration(),
      ],
      tracesSampleRate: 1.0,
    })
  }
}
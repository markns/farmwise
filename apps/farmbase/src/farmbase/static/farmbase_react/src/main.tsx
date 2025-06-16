import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/index.scss'
import {initializeSentry} from './utils/sentry'
import {RequiredAuthProvider} from "@propelauth/react";

export const VITE_AUTH_URL = import.meta.env.VITE_AUTH_URL;

// Initialize Sentry if enabled
initializeSentry()

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <RequiredAuthProvider authUrl={VITE_AUTH_URL}>
            <App/>
        </RequiredAuthProvider>,
    </React.StrictMode>
)
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import React from 'react'
import { useNotificationStore } from '@/stores/notificationStore'
import { WithAuthInfoProps, withAuthInfo } from '@propelauth/react'
import { apiBaseUrl } from '@/config/env'

export interface ApiConfig {
  baseURL?: string
  timeout?: number
  accessToken?: string | null
}

export class ApiClient {
  private instance: AxiosInstance
  private accessToken: string | null

  constructor(config: ApiConfig = {}) {
    this.accessToken = config.accessToken || null

    this.instance = axios.create({
      baseURL: config.baseURL || apiBaseUrl,
      timeout: config.timeout || 20000,
    })

    this.setupInterceptors()
  }

  // Method to update the access token
  setAccessToken(token: string | null) {
    this.accessToken = token
  }

  private setupInterceptors() {
    // Request interceptor for auth and organization context
    this.instance.interceptors.request.use(
      (config) => {
        // Remove empty query parameters
        if (config.params) {
          if (!config.params['q']) {
            delete config.params['q']
          }
        }

        // Add auth token
        if (this.accessToken) {
          config.headers['Authorization'] = `Bearer ${this.accessToken}`
        }

        return config
      },
      (error) => Promise.reject(error)
    )

    // Organization context interceptor
    this.instance.interceptors.request.use((config) => {
      // Skip organization prefix for global endpoints
      const globalEndpoints = ['/markets', '/commodities', '/market_prices', '/crop-varieties', '/agronomy']
      const isGlobalEndpoint = globalEndpoints.some(endpoint => config.url?.includes(endpoint))
      
      if (!config.url?.includes('organization') && !isGlobalEndpoint) {
        // Extract organization from current URL path
        const pathParts = window.location.pathname.split('/')
        const currentOrganization = pathParts[1] || 'default'

        if (currentOrganization) {
          config.url = `${currentOrganization}${config.url}`
        }
      }
      return config
    })

    // Response interceptor for error handling
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        if (error.response) {
          this.handleErrorResponse(error)
        }
        return Promise.reject(error)
      }
    )
  }

  private handleErrorResponse(error: any) {
    const { addNotification } = useNotificationStore.getState()
    const status = error.response.status

    // Handle authentication errors
    if (status === 401) {
      // if (this.authProviderSlug === 'dispatch-auth-provider-basic') {
        // Redirect to login - handled by PropelAuth
        window.location.href = '/login'
      // } else {
      //   window.location.reload()
      // }
      return
    }

    // Skip error handling if explicitly disabled
    if (error.config?.errorHandle === false) {
      return
    }

    // Handle various error types
    let errorText = ''
    
    if (status === 403 || status === 409 || status === 422) {
      if (error.response.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          errorText = error.response.data.detail.map((item: any) => item.msg || item).join(' ')
        } else {
          errorText = error.response.data.detail
        }
      }
    } else if (status === 500) {
      if (error.response.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          errorText = error.response.data.detail.map((item: any) => item.msg || item).join(' ')
        } else {
          errorText = error.response.data.detail
        }
      }
      
      if (!errorText) {
        errorText = 'Something has gone wrong. Please retry or let your admin know that you received this error.'
      }
    }

    if (errorText) {
      addNotification({
        text: errorText,
        type: 'error',
      })
    }
  }

  // HTTP methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.get(url, config)
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.post(url, data, config)
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.put(url, data, config)
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.patch(url, data, config)
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.delete(url, config)
  }

  // Get the raw axios instance if needed
  getInstance(): AxiosInstance {
    return this.instance
  }
}

// Create factory function for PropelAuth integration
export const createApiClient = (accessToken?: string | null) => {
  return new ApiClient({ accessToken })
}

// HOC to provide an authenticated API client via PropelAuth
export const withApiClient = <P extends object>(
  Component: React.ComponentType<P & { apiClient: ApiClient }>
) => {
  return withAuthInfo((props: WithAuthInfoProps & P) => {
    const apiClient = createApiClient(props.accessToken)
    return React.createElement(Component, { ...props, apiClient })
  })
}

// Create and export a singleton instance (for backwards compatibility)
// export const apiClient = new ApiClient()
// export default apiClient
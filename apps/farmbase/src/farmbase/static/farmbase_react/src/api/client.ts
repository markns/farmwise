import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/authStore'
import { useNotificationStore } from '@/stores/notificationStore'

export interface ApiConfig {
  baseURL?: string
  timeout?: number
}

class ApiClient {
  private instance: AxiosInstance
  private authProviderSlug: string

  constructor(config: ApiConfig = {}) {
    this.authProviderSlug = 
      import.meta.env.VITE_DISPATCH_AUTHENTICATION_PROVIDER_SLUG || 'dispatch-auth-provider-basic'

    this.instance = axios.create({
      baseURL: config.baseURL || 'http://localhost:8000/api/v1',
      timeout: config.timeout || 10000,
    })

    this.setupInterceptors()
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
        const authState = useAuthStore.getState()
        const token = authState.currentUser.token
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`
        }

        return config
      },
      (error) => Promise.reject(error)
    )

    // Organization context interceptor
    this.instance.interceptors.request.use((config) => {
      if (!config.url?.includes('organization')) {
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
      if (this.authProviderSlug === 'dispatch-auth-provider-basic') {
        // Redirect to login - this will be handled by the auth store
        const { logout } = useAuthStore.getState()
        logout()
      } else {
        window.location.reload()
      }
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

// Create and export a singleton instance
export const apiClient = new ApiClient()
export default apiClient
import apiClient from './client'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials {
  email: string
  password: string
}

export interface User {
  id: string
  email: string
  role: string | null
  experimental_features?: boolean
}

export interface AuthResponse {
  token: string
  user?: User
}

export interface UserListOptions {
  q?: string
  page?: number
  itemsPerPage?: number
  sortBy?: string[]
  descending?: boolean[]
}

export interface UserListResponse {
  items: User[]
  total: number
}

export interface MfaVerification {
  code: string
  token?: string
}

const resource = 'users'

export const authApi = {
  // User management
  async getAll(options: UserListOptions = {}): Promise<UserListResponse> {
    const response = await apiClient.get(`/${resource}`, { params: options })
    return response.data
  },

  async getUser(userId: string): Promise<User> {
    const response = await apiClient.get(`/${resource}/${userId}`)
    return response.data
  },

  async updateUser(userId: string, payload: Partial<User>): Promise<User> {
    const response = await apiClient.put(`/${resource}/${userId}`, payload)
    return response.data
  },

  async createUser(payload: Partial<User>): Promise<User> {
    const response = await apiClient.post(`/${resource}`, payload)
    return response.data
  },

  async deleteUser(userId: string): Promise<void> {
    await apiClient.delete(`/${resource}/${userId}`)
  },

  // Authentication
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post('/auth/login', credentials)
    return response.data
  },

  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    const response = await apiClient.post('/auth/register', credentials)
    return response.data
  },

  async getUserInfo(): Promise<User> {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  async getUserRole(): Promise<{ role: string }> {
    const response = await apiClient.get('/auth/myrole')
    return response.data
  },

  async verifyMfa(payload: MfaVerification): Promise<AuthResponse> {
    const response = await apiClient.post('/auth/mfa', payload)
    return response.data
  },

  // Logout (client-side only, no API call needed)
  logout(): void {
    // This is handled entirely on the client side
    // Just clear the token from localStorage
    localStorage.removeItem('token')
  }
}

export default authApi
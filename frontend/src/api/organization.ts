import { ApiClient } from './client'

// Create a default API client instance for this module
const apiClient = new ApiClient()

export interface Organization {
  id: string
  name: string
  slug: string
  description?: string
  settings?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface OrganizationMember {
  id: string
  user_id: string
  organization_id: string
  role: string
  email: string
  name?: string
  joined_at: string
}

export interface OrganizationListOptions {
  q?: string
  page?: number
  itemsPerPage?: number
  sortBy?: string[]
  descending?: boolean[]
}

export interface OrganizationListResponse {
  items: Organization[]
  total: number
}

export interface MemberListOptions {
  q?: string
  page?: number
  itemsPerPage?: number
  sortBy?: string[]
  descending?: boolean[]
  role?: string
}

export interface MemberListResponse {
  items: OrganizationMember[]
  total: number
}

const resource = '/organizations'

export const organizationApi = {
  /**
   * Get all organizations
   */
  async getAll(options: OrganizationListOptions = {}): Promise<OrganizationListResponse> {
    const response = await apiClient.get(resource, { params: options })
    return response.data
  },

  /**
   * Get a specific organization by ID
   */
  async getOrganization(organizationId: string): Promise<Organization> {
    const response = await apiClient.get(`${resource}/${organizationId}`)
    return response.data
  },

  /**
   * Create a new organization
   */
  async createOrganization(payload: Partial<Organization>): Promise<Organization> {
    const response = await apiClient.post(resource, payload)
    return response.data
  },

  /**
   * Update an existing organization
   */
  async updateOrganization(organizationId: string, payload: Partial<Organization>): Promise<Organization> {
    const response = await apiClient.put(`${resource}/${organizationId}`, payload)
    return response.data
  },

  /**
   * Delete an organization
   */
  async deleteOrganization(organizationId: string): Promise<void> {
    await apiClient.delete(`${resource}/${organizationId}`)
  },

  /**
   * Get organization members
   */
  async getMembers(organizationId: string, options: MemberListOptions = {}): Promise<MemberListResponse> {
    const response = await apiClient.get(`${resource}/${organizationId}/members`, { params: options })
    return response.data
  },

  /**
   * Add a member to an organization
   */
  async addMember(organizationId: string, payload: { email: string, role: string }): Promise<OrganizationMember> {
    const response = await apiClient.post(`${resource}/${organizationId}/members`, payload)
    return response.data
  },

  /**
   * Update a member's role
   */
  async updateMember(organizationId: string, memberId: string, payload: { role: string }): Promise<OrganizationMember> {
    const response = await apiClient.put(`${resource}/${organizationId}/members/${memberId}`, payload)
    return response.data
  },

  /**
   * Remove a member from an organization
   */
  async removeMember(organizationId: string, memberId: string): Promise<void> {
    await apiClient.delete(`${resource}/${organizationId}/members/${memberId}`)
  },

  /**
   * Get current organization settings
   */
  async getSettings(organizationId: string): Promise<Record<string, any>> {
    const response = await apiClient.get(`${resource}/${organizationId}/settings`)
    return response.data
  },

  /**
   * Update organization settings
   */
  async updateSettings(organizationId: string, settings: Record<string, any>): Promise<Record<string, any>> {
    const response = await apiClient.put(`${resource}/${organizationId}/settings`, settings)
    return response.data
  }
}

export default organizationApi
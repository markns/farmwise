import { ApiClient } from './client'

// Contact data types
export interface Contact {
  id: string
  external_id: string
  external_url?: string
  name: string
  phone_number?: string
  email?: string
  preferred_form_of_address?: string
  gender?: string
  date_of_birth?: string
  estimated_age?: number
  role?: string
  experience?: number
  organization?: string
  product_interests?: ProductInterests
  farms?: Farm[]
  created_at: string
  updated_at: string
}

export interface ProductInterests {
  crops?: string[]
  livestock?: string[]
  other?: string[]
}

export interface Farm {
  id: string
  name: string
  farm_name?: string
}

export interface ContactListOptions {
  q?: string
  page?: number
  itemsPerPage?: number
  sortBy?: string[]
  descending?: boolean[]
  filters?: ContactFilters
}

export interface ContactFilters {
  contact_definition_ids?: string[]
  gender?: string[]
  role?: string[]
  organization?: string[]
  [key: string]: any
}

export interface ContactListResponse {
  items: Contact[]
  total: number
}

export interface ContactEngagement {
  id: string
  contact_id: string
  engagement_type: string
  engagement_date: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface ContactFilter {
  id: string
  name: string
  description?: string
  filter_type: string
  filter_criteria: Record<string, any>
  enabled: boolean
  created_at: string
  updated_at: string
}

export interface ChatState {
  contact_id: string
  messages: ChatMessage[]
  agent_state?: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: Record<string, any>[]
  timestamp: string
  metadata?: Record<string, any>
}

export interface ContactInstance {
  id: string
  contact_id: string
  instance_data: Record<string, any>
  created_at: string
  updated_at: string
}

// Factory function to create contact API with authenticated client
export const createContactApi = (client: ApiClient) => ({
  // Main contact operations
  async getAll(options: ContactListOptions = {}): Promise<ContactListResponse> {
    const params = new URLSearchParams()
    
    if (options.q) params.append('q', options.q)
    if (options.page) params.append('page', options.page.toString())
    if (options.itemsPerPage) params.append('itemsPerPage', options.itemsPerPage.toString())
    if (options.sortBy?.length) {
      options.sortBy.forEach(sort => params.append('sortBy', sort))
    }
    if (options.descending?.length) {
      options.descending.forEach(desc => params.append('descending', desc.toString()))
    }
    if (options.filters) {
      Object.entries(options.filters).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(`filters[${key}]`, v))
        } else if (value !== undefined && value !== null) {
          params.append(`filters[${key}]`, value.toString())
        }
      })
    }

    const response = await client.get(`/contacts?${params.toString()}`)
    return response.data
  },

  async getContact(id: string): Promise<Contact> {
    const response = await client.get(`/contacts/${id}`)
    return response.data
  },

  async createContact(contactData: Partial<Contact>): Promise<Contact> {
    const response = await client.post('/contacts', contactData)
    return response.data
  },

  async updateContact(id: string, contactData: Partial<Contact>): Promise<Contact> {
    const response = await client.put(`/contacts/${id}`, contactData)
    return response.data
  },

  async deleteContact(id: string): Promise<void> {
    await client.delete(`/contacts/${id}`)
  },

  // Contact instances
  async getAllInstances(options: ContactListOptions = {}): Promise<ContactListResponse> {
    const params = new URLSearchParams()
    
    if (options.q) params.append('q', options.q)
    if (options.page) params.append('page', options.page.toString())
    if (options.itemsPerPage) params.append('itemsPerPage', options.itemsPerPage.toString())

    const response = await client.get(`/contacts?${params.toString()}`)
    return response.data
  },

  async getContactInstance(contactId: string, instanceId: string): Promise<ContactInstance> {
    const response = await client.get(`/contacts/${contactId}/${instanceId}`)
    return response.data
  },

  // Contact engagements
  async getEngagements(contactId?: string): Promise<ContactEngagement[]> {
    const url = contactId 
      ? `/contacts/engagements?contact_id=${contactId}` 
      : '/contacts/engagements'
    const response = await client.get(url)
    return response.data.items || response.data
  },

  async createEngagement(engagementData: Partial<ContactEngagement>): Promise<ContactEngagement> {
    const response = await client.post('/contacts/engagements', engagementData)
    return response.data
  },

  async updateEngagement(id: string, engagementData: Partial<ContactEngagement>): Promise<ContactEngagement> {
    const response = await client.put(`/contacts/engagements/${id}`, engagementData)
    return response.data
  },

  async deleteEngagement(id: string): Promise<void> {
    await client.delete(`/contacts/engagements/${id}`)
  },

  // Contact filters
  async getFilters(): Promise<ContactFilter[]> {
    const response = await client.get('/contacts/filters')
    return response.data.items || response.data
  },

  async createFilter(filterData: Partial<ContactFilter>): Promise<ContactFilter> {
    const response = await client.post('/contacts/filters', filterData)
    return response.data
  },

  async updateFilter(id: string, filterData: Partial<ContactFilter>): Promise<ContactFilter> {
    const response = await client.put(`/contacts/filters/${id}`, filterData)
    return response.data
  },

  async deleteFilter(id: string): Promise<void> {
    await client.delete(`/contacts/filters/${id}`)
  },

  // Chat functionality
  async getChatState(contactId: string): Promise<ChatState> {
    const response = await client.get(`/chatstate?contact_id=${contactId}`)
    return response.data
  },

  // Utility methods
  async getFilterOptions(): Promise<Record<string, string[]>> {
    const response = await client.get('/contacts/filters/options')
    return response.data
  }
})

// Example usage with PropelAuth HOC:
// import { withApiClient } from '@/api/client'
// import { createContactApi } from '@/api/contact'
//
// const ContactComponent = ({ apiClient }) => {
//   const contactApi = createContactApi(apiClient)
//   // Use contactApi methods here...
//   return <div>Contact content</div>
// }
//
// export default withApiClient(ContactComponent)
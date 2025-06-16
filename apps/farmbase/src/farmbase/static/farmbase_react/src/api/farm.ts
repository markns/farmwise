import apiClient from './client'

export interface Farm {
  id: string
  name: string
  description?: string
  location?: {
    latitude: number
    longitude: number
    address?: string
  }
  area?: number
  owner?: string
  created_at: string
  updated_at: string
}

export interface FarmListOptions {
  q?: string
  page?: number
  itemsPerPage?: number
  sortBy?: string[]
  descending?: boolean[]
}

export interface FarmListResponse {
  items: Farm[]
  total: number
}

export interface Note {
  id: string
  content: string
  farm_id: string
  created_at: string
  updated_at: string
  author?: string
}

export interface NotesListOptions {
  page?: number
  itemsPerPage?: number
  sortBy?: string[]
  descending?: boolean[]
}

export interface NotesListResponse {
  items: Note[]
  total: number
}

const resource = '/farms'

export const farmApi = {
  /**
   * Get all farms with optional filtering and pagination
   */
  async getAll(options: FarmListOptions = {}): Promise<FarmListResponse> {
    const response = await apiClient.get(resource, { params: options })
    return response.data
  },

  /**
   * Get a specific farm by ID
   */
  async getFarm(farmId: string): Promise<Farm> {
    const response = await apiClient.get(`${resource}/${farmId}`)
    return response.data
  },

  /**
   * Create a new farm
   */
  async createFarm(payload: Partial<Farm>): Promise<Farm> {
    const response = await apiClient.post(resource, payload)
    return response.data
  },

  /**
   * Update an existing farm
   */
  async updateFarm(farmId: string, payload: Partial<Farm>): Promise<Farm> {
    const response = await apiClient.put(`${resource}/${farmId}`, payload)
    return response.data
  },

  /**
   * Delete a farm
   */
  async deleteFarm(farmId: string): Promise<void> {
    await apiClient.delete(`${resource}/${farmId}`)
  },

  /**
   * Get notes for a specific farm
   */
  async getNotes(farmId: string, options: NotesListOptions = {}): Promise<NotesListResponse> {
    const response = await apiClient.get('/notes', {
      params: { farm_id: farmId, ...options }
    })
    return response.data
  },

  /**
   * Create a note for a farm
   */
  async createNote(farmId: string, content: string): Promise<Note> {
    const response = await apiClient.post('/notes', {
      farm_id: farmId,
      content
    })
    return response.data
  },

  /**
   * Update a note
   */
  async updateNote(noteId: string, content: string): Promise<Note> {
    const response = await apiClient.put(`/notes/${noteId}`, { content })
    return response.data
  },

  /**
   * Delete a note
   */
  async deleteNote(noteId: string): Promise<void> {
    await apiClient.delete(`/notes/${noteId}`)
  }
}

export default farmApi
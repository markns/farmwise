import { ApiClient } from './client'

export interface CropVariety {
  variety: string
  producer: string
  description: string
  maturity_months: string
  yield_tons_ha: string
  min_altitude_masl: number
  max_altitude_masl: number
  maturity_category: string
}

export interface CropVarietiesResponse {
  crop: string
  varieties: CropVariety[]
}

export class CropVarietiesApi {
  constructor(private apiClient: ApiClient) {}

  async getCropVarieties(crop: string): Promise<CropVarietiesResponse> {
    const response = await this.apiClient.get<CropVarietiesResponse>(`/crop-varieties/${crop}`)
    return response.data
  }

  async getMaizeVarieties(): Promise<CropVarietiesResponse> {
    return this.getCropVarieties('maize')
  }
}
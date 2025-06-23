import { ApiClient } from './client'

export interface Market {
  id: number
  name: string
}

export interface Commodity {
  id: number
  name: string
  classification?: string | null
  grade?: string | null
  sex?: string | null
}

export interface MarketPrice {
  id: number
  price_date: string
  supply_volume?: number | null
  wholesale_price?: number | null
  wholesale_unit?: string | null
  wholesale_ccy: string
  retail_price?: number | null
  retail_unit?: string | null
  retail_ccy: string
  market: Market
  commodity: Commodity
}

export interface PaginatedResponse<T> {
  items_per_page: number
  page: number
  total: number
  items: T[]
}

export interface MarketPriceParams {
  market_id?: number
  commodity_id?: number
  page?: number
  items_per_page?: number
}

export class MarketApi {
  constructor(private apiClient: ApiClient) {}

  async getMarkets(): Promise<PaginatedResponse<Market>> {
    const response = await this.apiClient.get<PaginatedResponse<Market>>('/markets')
    return response.data
  }

  async getCommodities(page: number = 1, itemsPerPage: number = 50): Promise<PaginatedResponse<Commodity>> {
    const response = await this.apiClient.get<PaginatedResponse<Commodity>>('/commodities', {
      params: {
        page,
        items_per_page: itemsPerPage
      }
    })
    return response.data
  }

  async getAllCommodities(): Promise<Commodity[]> {
    const allCommodities: Commodity[] = []
    let page = 1
    let hasMore = true

    while (hasMore) {
      const response = await this.getCommodities(page, 50)
      allCommodities.push(...response.items)
      hasMore = response.items.length === response.items_per_page && allCommodities.length < response.total
      page++
    }

    return allCommodities
  }

  async getMarketPrices(params: MarketPriceParams = {}): Promise<PaginatedResponse<MarketPrice>> {
    const response = await this.apiClient.get<PaginatedResponse<MarketPrice>>('/market_prices', {
      params: {
        market_id: params.market_id,
        commodity_id: params.commodity_id,
        page: params.page || 1,
        items_per_page: params.items_per_page || 50
      }
    })
    return response.data
  }
}
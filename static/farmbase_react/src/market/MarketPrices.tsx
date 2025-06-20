import React from 'react'
import { MarketStoreProvider } from '@/stores/marketStore'
import { withApiClient, type ApiClient } from '@/api/client'
import MarketPricesTable from './MarketPricesTable'

interface MarketPricesProps {
  apiClient: ApiClient
}

// Inner component that renders the market prices table
const MarketPricesContent: React.FC = () => {
  return <MarketPricesTable />
}

// Main component that provides the store
const MarketPrices: React.FC<MarketPricesProps> = ({ apiClient }) => {
  return (
    <MarketStoreProvider apiClient={apiClient}>
      <MarketPricesContent />
    </MarketStoreProvider>
  )
}

export default withApiClient(MarketPrices)
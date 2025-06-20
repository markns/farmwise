import React from 'react'
import { SeedVarietiesStoreProvider } from '@/stores/seedVarietiesStore'
import { withApiClient, type ApiClient } from '@/api/client'
import SeedVarietiesTable from './SeedVarietiesTable'

interface SeedVarietiesProps {
  apiClient: ApiClient
}

// Inner component that renders the seed varieties table
const SeedVarietiesContent: React.FC = () => {
  return <SeedVarietiesTable />
}

// Main component that provides the store
const SeedVarieties: React.FC<SeedVarietiesProps> = ({ apiClient }) => {
  return (
    <SeedVarietiesStoreProvider apiClient={apiClient}>
      <SeedVarietiesContent />
    </SeedVarietiesStoreProvider>
  )
}

export default withApiClient(SeedVarieties)
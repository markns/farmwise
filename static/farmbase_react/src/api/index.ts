// Export the main API client
export { ApiClient, createApiClient, withApiClient } from './client'

// Export API modules selectively to avoid conflicts
export { createFarmApi } from './farm'
export { organizationApi } from './organization'
export * from './contact'

// Export types
export type { Farm, FarmListOptions, FarmListResponse } from './farm'
export type { Organization, OrganizationMember, OrganizationListOptions, OrganizationListResponse, MemberListOptions, MemberListResponse } from './organization'
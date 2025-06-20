import React from 'react'
import { DefaultLayout, DashboardLayout } from '@/components/layouts'
import { CircularProgress, Box } from '@mui/material'

// Loading component for Suspense
const LoadingFallback = () => (
  <Box 
    sx={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '200px' 
    }}
  >
    <CircularProgress />
  </Box>
)

// Helper to wrap lazy components with Suspense
const withSuspense = (Component: React.LazyExoticComponent<any>) => (
  <React.Suspense fallback={<LoadingFallback />}>
    <Component />
  </React.Suspense>
)

// Lazy load components
const NotFound = React.lazy(() => import('@/views/error/NotFound'))
const ServerError = React.lazy(() => import('@/views/error/Error'))
const Farms = React.lazy(() => import('@/farm/Farms'))
const Contacts = React.lazy(() => import('@/contact/Contacts'))
const OrganizationMemberTable = React.lazy(() => import('@/organization/OrganizationMemberTable'))
const ResultList = React.lazy(() => import('@/search/ResultList'))
const MarketPrices = React.lazy(() => import('@/market/MarketPrices'))


export interface RouteConfig {
  path?: string
  element?: React.ReactElement
  children?: RouteConfig[]
  index?: boolean
  meta?: {
    title?: string
    icon?: string
    group?: string
    requiresAuth?: boolean
    menu?: boolean
    showEditSheet?: boolean
    subMenu?: string
    noMenu?: boolean
  }
}


export const publicRoutes: RouteConfig[] = [
  {
    path: '/404',
    element: withSuspense(NotFound),
    meta: { title: 'Not Found' },
  },
  {
    path: '/500',
    element: withSuspense(ServerError),
    meta: { title: 'Server Error' },
  },
  {
    path: '/implicit/callback',
    element: <div>Processing...</div>,
    meta: { requiresAuth: true },
  },
  {
    path: '*',
    element: withSuspense(NotFound),
    meta: { title: 'Farmbase' },
  },
]

export const protectedRoutes: RouteConfig[] = [
  {
    path: '/:organization/dashboards',
    element: <DashboardLayout />,
    meta: {
      title: 'Dashboards',
      group: 'dashboard',
      icon: 'mdi-monitor-dashboard',
      menu: true,
      requiresAuth: true,
    },
    children: [],
  },
  {
    path: '/:organization/farms',
    element: <DefaultLayout />,
    meta: {
      title: 'Farms',
      icon: 'mdi-barn',
      group: 'farms',
      requiresAuth: true,
      menu: true,
      showEditSheet: false,
    },
    children: [
      {
        index: true,
        element: withSuspense(Farms),
        meta: { title: 'List' },
      },
    ],
  },
  {
    path: '/:organization/contacts',
    element: <DefaultLayout />,
    meta: {
      title: 'Contacts',
      icon: 'mdi-account',
      group: 'contacts',
      requiresAuth: true,
      menu: true,
      showEditSheet: false,
    },
    children: [
      {
        index: true,
        element: withSuspense(Contacts),
        meta: { title: 'List' },
      },
    ],
  },
  {
    path: '/:organization/data',
    element: <DefaultLayout />,
    meta: {
      title: 'Data',
      icon: 'mdi-database',
      group: 'data',
      menu: true,
      requiresAuth: true,
    },
    children: [
      {
        path: 'market-prices',
        element: withSuspense(MarketPrices),
        meta: { title: 'Market Prices', subMenu: 'data', group: 'market-prices' },
      },
    ],
  },
  {
    path: '/:organization/settings',
    element: <DefaultLayout />,
    meta: {
      title: 'Settings',
      icon: 'mdi-cog',
      group: 'settings',
      menu: true,
      requiresAuth: true,
    },
    children: [
      {
        path: 'members',
        element: withSuspense(OrganizationMemberTable),
        meta: { title: 'Members', subMenu: 'organization', group: 'organization' },
      },
    ],
  },
  {
    path: '/:organization/search',
    element: <DefaultLayout />,
    meta: {
      title: 'Search',
      icon: 'mdi-view-comfy-outline',
      group: 'search',
      noMenu: true,
      requiresAuth: true,
    },
    children: [
      {
        path: 'results',
        element: withSuspense(ResultList),
        meta: { title: 'Results' },
      },
    ],
  },
]

export const allRoutes: RouteConfig[] = [...protectedRoutes, ...publicRoutes]
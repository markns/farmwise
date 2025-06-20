import React from 'react'
import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Box,
  Collapse,
  Tooltip,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Agriculture as FarmIcon,
  People as ContactIcon,
  Storage as DataIcon,
  Settings as SettingsIcon,
  TrendingUp as MarketIcon,
  Grass as SeedIcon,
  ExpandLess,
  ExpandMore,
} from '@mui/icons-material'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { useAppStore } from '../stores/appStore'

const drawerWidth = 256
const collapsedDrawerWidth = 72

interface MenuItem {
  title: string
  icon: React.ReactNode
  path?: string
  group: string
  children?: MenuItem[]
}

const AppDrawer: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { organization = 'default' } = useParams()
  const toggleDrawer = useAppStore(state => state.toggleDrawer)
  const drawerHovered = useAppStore(state => state.drawerHovered)
  const setDrawerHovered = useAppStore(state => state.setDrawerHovered)
  const [expandedSections, setExpandedSections] = React.useState<Record<string, boolean>>({
    management: true,
    data: true,
  })
  
  // When drawer is collapsed, only expand on hover
  const isExpanded = toggleDrawer || drawerHovered

  const menuItems: MenuItem[] = [
    {
      title: 'Management',
      icon: <DashboardIcon />,
      group: 'management',
      children: [
        {
          title: 'Dashboards',
          icon: <DashboardIcon />,
          path: `/${organization}/dashboards`,
          group: 'dashboards',
        },
        {
          title: 'Farms',
          icon: <FarmIcon />,
          path: `/${organization}/farms`,
          group: 'farms',
        },
        {
          title: 'Contacts',
          icon: <ContactIcon />,
          path: `/${organization}/contacts`,
          group: 'contacts',
        },
      ],
    },
    {
      title: 'Data & Analytics',
      icon: <DataIcon />,
      group: 'data',
      children: [
        {
          title: 'Data Explorer',
          icon: <DataIcon />,
          path: `/${organization}/data`,
          group: 'data-explorer',
        },
        {
          title: 'Market Prices',
          icon: <MarketIcon />,
          path: `/${organization}/data/market-prices`,
          group: 'market-prices',
        },
        {
          title: 'Seed Varieties',
          icon: <SeedIcon />,
          path: `/${organization}/data/seed-varieties`,
          group: 'seed-varieties',
        },
      ],
    },
    {
      title: 'Settings',
      icon: <SettingsIcon />,
      path: `/${organization}/settings`,
      group: 'settings',
    },
  ]

  const handleItemClick = (path: string) => {
    navigate(path)
  }

  const handleSectionToggle = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const isActive = (path?: string) => {
    if (!path) return false
    return location.pathname === path
  }

  const renderMenuItem = (item: MenuItem, level: number = 0) => {
    if (item.children) {
      const isSectionExpanded = expandedSections[item.group]
      
      // In collapsed mode, show only the icon
      if (!isExpanded) {
        return (
          <Tooltip key={item.group} title={item.title} placement="right">
            <ListItemButton
              onClick={() => handleSectionToggle(item.group)}
              sx={{
                minHeight: 48,
                justifyContent: 'center',
                px: 2.5,
                '&:hover': {
                  backgroundColor: 'rgba(25, 118, 210, 0.08)',
                },
              }}
            >
              <ListItemIcon sx={{ 
                minWidth: 0, 
                mr: 0,
                justifyContent: 'center',
                color: '#5f6368' 
              }}>
                {item.icon}
              </ListItemIcon>
            </ListItemButton>
          </Tooltip>
        )
      }
      
      return (
        <React.Fragment key={item.group}>
          <ListItemButton
            onClick={() => handleSectionToggle(item.group)}
            sx={{
              pl: 2 + level * 2,
              py: 1,
              '&:hover': {
                backgroundColor: 'rgba(25, 118, 210, 0.08)',
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40, color: '#5f6368' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.title}
              primaryTypographyProps={{
                fontSize: '14px',
                fontWeight: 500,
                color: '#3c4043',
              }}
            />
            {isSectionExpanded ? <ExpandLess /> : <ExpandMore />}
          </ListItemButton>
          <Collapse in={isSectionExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children.map((child) => renderMenuItem(child, level + 1))}
            </List>
          </Collapse>
        </React.Fragment>
      )
    }

    // For leaf items
    if (!isExpanded) {
      return (
        <Tooltip key={item.group} title={item.title} placement="right">
          <ListItemButton
            onClick={() => item.path && handleItemClick(item.path)}
            sx={{
              minHeight: 48,
              justifyContent: 'center',
              px: 2.5,
              backgroundColor: isActive(item.path) ? 'rgba(25, 118, 210, 0.12)' : 'transparent',
              borderRight: isActive(item.path) ? '3px solid #1976d2' : 'none',
              '&:hover': {
                backgroundColor: isActive(item.path) 
                  ? 'rgba(25, 118, 210, 0.16)' 
                  : 'rgba(25, 118, 210, 0.08)',
              },
            }}
          >
            <ListItemIcon sx={{ 
              minWidth: 0,
              mr: 0,
              justifyContent: 'center',
              color: isActive(item.path) ? '#1976d2' : '#5f6368' 
            }}>
              {item.icon}
            </ListItemIcon>
          </ListItemButton>
        </Tooltip>
      )
    }

    return (
      <ListItemButton
        key={item.group}
        onClick={() => item.path && handleItemClick(item.path)}
        sx={{
          pl: 2 + level * 2,
          py: 1,
          backgroundColor: isActive(item.path) ? 'rgba(25, 118, 210, 0.12)' : 'transparent',
          borderRight: isActive(item.path) ? '3px solid #1976d2' : 'none',
          '&:hover': {
            backgroundColor: isActive(item.path) 
              ? 'rgba(25, 118, 210, 0.16)' 
              : 'rgba(25, 118, 210, 0.08)',
          },
        }}
      >
        <ListItemIcon sx={{ 
          minWidth: 40, 
          color: isActive(item.path) ? '#1976d2' : '#5f6368' 
        }}>
          {item.icon}
        </ListItemIcon>
        <ListItemText 
          primary={item.title}
          primaryTypographyProps={{
            fontSize: '14px',
            fontWeight: isActive(item.path) ? 600 : 400,
            color: isActive(item.path) ? '#1976d2' : '#3c4043',
          }}
        />
      </ListItemButton>
    )
  }

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={true} // Always open, but width changes
      onMouseEnter={() => setDrawerHovered(true)}
      onMouseLeave={() => setDrawerHovered(false)}
      sx={{
        width: isExpanded ? drawerWidth : collapsedDrawerWidth,
        flexShrink: 0,
        transition: 'width 0.2s ease-in-out',
        '& .MuiDrawer-paper': {
          width: isExpanded ? drawerWidth : collapsedDrawerWidth,
          boxSizing: 'border-box',
          backgroundColor: '#fafafa',
          borderRight: '1px solid #e0e0e0',
          transition: 'width 0.2s ease-in-out',
          overflowX: 'hidden',
        },
      }}
    >
      <Toolbar sx={{ 
        minHeight: '64px !important',
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e0e0e0',
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          width: '100%',
          justifyContent: isExpanded ? 'flex-start' : 'center',
        }}>
          {isExpanded ? (
            <Typography 
              variant="h6" 
              noWrap 
              component="div"
              sx={{
                fontWeight: 400,
                fontSize: '22px',
                color: '#3c4043',
              }}
            >
              FarmBase
            </Typography>
          ) : (
            <Tooltip title="FarmBase" placement="right">
              <Box sx={{
                width: 32,
                height: 32,
                backgroundColor: '#1976d2',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '14px',
              }}>
                FB
              </Box>
            </Tooltip>
          )}
        </Box>
      </Toolbar>
      <List sx={{ pt: 1 }}>
        {menuItems.map((item) => renderMenuItem(item))}
      </List>
    </Drawer>
  )
}

export default AppDrawer
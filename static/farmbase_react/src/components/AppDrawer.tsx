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
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Agriculture as FarmIcon,
  People as ContactIcon,
  Storage as DataIcon,
  Settings as SettingsIcon,
  ExpandLess,
  ExpandMore,
} from '@mui/icons-material'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { useAppStore } from '../stores/appStore'

const drawerWidth = 256

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
  const [expandedSections, setExpandedSections] = React.useState<Record<string, boolean>>({
    management: true,
    data: true,
  })

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
      const isExpanded = expandedSections[item.group]
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
            {isExpanded ? <ExpandLess /> : <ExpandMore />}
          </ListItemButton>
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children.map((child) => renderMenuItem(child, level + 1))}
            </List>
          </Collapse>
        </React.Fragment>
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
      open={toggleDrawer}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: '#fafafa',
          borderRight: '1px solid #e0e0e0',
        },
      }}
    >
      <Toolbar sx={{ 
        minHeight: '64px !important',
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e0e0e0',
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
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
        </Box>
      </Toolbar>
      <List sx={{ pt: 1 }}>
        {menuItems.map((item) => renderMenuItem(item))}
      </List>
    </Drawer>
  )
}

export default AppDrawer
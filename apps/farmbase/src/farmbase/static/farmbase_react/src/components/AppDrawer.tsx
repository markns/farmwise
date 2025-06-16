import React from 'react'
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Divider,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Agriculture as FarmIcon,
  People as ContactIcon,
  Storage as DataIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import { useNavigate, useParams } from 'react-router-dom'
import { useAppStore } from '../stores/appStore'

const drawerWidth = 200

interface MenuItem {
  title: string
  icon: React.ReactNode
  path: string
  group: string
}

const AppDrawer: React.FC = () => {
  const navigate = useNavigate()
  const { organization = 'default' } = useParams()
  const toggleDrawer = useAppStore(state => state.toggleDrawer)

  const menuItems: MenuItem[] = [
    {
      title: 'Dashboards',
      icon: <DashboardIcon />,
      path: `/${organization}/dashboards`,
      group: 'dashboard',
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
    {
      title: 'Data',
      icon: <DataIcon />,
      path: `/${organization}/data`,
      group: 'data',
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
        },
      }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Navigation
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.group} disablePadding>
            <ListItemButton onClick={() => handleItemClick(item.path)}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.title} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  )
}

export default AppDrawer
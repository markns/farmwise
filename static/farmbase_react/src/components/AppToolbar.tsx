import React from 'react'
import {AppBar,  Box, IconButton, Menu, MenuItem, Toolbar, Typography,} from '@mui/material'
import {AccountCircle, ExitToApp, Menu as MenuIcon,} from '@mui/icons-material'
// import { useNavigate } from 'react-router-dom'
import {useAppStore} from '../stores/appStore'
import {useLogoutFunction, withAuthInfo, WithAuthInfoProps} from "@propelauth/react";


// This version expects WithAuthInfoProps from PropelAuth
const AppToolbar: React.FC<WithAuthInfoProps> = (auth) => {
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null)
    const logoutFunction = useLogoutFunction()
    const toggleDrawer = useAppStore(state => state.toggleDrawer)
    const setDrawerOpen = useAppStore(state => state.setDrawerOpen)

    const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget)
    }

    const handleClose = () => {
        setAnchorEl(null)
    }

    const handleLogout = () => {
        // props. // <-- optional: if you're using PropelAuth's logout
        logoutFunction(true)
        handleClose()
    }

    const handleDrawerToggle = () => {
        setDrawerOpen(!toggleDrawer)
    }

    // const avatarUrl = getUserAvatarUrl(auth.user?.email || '')

    return (
        <AppBar position="static" sx={{zIndex: (theme) => theme.zIndex.drawer + 1}}>
            <Toolbar>
                <IconButton
                    color="inherit"
                    aria-label="open drawer"
                    onClick={handleDrawerToggle}
                    edge="start"
                    sx={{mr: 2}}
                >
                    <MenuIcon/>
                </IconButton>

                <Typography variant="h6" component="div" sx={{flexGrow: 1}}>
                    FarmBase
                </Typography>

                {auth.isLoggedIn && auth.user && (
                    <Box sx={{display: 'flex', alignItems: 'center'}}>
                        <Typography variant="body2" sx={{mr: 2}}>
                            {auth.user.email}
                        </Typography>
                        <IconButton
                            size="large"
                            aria-label="account of current user"
                            aria-controls="menu-appbar"
                            aria-haspopup="true"
                            onClick={handleMenu}
                            color="inherit"
                        >
                            {/*{avatarUrl ? (*/}
                            {/*    <Avatar src={avatarUrl} sx={{width: 32, height: 32}}/>*/}
                            {/*) : (*/}
                            <AccountCircle/>
                            {/*)}*/}
                        </IconButton>
                        <Menu
                            id="menu-appbar"
                            anchorEl={anchorEl}
                            anchorOrigin={{
                                vertical: 'top',
                                horizontal: 'right',
                            }}
                            keepMounted
                            transformOrigin={{
                                vertical: 'top',
                                horizontal: 'right',
                            }}
                            open={Boolean(anchorEl)}
                            onClose={handleClose}
                        >
                            <MenuItem onClick={handleLogout}>
                                <ExitToApp sx={{mr: 1}}/>
                                Logout
                            </MenuItem>
                        </Menu>
                    </Box>
                )}
            </Toolbar>
        </AppBar>
    )
}

// Wrap with PropelAuth
export default withAuthInfo(AppToolbar)
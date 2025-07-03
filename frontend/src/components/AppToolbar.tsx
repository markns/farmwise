import React from 'react'
import {
    alpha,
    AppBar,
    Box,
    Breadcrumbs,
    IconButton,
    InputBase,
    Link,
    Menu,
    MenuItem,
    Toolbar,
    Typography
} from '@mui/material'
import {
    AccountCircle,
    ExitToApp,
    Help,
    Menu as MenuIcon,
    Notifications,
    Search as SearchIcon
} from '@mui/icons-material'
import {useLocation, useNavigate, useParams} from 'react-router-dom'
import {useAppStore} from '../stores/appStore'
import {useLogoutFunction, withAuthInfo, WithAuthInfoProps} from "@propelauth/react"
import {config} from "@/config/env.ts";


// This version expects WithAuthInfoProps from PropelAuth
const AppToolbar: React.FC<WithAuthInfoProps> = (auth) => {
    const navigate = useNavigate()
    const location = useLocation()
    const {organization = 'default'} = useParams()
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

    // Generate breadcrumbs based on current path
    const generateBreadcrumbs = () => {
        const pathSegments = location.pathname.split('/').filter(segment => segment)
        const breadcrumbs = []

        if (pathSegments.length > 1) {
            breadcrumbs.push({
                label: organization.charAt(0).toUpperCase() + organization.slice(1),
                path: `/${organization}`
            })

            if (pathSegments[1]) {
                const currentPage = pathSegments[1].charAt(0).toUpperCase() + pathSegments[1].slice(1)
                breadcrumbs.push({
                    label: currentPage,
                    path: location.pathname
                })
            }
        }

        return breadcrumbs
    }

    const breadcrumbs = generateBreadcrumbs()

    // const avatarUrl = getUserAvatarUrl(auth.user?.email || '')

    return (
        <>
            <AppBar
                position="static"
                sx={{
                    zIndex: (theme) => theme.zIndex.drawer + 1,
                    backgroundColor: '#ffffff',
                    color: '#3c4043',
                    boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
                }}
            >
                <Toolbar sx={{minHeight: '64px !important', px: 2}}>
                    <IconButton
                        color="inherit"
                        aria-label="open drawer"
                        onClick={handleDrawerToggle}
                        edge="start"
                        sx={{
                            mr: 2,
                            color: '#5f6368',
                            '&:hover': {
                                backgroundColor: 'rgba(60,64,67,0.08)',
                            }
                        }}
                    >
                        <MenuIcon/>
                    </IconButton>

                    {/* Search Bar */}
                    <Box
                        sx={{
                            position: 'relative',
                            borderRadius: '24px',
                            backgroundColor: alpha('#5f6368', 0.08),
                            '&:hover': {
                                backgroundColor: alpha('#5f6368', 0.12),
                            },
                            marginLeft: 0,
                            width: '100%',
                            maxWidth: '480px',
                            mr: 3,
                        }}
                    >
                        <Box
                            sx={{
                                padding: (theme) => theme.spacing(0, 2),
                                height: '100%',
                                position: 'absolute',
                                pointerEvents: 'none',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}
                        >
                            <SearchIcon sx={{color: '#5f6368'}}/>
                        </Box>
                        <InputBase
                            placeholder="Search resources..."
                            sx={{
                                color: '#3c4043',
                                '& .MuiInputBase-input': {
                                    padding: '8px 8px 8px 0',
                                    paddingLeft: 'calc(1em + 32px)',
                                    width: '100%',
                                    fontSize: '14px',
                                },
                            }}
                        />
                    </Box>

                    <Box sx={{flexGrow: 1}}/>

                    {/* Right side icons */}
                    <Box sx={{display: 'flex', alignItems: 'center'}}>
                        <IconButton
                            component="a"
                            href={`${config.apiBaseUrl}/docs`}
                            target="_blank"
                            rel="noopener noreferrer"
                            sx={{
                                color: '#5f6368',
                                '&:hover': {
                                    backgroundColor: 'rgba(60,64,67,0.08)',
                                }
                            }}
                        >
                            <Help/>
                        </IconButton>
                        <IconButton
                            sx={{
                                color: '#5f6368',
                                '&:hover': {
                                    backgroundColor: 'rgba(60,64,67,0.08)',
                                }
                            }}
                        >
                            <Notifications/>
                        </IconButton>

                        {auth.isLoggedIn && auth.user && (
                            <IconButton
                                size="large"
                                aria-label="account of current user"
                                aria-controls="menu-appbar"
                                aria-haspopup="true"
                                onClick={handleMenu}
                                sx={{
                                    ml: 1,
                                    color: '#5f6368',
                                    '&:hover': {
                                        backgroundColor: 'rgba(60,64,67,0.08)',
                                    }
                                }}
                            >
                                <AccountCircle sx={{fontSize: 32}}/>
                            </IconButton>
                        )}

                        <Menu
                            id="menu-appbar"
                            anchorEl={anchorEl}
                            anchorOrigin={{
                                vertical: 'bottom',
                                horizontal: 'right',
                            }}
                            keepMounted
                            transformOrigin={{
                                vertical: 'top',
                                horizontal: 'right',
                            }}
                            open={Boolean(anchorEl)}
                            onClose={handleClose}
                            sx={{
                                '& .MuiPaper-root': {
                                    borderRadius: '8px',
                                    minWidth: '200px',
                                    boxShadow: '0 4px 6px rgba(32,33,36,0.28)',
                                }
                            }}
                        >
                            <Box sx={{px: 2, py: 1, borderBottom: '1px solid #e0e0e0'}}>
                                <Typography variant="body2" sx={{fontWeight: 500, color: '#3c4043'}}>
                                    {auth.user?.email}
                                </Typography>
                            </Box>
                            <MenuItem
                                onClick={handleLogout}
                                sx={{
                                    py: 1.5,
                                    '&:hover': {
                                        backgroundColor: 'rgba(60,64,67,0.08)',
                                    }
                                }}
                            >
                                <ExitToApp sx={{mr: 2, color: '#5f6368'}}/>
                                <Typography variant="body2">Sign out</Typography>
                            </MenuItem>
                        </Menu>
                    </Box>
                </Toolbar>
            </AppBar>

            {/* Breadcrumb Bar */}
            {breadcrumbs.length > 0 && (
                <Box
                    sx={{
                        backgroundColor: '#ffffff',
                        borderBottom: '1px solid #e0e0e0',
                        px: 3,
                        py: 1,
                        zIndex: (theme) => theme.zIndex.drawer + 1,
                    }}
                >
                    <Breadcrumbs
                        aria-label="breadcrumb"
                        sx={{
                            '& .MuiBreadcrumbs-separator': {
                                color: '#5f6368',
                            }
                        }}
                    >
                        {breadcrumbs.map((crumb, index) => (
                            index === breadcrumbs.length - 1 ? (
                                <Typography
                                    key={crumb.path}
                                    color="#3c4043"
                                    sx={{fontSize: '14px', fontWeight: 500}}
                                >
                                    {crumb.label}
                                </Typography>
                            ) : (
                                <Link
                                    key={crumb.path}
                                    color="#1976d2"
                                    href="#"
                                    onClick={(e) => {
                                        e.preventDefault()
                                        navigate(crumb.path)
                                    }}
                                    sx={{
                                        fontSize: '14px',
                                        textDecoration: 'none',
                                        '&:hover': {
                                            textDecoration: 'underline',
                                        }
                                    }}
                                >
                                    {crumb.label}
                                </Link>
                            )
                        ))}
                    </Breadcrumbs>
                </Box>
            )}
        </>
    )
}

// Wrap with PropelAuth
export default withAuthInfo(AppToolbar)
import React, { useEffect } from 'react'
import {
  Typography,
  Box,
  Button,
  Chip,
  Tooltip,
  Avatar,
} from '@mui/material'
import {
  DataGrid,
  GridColDef,
  GridActionsCellItem,
  GridToolbar,
  GridRenderCellParams,
} from '@mui/x-data-grid'
import {
  Add as AddIcon,
  Chat as ChatIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  FilterAlt as FilterIcon,
  Agriculture as FarmerIcon,
  School as ExtensionOfficerIcon,
  Person as PersonIcon,
  Psychology as MemoryIcon,
} from '@mui/icons-material'
import { useNavigate, useParams } from 'react-router-dom'
import { useContactStore, type Contact } from '@/stores/contactStore'
import ContactPopover from './ContactPopover'
import ChatDrawer from './ChatDrawer'
import ContactCreateEditDialog from './ContactCreateEditDialog'
import ContactFilterDialog from './ContactFilterDialog'

const TableInstance: React.FC = () => {
  const navigate = useNavigate()
  const { organization = 'default' } = useParams()
  
  const {
    instanceTable,
    getAllInstances,
    createEditShow,
    chatShow,
    removeShow,
    filterShow,
    memoriesShow,
    updateInstanceTableOptions,
  } = useContactStore()

  useEffect(() => {
    getAllInstances()
  }, [getAllInstances])

  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map(word => word.charAt(0).toUpperCase())
      .slice(0, 2)
      .join('')
  }

  const getAvatarColor = (name: string): string => {
    const colors = [
      '#e3f2fd', '#f3e5f5', '#e8f5e8', '#fff3e0', '#fce4ec',
      '#e0f2f1', '#f1f8e9', '#e8eaf6', '#fff8e1', '#fde7e7'
    ]
    const index = name.charCodeAt(0) % colors.length
    return colors[index]
  }

  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'Unknown'
    try {
      return new Date(dateString).toLocaleDateString()
    } catch {
      return 'Invalid date'
    }
  }

  const calculateAge = (dateOfBirth?: string, estimatedAge?: number): string => {
    if (estimatedAge) return `~${estimatedAge} years`
    if (!dateOfBirth) return 'Unknown'
    
    try {
      const birth = new Date(dateOfBirth)
      const today = new Date()
      const age = today.getFullYear() - birth.getFullYear()
      const monthDiff = today.getMonth() - birth.getMonth()
      
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        return `${age - 1} years`
      }
      return `${age} years`
    } catch {
      return 'Unknown'
    }
  }

  const getRoleIcon = (role?: string) => {
    if (!role) return <PersonIcon sx={{ color: '#9e9e9e' }} />
    
    switch (role.toLowerCase()) {
      case 'farmer':
        return <FarmerIcon sx={{ color: '#4caf50' }} />
      case 'extension_officer':
      case 'extension officer':
        return <ExtensionOfficerIcon sx={{ color: '#2196f3' }} />
      default:
        return <PersonIcon sx={{ color: '#9e9e9e' }} />
    }
  }

  const getRoleTooltip = (role?: string): string => {
    if (!role) return 'No role specified'
    
    switch (role.toLowerCase()) {
      case 'farmer':
        return 'Farmer'
      case 'extension_officer':
      case 'extension officer':
        return 'Extension Officer'
      default:
        return role.charAt(0).toUpperCase() + role.slice(1)
    }
  }

  const handleEdit = (contact: Contact) => {
    createEditShow(contact)
  }

  const handleChat = (contact: Contact) => {
    chatShow(contact)
  }

  const handleDelete = (contact: Contact) => {
    removeShow(contact)
  }

  const handleMemories = (contact: Contact) => {
    memoriesShow(contact)
  }

  const renderContactCell = (params: GridRenderCellParams) => {
    const contact = params.row as Contact
    return (
      <ContactPopover contact={contact}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar
            sx={{
              width: 32,
              height: 32,
              bgcolor: getAvatarColor(contact.name),
              color: 'text.primary',
              fontSize: '0.875rem',
            }}
          >
            {getInitials(contact.name)}
          </Avatar>
          <Typography variant="body2" fontWeight="medium">
            {contact.name}
          </Typography>
        </Box>
      </ContactPopover>
    )
  }

  const renderProductInterestsCell = (params: GridRenderCellParams) => {
    const interests = params.value
    if (!interests) return null

    const chips: React.ReactNode[] = []
    
    // Crops (green)
    if (interests.crops?.length > 0) {
      interests.crops.forEach((crop: string, index: number) => (
        chips.push(
          <Chip
            key={`crop-${index}`}
            label={crop}
            size="small"
            sx={{
              bgcolor: '#c8e6c9',
              color: '#2e7d32',
              fontSize: '0.75rem',
              height: 20,
              margin: 0.25,
            }}
          />
        )
      ))
    }
    
    // Livestock (brown)
    if (interests.livestock?.length > 0) {
      interests.livestock.forEach((livestock: string, index: number) => (
        chips.push(
          <Chip
            key={`livestock-${index}`}
            label={livestock}
            size="small"
            sx={{
              bgcolor: '#d7ccc8',
              color: '#5d4037',
              fontSize: '0.75rem',
              height: 20,
              margin: 0.25,
            }}
          />
        )
      ))
    }
    
    // Other (blue)
    if (interests.other?.length > 0) {
      interests.other.forEach((other: string, index: number) => (
        chips.push(
          <Chip
            key={`other-${index}`}
            label={other}
            size="small"
            sx={{
              bgcolor: '#bbdefb',
              color: '#1976d2',
              fontSize: '0.75rem',
              height: 20,
              margin: 0.25,
            }}
          />
        )
      ))
    }

    return (
      <Box sx={{ display: 'flex', flexWrap: 'wrap', maxWidth: 200 }}>
        {chips}
      </Box>
    )
  }

  const renderFarmsCell = (params: GridRenderCellParams) => {
    const farms = params.value
    if (!farms || farms.length === 0) {
      return (
        <Typography variant="body2" color="text.secondary">
          No farms
        </Typography>
      )
    }

    return (
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
        {farms.map((farm: any, index: number) => (
          <Chip
            key={index}
            label={farm.name || farm.farm_name}
            size="small"
            variant="outlined"
            onClick={() => navigate(`/${organization}/farms`, { 
              state: { farm_id: farm.id } 
            })}
            sx={{ cursor: 'pointer', fontSize: '0.75rem', height: 20 }}
          />
        ))}
      </Box>
    )
  }

  const renderDateCell = (params: GridRenderCellParams) => {
    const date = formatDate(params.value)
    const tooltip = params.value ? new Date(params.value).toLocaleString() : 'No date available'
    
    return (
      <Tooltip title={tooltip}>
        <Typography variant="body2">
          {date}
        </Typography>
      </Tooltip>
    )
  }

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Contact',
      width: 200,
      renderCell: renderContactCell,
    },
    {
      field: 'phone_number',
      headerName: 'Phone',
      width: 130,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value || 'No phone'}
        </Typography>
      ),
    },
    {
      field: 'gender',
      headerName: 'Gender',
      width: 80,
      align: 'center',
      headerAlign: 'center',
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value ? params.value.charAt(0).toUpperCase() : ''}
        </Typography>
      ),
    },
    {
      field: 'role',
      headerName: 'Role',
      width: 80,
      align: 'center',
      headerAlign: 'center',
      renderCell: (params) => (
        <Tooltip title={getRoleTooltip(params.value)} placement="top">
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            height: '100%',
          }}>
            {getRoleIcon(params.value)}
          </Box>
        </Tooltip>
      ),
    },
    {
      field: 'date_of_birth',
      headerName: 'Date of Birth',
      width: 130,
      renderCell: renderDateCell,
    },
    {
      field: 'age',
      headerName: 'Age',
      width: 100,
      valueGetter: (_, row) => calculateAge(row.date_of_birth, row.estimated_age),
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value}
        </Typography>
      ),
    },
    {
      field: 'experience',
      headerName: 'Experience',
      width: 110,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value ? `${params.value} years` : 'Unknown'}
        </Typography>
      ),
    },
    {
      field: 'product_interests',
      headerName: 'Product Interests',
      width: 220,
      sortable: false,
      renderCell: renderProductInterestsCell,
    },
    {
      field: 'farms',
      headerName: 'Farms',
      width: 150,
      sortable: false,
      renderCell: renderFarmsCell,
    },
    {
      field: 'actions',
      type: 'actions',
      headerName: '',
      width: 150,
      getActions: (params) => [
        <GridActionsCellItem
          key="edit"
          icon={
            <Tooltip title="Edit Contact">
              <EditIcon />
            </Tooltip>
          }
          label="Edit Contact"
          onClick={() => handleEdit(params.row)}
          color="primary"
        />,
        <GridActionsCellItem
          key="chat"
          icon={
            <Tooltip title="View Chat History">
              <ChatIcon />
            </Tooltip>
          }
          label="View Chat"
          onClick={() => handleChat(params.row)}
          color="primary"
        />,
        <GridActionsCellItem
          key="memories"
          icon={
            <Tooltip title="View Memories">
              <MemoryIcon />
            </Tooltip>
          }
          label="View Memories"
          onClick={() => handleMemories(params.row)}
          color="primary"
        />,
        <GridActionsCellItem
          key="delete"
          icon={
            <Tooltip title="Delete Contact">
              <DeleteIcon />
            </Tooltip>
          }
          label="Delete Contact"
          onClick={() => handleDelete(params.row)}
          color="error"
        />,
      ],
    },
  ]

  const handlePaginationModelChange = (model: { page: number; pageSize: number }) => {
    updateInstanceTableOptions({
      page: model.page + 1, // DataGrid uses 0-based indexing
      itemsPerPage: model.pageSize,
    })
  }

  const handleSortModelChange = (model: readonly any[]) => {
    if (model.length > 0) {
      updateInstanceTableOptions({
        sortBy: [model[0].field],
        descending: [model[0].sort === 'desc'],
      })
    }
  }

  return (
    <Box sx={{ 
      p: 3, 
      backgroundColor: '#f8f9fa', 
      minHeight: '100%',
      width: '100%',
      maxWidth: 'none',
    }}>
      <ChatDrawer />
      <ContactCreateEditDialog />
      <ContactFilterDialog />
      
      {/* Header */}
      <Box sx={{ mb: 3, width: '100%' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography 
            variant="h4" 
            component="h1"
            sx={{ 
              fontWeight: 400,
              fontSize: '28px',
              color: '#3c4043',
              fontFamily: '"Google Sans", Roboto, sans-serif',
            }}
          >
            Contacts
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={() => filterShow()}
              sx={{
                color: '#1976d2',
                borderColor: '#1976d2',
                textTransform: 'none',
                fontWeight: 500,
                fontSize: '14px',
                '&:hover': {
                  borderColor: '#1565c0',
                  backgroundColor: 'rgba(25, 118, 210, 0.04)',
                },
              }}
            >
              FILTERS
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => createEditShow()}
              sx={{
                backgroundColor: '#1976d2',
                boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
                '&:hover': {
                  backgroundColor: '#1565c0',
                  boxShadow: '0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)',
                },
                textTransform: 'none',
                fontWeight: 500,
                fontSize: '14px',
                borderRadius: '4px',
                px: 3,
                py: 1,
              }}
            >
              CREATE CONTACT
            </Button>
          </Box>
        </Box>
        <Typography 
          variant="body2" 
          sx={{ 
            color: '#5f6368',
            fontSize: '14px',
            mb: 2,
          }}
        >
          Manage your contacts and track relationships with farmers and stakeholders
        </Typography>
      </Box>

      {/* Data Table */}
      <Box
        sx={{
          backgroundColor: '#ffffff',
          borderRadius: '8px',
          boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
          overflow: 'hidden',
          width: '100%',
        }}
      >
          <DataGrid
            rows={instanceTable.rows.items}
            columns={columns}
            loading={instanceTable.loading}
            pagination
            paginationMode="server"
            sortingMode="server"
            rowCount={instanceTable.rows.total || 0}
            columnVisibilityModel={{
              date_of_birth: false, // Hide date of birth by default
            }}
            paginationModel={{
              page: instanceTable.options.page - 1, // DataGrid uses 0-based indexing
              pageSize: instanceTable.options.itemsPerPage,
            }}
            onPaginationModelChange={handlePaginationModelChange}
            onSortModelChange={handleSortModelChange}
            pageSizeOptions={[10, 25, 50, 100]}
            disableRowSelectionOnClick
            slots={{
              toolbar: GridToolbar,
            }}
            slotProps={{
              toolbar: {
                showQuickFilter: true,
                quickFilterProps: { debounceMs: 500 },
              },
            }}
            onFilterModelChange={(model) => {
              const quickFilterValue = model.quickFilterValues?.[0] || ''
              updateInstanceTableOptions({ q: quickFilterValue })
            }}
            sx={{
              border: 'none',
              '& .MuiDataGrid-main': {
                '& .MuiDataGrid-columnHeaders': {
                  backgroundColor: '#f8f9fa',
                  borderBottom: '1px solid #e0e0e0',
                  fontSize: '14px',
                  fontWeight: 500,
                  color: '#3c4043',
                  '& .MuiDataGrid-columnHeaderTitle': {
                    fontWeight: 500,
                  },
                },
                '& .MuiDataGrid-cell': {
                  borderBottom: '1px solid #f0f0f0',
                  fontSize: '14px',
                  color: '#3c4043',
                  display: 'flex',
                  alignItems: 'center',
                  '&:focus': {
                    outline: 'none',
                  },
                },
                '& .MuiDataGrid-row': {
                  '&:hover': {
                    backgroundColor: '#f8f9fa',
                  },
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(25, 118, 210, 0.08)',
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.12)',
                    },
                  },
                },
              },
              '& .MuiDataGrid-toolbarContainer': {
                padding: '16px',
                borderBottom: '1px solid #e0e0e0',
                '& .MuiButton-root': {
                  color: '#5f6368',
                  fontSize: '14px',
                  textTransform: 'none',
                },
                '& .MuiInputBase-root': {
                  fontSize: '14px',
                },
              },
              '& .MuiDataGrid-footerContainer': {
                borderTop: '1px solid #e0e0e0',
                backgroundColor: '#fafafa',
                '& .MuiTablePagination-root': {
                  fontSize: '14px',
                  color: '#5f6368',
                },
              },
              minHeight: 500,
            }}
          />
      </Box>
    </Box>
  )
}

export default TableInstance
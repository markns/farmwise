import React, { useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Button,
  Chip,
  Tooltip,
  Card,
  CardContent,
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

  const handleEdit = (contact: Contact) => {
    createEditShow(contact)
  }

  const handleChat = (contact: Contact) => {
    chatShow(contact)
  }

  const handleDelete = (contact: Contact) => {
    removeShow(contact)
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
      width: 100,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value || 'Not specified'}
        </Typography>
      ),
    },
    {
      field: 'role',
      headerName: 'Role',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value || 'No role'}
        </Typography>
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
      width: 120,
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
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <ChatDrawer />
      <ContactCreateEditDialog />
      <ContactFilterDialog />
      
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Contacts
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={() => filterShow()}
          >
            Filters
          </Button>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => createEditShow()}
          >
            New Contact
          </Button>
        </Box>
      </Box>

      {/* Data Table */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <DataGrid
            rows={instanceTable.rows.items}
            columns={columns}
            loading={instanceTable.loading}
            pagination
            paginationMode="server"
            sortingMode="server"
            rowCount={instanceTable.rows.total || 0}
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
              '& .MuiDataGrid-cell': {
                borderBottom: '1px solid rgba(224, 224, 224, 1)',
                display: 'flex',
                alignItems: 'center',
              },
              '& .MuiDataGrid-columnHeaders': {
                backgroundColor: 'rgba(0, 0, 0, 0.04)',
              },
              '& .MuiDataGrid-cell--textLeft': {
                justifyContent: 'flex-start',
              },
              '& .MuiDataGrid-cell--textCenter': {
                justifyContent: 'center',
              },
              '& .MuiDataGrid-cell--textRight': {
                justifyContent: 'flex-end',
              },
              minHeight: 400,
            }}
          />
        </CardContent>
      </Card>
    </Container>
  )
}

export default TableInstance
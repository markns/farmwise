import React, {useEffect} from 'react'
import {Box, Button, Tooltip, Typography,} from '@mui/material'
import {DataGrid, GridActionsCellItem, GridColDef, GridToolbar,} from '@mui/x-data-grid'
import {Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon, Note as NoteIcon,} from '@mui/icons-material'
import {type Contact, FarmStoreProvider, useFarmStore, type FarmWithContacts} from '@/stores/farmStore'
import {withApiClient, type ApiClient} from '@/api/client'
import LocationPopover from './LocationPopover'
import ContactPopover from './ContactPopover'
import NotesDrawer from './NotesDrawer'
import FarmCreateEditDialog from './FarmCreateEditDialog'
import FarmDeleteDialog from './FarmDeleteDialog'

interface FarmsProps {
    apiClient: ApiClient
}

// Inner component that uses the store
const FarmsContent: React.FC = () => {
    const {
        table,
        getAll,
        createEditShow,
        showNotes,
        removeShow,
        updateTableOptions,
    } = useFarmStore()

    useEffect(() => {
        getAll()
    }, [getAll])

    const getContactRoleColor = (role: string): 'success' | 'info' | 'warning' | 'default' => {
        switch (role?.toLowerCase()) {
            case 'owner':
                return 'success'
            case 'worker':
                return 'info'
            case 'advisor':
                return 'warning'
            default:
                return 'default'
        }
    }

    const handleShowNotes = (farm: FarmWithContacts) => {
        showNotes(farm)
    }

    const handleEdit = (farm: FarmWithContacts) => {
        createEditShow(farm)
    }

    const handleDelete = (farm: FarmWithContacts) => {
        removeShow(farm)
    }

    const columns: GridColDef[] = [
        {
            field: 'farm_name',
            headerName: 'Farm Name',
            width: 250,
            renderCell: (params) => (
                <Typography variant="body2" fontWeight="medium">
                    {params.value}
                </Typography>
            ),
        },
        {
            field: 'location',
            headerName: 'Location',
            width: 200,
            sortable: false,
            renderCell: (params) => {
                if (params.value) {
                    return (
                        <LocationPopover
                            location={params.value}
                            farmName={params.row.farm_name}
                        />
                    )
                }
                return (
                    <Typography variant="body2" color="text.secondary">
                        No location
                    </Typography>
                )
            },
        },
        {
            field: 'contacts',
            headerName: 'Contacts',
            width: 400,
            sortable: false,
            renderCell: (params) => {
                const contacts = params.value as Contact[]
                if (contacts && contacts.length > 0) {
                    return (
                        <Box sx={{display: 'flex', flexWrap: 'wrap', gap: 0.5}}>
                            {contacts.map((contact) => (
                                <ContactPopover
                                    key={contact.id}
                                    contact={contact}
                                    chipColor={getContactRoleColor(contact.role)}
                                />
                            ))}
                        </Box>
                    )
                }
                return (
                    <Typography variant="body2" color="text.secondary">
                        No contacts
                    </Typography>
                )
            },
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
                        <Tooltip title="Edit Farm">
                            <EditIcon/>
                        </Tooltip>
                    }
                    label="Edit Farm"
                    onClick={() => handleEdit(params.row)}
                    color="primary"
                />,
                <GridActionsCellItem
                    key="notes"
                    icon={
                        <Tooltip title="View Notes">
                            <NoteIcon/>
                        </Tooltip>
                    }
                    label="View Notes"
                    onClick={() => handleShowNotes(params.row)}
                    color="primary"
                />,
                <GridActionsCellItem
                    key="delete"
                    icon={
                        <Tooltip title="Delete Farm">
                            <DeleteIcon/>
                        </Tooltip>
                    }
                    label="Delete Farm"
                    onClick={() => handleDelete(params.row)}
                    color="error"
                />,
            ],
        },
    ]

    const handlePaginationModelChange = (model: { page: number; pageSize: number }) => {
        updateTableOptions({
            page: model.page + 1, // DataGrid uses 0-based indexing
            itemsPerPage: model.pageSize,
        })
    }

    const handleSortModelChange = (model: readonly any[]) => {
        if (model.length > 0) {
            updateTableOptions({
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
            <NotesDrawer/>
            <FarmCreateEditDialog/>
            <FarmDeleteDialog/>

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
                        Farms
                    </Typography>
                    <Button
                        variant="contained"
                        startIcon={<AddIcon/>}
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
                        CREATE FARM
                    </Button>
                </Box>
                <Typography 
                    variant="body2" 
                    sx={{ 
                        color: '#5f6368',
                        fontSize: '14px',
                        mb: 2,
                    }}
                >
                    Manage your farm resources and track agricultural operations
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
                    rows={table.rows.items}
                    columns={columns}
                    loading={table.loading}
                    pagination
                    paginationMode="server"
                    sortingMode="server"
                    rowCount={table.rows.total || 0}
                    paginationModel={{
                        page: table.options.page - 1, // DataGrid uses 0-based indexing
                        pageSize: table.options.itemsPerPage,
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
                            quickFilterProps: {debounceMs: 500},
                        },
                    }}
                    onFilterModelChange={(model) => {
                        const quickFilterValue = model.quickFilterValues?.[0] || ''
                        updateTableOptions({q: quickFilterValue})
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

// Main component that provides the store
const Farms: React.FC<FarmsProps> = ({apiClient}) => {
    return (
        <FarmStoreProvider apiClient={apiClient}>
            <FarmsContent />
        </FarmStoreProvider>
    )
}

export default withApiClient(Farms)
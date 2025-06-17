import React, {useEffect} from 'react'
import {Box, Button, Card, CardContent, Chip, Container, Tooltip, Typography,} from '@mui/material'
import {DataGrid, GridActionsCellItem, GridColDef, GridToolbar,} from '@mui/x-data-grid'
import {Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon, Note as NoteIcon,} from '@mui/icons-material'
import {useNavigate, useParams} from 'react-router-dom'
import {type Contact, FarmStoreProvider, useFarmStore, type FarmWithContacts} from '@/stores/farmStore'
import {withApiClient, type ApiClient} from '@/api/client'
import LocationPopover from './LocationPopover'
import NotesDrawer from './NotesDrawer'
import FarmCreateEditDialog from './FarmCreateEditDialog'
import FarmDeleteDialog from './FarmDeleteDialog'

interface FarmsProps {
    apiClient: ApiClient
}

// Inner component that uses the store
const FarmsContent: React.FC = () => {
    const navigate = useNavigate()
    const {organization = 'default'} = useParams()
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

    const navigateToContact = (contactId: string) => {
        navigate(`/${organization}/contacts`, {
            state: {contact_id: contactId}
        })
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
                                <Chip
                                    key={contact.id}
                                    label={contact.name}
                                    size="small"
                                    color={getContactRoleColor(contact.role)}
                                    onClick={() => navigateToContact(contact.id)}
                                    sx={{cursor: 'pointer', margin: 0.25}}
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
        <Container maxWidth="xl" sx={{mt: 4, mb: 4}}>
            <NotesDrawer/>
            <FarmCreateEditDialog/>
            <FarmDeleteDialog/>

            {/* Header */}
            <Box sx={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3}}>
                <Typography variant="h4" component="h1">
                    Farms
                </Typography>
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AddIcon/>}
                    onClick={() => createEditShow()}
                >
                    New Farm
                </Button>
            </Box>

            {/* Data Table */}
            <Card>
                <CardContent sx={{p: 0}}>
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
                            '& .MuiDataGrid-cell': {
                                borderBottom: '1px solid rgba(224, 224, 224, 1)',
                            },
                            '& .MuiDataGrid-columnHeaders': {
                                backgroundColor: 'rgba(0, 0, 0, 0.04)',
                            },
                            minHeight: 400,
                        }}
                    />
                </CardContent>
            </Card>
        </Container>
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
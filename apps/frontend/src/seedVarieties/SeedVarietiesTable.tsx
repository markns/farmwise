import React, { useEffect, useState } from 'react'
import {
  Typography,
  Box,
  Chip,
  Popover,
} from '@mui/material'
import {
  DataGrid,
  GridColDef,
  GridToolbar,
  GridRenderCellParams,
} from '@mui/x-data-grid'
import { useSeedVarietiesStore, type CropVariety } from '@/stores/seedVarietiesStore'

const SeedVarietiesTable: React.FC = () => {
  const store = useSeedVarietiesStore()
  const {
    cropVarietiesData,
    instanceTable,
    loadCropVarieties,
    updateInstanceTableOptions,
  } = store()

  const { options } = instanceTable
  const [descriptionPopover, setDescriptionPopover] = useState<{
    anchorEl: HTMLElement | null
    content: string
  }>({ anchorEl: null, content: '' })

  useEffect(() => {
    if (!cropVarietiesData) {
      loadCropVarieties()
    }
  }, [loadCropVarieties, cropVarietiesData])

  const handleDescriptionMouseEnter = (event: React.MouseEvent<HTMLElement>, description: string) => {
    setDescriptionPopover({
      anchorEl: event.currentTarget,
      content: description
    })
  }

  const handleDescriptionMouseLeave = () => {
    setDescriptionPopover({ anchorEl: null, content: '' })
  }

  const renderVarietyCell = (params: GridRenderCellParams) => {
    const variety = params.row as CropVariety
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', py: 1 }}>
        <Typography variant="body2" fontWeight="medium">
          {variety.variety}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {variety.producer}
        </Typography>
      </Box>
    )
  }

  const renderDescriptionCell = (params: GridRenderCellParams) => {
    const description = params.value as string
    const truncatedDescription = description.length > 100 
      ? description.substring(0, 100) + '...' 
      : description

    return (
      <Box
        onMouseEnter={(e) => handleDescriptionMouseEnter(e, description)}
        onMouseLeave={handleDescriptionMouseLeave}
        sx={{ 
          cursor: 'pointer',
          py: 1,
          '&:hover': {
            backgroundColor: 'rgba(0, 0, 0, 0.04)',
          }
        }}
      >
        <Typography variant="body2" sx={{ lineHeight: 1.4 }}>
          {truncatedDescription}
        </Typography>
      </Box>
    )
  }

  const renderMaturityCell = (params: GridRenderCellParams) => {
    const variety = params.row as CropVariety
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 1 }}>
        <Typography variant="body2" fontWeight="medium">
          {variety.maturity_months}
        </Typography>
        <Chip 
          label={variety.maturity_category}
          size="small"
          variant="outlined"
          sx={{ 
            height: 18, 
            fontSize: '0.7rem',
            mt: 0.5,
            backgroundColor: variety.maturity_category === 'Early' ? '#e8f5e8' :
                           variety.maturity_category === 'Medium' ? '#fff3e0' : '#fde7e7',
            color: variety.maturity_category === 'Early' ? '#2e7d32' :
                   variety.maturity_category === 'Medium' ? '#f57c00' : '#d32f2f'
          }}
        />
      </Box>
    )
  }

  const renderYieldCell = (params: GridRenderCellParams) => {
    return (
      <Typography variant="body2" sx={{ textAlign: 'center' }}>
        {params.value} tons/ha
      </Typography>
    )
  }

  const renderAltitudeCell = (params: GridRenderCellParams) => {
    const variety = params.row as CropVariety
    return (
      <Typography variant="body2" sx={{ textAlign: 'center' }}>
        {variety.min_altitude_masl.toLocaleString()} - {variety.max_altitude_masl.toLocaleString()} m
      </Typography>
    )
  }

  const columns: GridColDef[] = [
    {
      field: 'variety',
      headerName: 'Variety',
      width: 200,
      renderCell: renderVarietyCell,
    },
    {
      field: 'description',
      headerName: 'Description',
      width: 350,
      sortable: false,
      renderCell: renderDescriptionCell,
    },
    {
      field: 'maturity_months',
      headerName: 'Maturity',
      width: 150,
      align: 'center',
      headerAlign: 'center',
      renderCell: renderMaturityCell,
    },
    {
      field: 'yield_tons_ha',
      headerName: 'Yield Potential',
      width: 140,
      align: 'center',
      headerAlign: 'center',
      renderCell: renderYieldCell,
    },
    {
      field: 'altitude_range',
      headerName: 'Altitude Range',
      width: 180,
      align: 'center',
      headerAlign: 'center',
      sortable: false,
      renderCell: renderAltitudeCell,
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
    } else {
      // Reset to default sort when no sort is applied
      updateInstanceTableOptions({
        sortBy: ['variety'],
        descending: [false],
      })
    }
  }

  const handleFilterModelChange = (model: any) => {
    const quickFilterValue = model.quickFilterValues?.[0] || ''
    updateInstanceTableOptions({ q: quickFilterValue })
  }

  return (
    <Box sx={{ 
      p: 3, 
      backgroundColor: '#f8f9fa', 
      minHeight: '100%',
      width: '100%',
      maxWidth: 'none',
    }}>
      {/* Header */}
      <Box sx={{ mb: 3, width: '100%' }}>
        <Typography 
          variant="h4" 
          component="h1"
          sx={{ 
            fontWeight: 400,
            fontSize: '28px',
            color: '#3c4043',
            fontFamily: '"Google Sans", Roboto, sans-serif',
            mb: 2,
          }}
        >
          Seed Varieties
        </Typography>
        <Typography 
          variant="body2" 
          sx={{ 
            color: '#5f6368',
            fontSize: '14px',
            mb: 3,
          }}
        >
          {cropVarietiesData ? 
            `Browse ${cropVarietiesData.crop} varieties with detailed information on maturity, yield potential, and growing conditions` :
            'Loading seed varieties information...'
          }
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
          rows={instanceTable.rows.items.map((item: CropVariety, index: number) => ({ ...item, id: index }))}
          columns={columns}
          loading={instanceTable.loading}
          pagination
          rowCount={instanceTable.rows.total || 0}
          paginationModel={{
            page: instanceTable.options.page - 1, // DataGrid uses 0-based indexing
            pageSize: instanceTable.options.itemsPerPage,
          }}
          sortModel={
            options.sortBy.length > 0 
              ? [{ field: options.sortBy[0], sort: options.descending[0] ? 'desc' : 'asc' }]
              : []
          }
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
          onFilterModelChange={handleFilterModelChange}
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

      {/* Description Popover */}
      <Popover
        open={Boolean(descriptionPopover.anchorEl)}
        anchorEl={descriptionPopover.anchorEl}
        onClose={handleDescriptionMouseLeave}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        disableRestoreFocus
        sx={{
          pointerEvents: 'none',
        }}
        slotProps={{
          paper: {
            sx: {
              p: 2,
              maxWidth: 400,
              backgroundColor: 'rgba(97, 97, 97, 0.95)',
              color: 'white',
              fontSize: '14px',
              lineHeight: 1.4,
            }
          }
        }}
      >
        <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
          {descriptionPopover.content}
        </Typography>
      </Popover>
    </Box>
  )
}

export default SeedVarietiesTable
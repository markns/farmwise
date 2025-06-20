import React, { useEffect } from 'react'
import {
  Typography,
  Box,
  Chip,
  Stack,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Select,
  MenuItem,
  InputLabel,
  SelectChangeEvent,
} from '@mui/material'
import {
  DataGrid,
  GridColDef,
  GridToolbar,
  GridRenderCellParams,
} from '@mui/x-data-grid'
import { useMarketStore, type MarketPrice } from '@/stores/marketStore'

const MarketPricesTable: React.FC = () => {
  const {
    markets,
    commodities,
    instanceTable,
    loading,
    loadMarkets,
    loadCommodities,
    updateInstanceTableOptions,
  } = useMarketStore()

  const { options } = instanceTable

  useEffect(() => {
    loadMarkets()
    loadCommodities()
  }, [loadMarkets, loadCommodities])

  const handleQueryTypeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newQueryType = event.target.value as 'commodity' | 'market'
    updateInstanceTableOptions({
      queryType: newQueryType,
      selectedMarketId: null,
      selectedCommodityId: null,
      page: 1,
    })
  }

  const handleMarketChange = (event: SelectChangeEvent<number>) => {
    updateInstanceTableOptions({
      selectedMarketId: event.target.value as number,
      page: 1,
    })
  }

  const handleCommodityChange = (event: SelectChangeEvent<number>) => {
    updateInstanceTableOptions({
      selectedCommodityId: event.target.value as number,
      page: 1,
    })
  }

  const formatPrice = (price: number | null | undefined, currency: string, unit: string | null | undefined) => {
    if (price === null || price === undefined) return '-'
    return `${currency} ${price.toLocaleString()}${unit ? `/${unit}` : ''}`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const renderDateCell = (params: GridRenderCellParams) => {
    return (
      <Typography variant="body2">
        {formatDate(params.value)}
      </Typography>
    )
  }

  const renderMarketOrCommodityCell = (params: GridRenderCellParams) => {
    const price = params.row as MarketPrice
    return (
      <Stack direction="column" spacing={0.5} sx={{ py: 1 }}>
        <Typography variant="body2" fontWeight="medium">
          {options.queryType === 'market' ? price.commodity.name : price.market.name}
        </Typography>
        {options.queryType === 'market' && (price.commodity.classification || price.commodity.grade || price.commodity.sex) && (
          <Stack direction="row" spacing={0.5} flexWrap="wrap">
            {price.commodity.classification && (
              <Chip 
                label={price.commodity.classification}
                size="small"
                variant="outlined"
                sx={{ height: 18, fontSize: '0.7rem' }}
              />
            )}
            {price.commodity.grade && (
              <Chip 
                label={`Grade: ${price.commodity.grade}`}
                size="small"
                variant="outlined"
                sx={{ height: 18, fontSize: '0.7rem' }}
              />
            )}
            {price.commodity.sex && (
              <Chip 
                label={price.commodity.sex}
                size="small"
                variant="outlined"
                sx={{ height: 18, fontSize: '0.7rem' }}
              />
            )}
          </Stack>
        )}
      </Stack>
    )
  }

  const renderPriceCell = (params: GridRenderCellParams) => {
    const price = params.row as MarketPrice
    const { field } = params
    
    if (field === 'retail_price') {
      return (
        <Typography variant="body2">
          {formatPrice(price.retail_price, price.retail_ccy, price.retail_unit)}
        </Typography>
      )
    } else if (field === 'wholesale_price') {
      return (
        <Typography variant="body2">
          {formatPrice(price.wholesale_price, price.wholesale_ccy, price.wholesale_unit)}
        </Typography>
      )
    }
    return null
  }

  const renderSupplyVolumeCell = (params: GridRenderCellParams) => {
    const price = params.row as MarketPrice
    return (
      <Typography variant="body2">
        {price.supply_volume 
          ? `${price.supply_volume.toLocaleString()} ${price.wholesale_unit || 'units'}` 
          : '-'
        }
      </Typography>
    )
  }

  const columns: GridColDef[] = [
    {
      field: 'price_date',
      headerName: 'Date',
      width: 130,
      renderCell: renderDateCell,
    },
    {
      field: 'market_commodity',
      headerName: options.queryType === 'market' ? 'Commodity' : 'Market',
      width: 250,
      sortable: false,
      renderCell: renderMarketOrCommodityCell,
    },
    {
      field: 'retail_price',
      headerName: 'Retail Price',
      width: 150,
      renderCell: renderPriceCell,
    },
    {
      field: 'wholesale_price',
      headerName: 'Wholesale Price',
      width: 150,
      renderCell: renderPriceCell,
    },
    {
      field: 'supply_volume',
      headerName: 'Supply Volume',
      width: 140,
      renderCell: renderSupplyVolumeCell,
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
        sortBy: ['price_date'],
        descending: [true],
      })
    }
  }

  const canShowTable = (options.queryType === 'market' && options.selectedMarketId) || 
                       (options.queryType === 'commodity' && options.selectedCommodityId)

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
          Market Prices
        </Typography>
        <Typography 
          variant="body2" 
          sx={{ 
            color: '#5f6368',
            fontSize: '14px',
            mb: 3,
          }}
        >
          View market prices by market or commodity with filtering and sorting capabilities
        </Typography>

        {/* Query Controls */}
        <Box sx={{ mb: 3, backgroundColor: '#ffffff', p: 3, borderRadius: '8px', boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)' }}>
          <FormControl component="fieldset" sx={{ mb: 3 }}>
            <FormLabel component="legend">Query by:</FormLabel>
            <RadioGroup
              row
              value={options.queryType}
              onChange={handleQueryTypeChange}
              sx={{ mt: 1 }}
            >
              <FormControlLabel value="commodity" control={<Radio />} label="Commodity" />
              <FormControlLabel value="market" control={<Radio />} label="Market" />
            </RadioGroup>
          </FormControl>

          <Box sx={{ minWidth: 200, maxWidth: 400 }}>
            {options.queryType === 'market' ? (
              <FormControl fullWidth>
                <InputLabel>Select Market</InputLabel>
                <Select
                  value={options.selectedMarketId || ''}
                  onChange={handleMarketChange}
                  label="Select Market"
                  disabled={loading.markets}
                >
                  <MenuItem value="">
                    <em>Choose a market</em>
                  </MenuItem>
                  {markets.map((market: any) => (
                    <MenuItem key={market.id} value={market.id}>
                      {market.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <FormControl fullWidth>
                <InputLabel>Select Commodity</InputLabel>
                <Select
                  value={options.selectedCommodityId || ''}
                  onChange={handleCommodityChange}
                  label="Select Commodity"
                  disabled={loading.commodities}
                >
                  <MenuItem value="">
                    <em>Choose a commodity</em>
                  </MenuItem>
                  {commodities.map((commodity: any) => (
                    <MenuItem key={commodity.id} value={commodity.id}>
                      <Box>
                        <Typography variant="body2" component="div">
                          {commodity.name}
                        </Typography>
                        {(commodity.classification || commodity.grade || commodity.sex) && (
                          <Typography variant="caption" color="text.secondary" component="div">
                            {[commodity.classification, commodity.grade, commodity.sex]
                              .filter(Boolean)
                              .join(' • ')}
                          </Typography>
                        )}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
          </Box>
        </Box>
      </Box>

      {/* Data Table */}
      {canShowTable && (
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
      )}

      {!canShowTable && (
        <Box
          sx={{
            backgroundColor: '#ffffff',
            borderRadius: '8px',
            boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
            p: 4,
            textAlign: 'center',
          }}
        >
          <Typography variant="body1" color="text.secondary">
            Please select a {options.queryType} to view market prices.
          </Typography>
        </Box>
      )}
    </Box>
  )
}

export default MarketPricesTable
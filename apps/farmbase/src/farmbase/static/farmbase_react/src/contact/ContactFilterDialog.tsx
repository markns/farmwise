import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  OutlinedInput,
  Divider,
} from '@mui/material'
import {
  Close as CloseIcon,
  FilterAlt as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import { useContactStore } from '@/stores/contactStore'

const ContactFilterDialog: React.FC = () => {
  const {
    dialogs,
    closeFilter,
    availableFilters,
    loadFilterOptions,
    applyFilters,
    table,
  } = useContactStore()

  const [filters, setFilters] = React.useState<Record<string, string[]>>({
    gender: [],
    role: [],
    organization: [],
  })

  // Load filter options when dialog opens
  React.useEffect(() => {
    if (dialogs.showFilter) {
      loadFilterOptions()
      // Initialize with current table filters
      setFilters({
        gender: table.options.filters.gender || [],
        role: table.options.filters.role || [],
        organization: table.options.filters.organization || [],
      })
    }
  }, [dialogs.showFilter, loadFilterOptions, table.options.filters])

  const handleFilterChange = (filterType: string, values: string[]) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: values
    }))
  }

  const handleApplyFilters = () => {
    // Remove empty filter arrays
    const cleanedFilters = Object.entries(filters).reduce((acc, [key, value]) => {
      if (value.length > 0) {
        acc[key] = value
      }
      return acc
    }, {} as Record<string, string[]>)

    applyFilters(cleanedFilters)
    closeFilter()
  }

  const handleClearFilters = () => {
    setFilters({
      gender: [],
      role: [],
      organization: [],
    })
  }

  const handleClose = () => {
    closeFilter()
  }

  const getFilterCount = () => {
    return Object.values(filters).reduce((count, filterValues) => count + filterValues.length, 0)
  }

  return (
    <Dialog
      open={dialogs.showFilter}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterIcon />
            <Typography variant="h6">
              Filter Contacts
            </Typography>
            {getFilterCount() > 0 && (
              <Chip 
                label={`${getFilterCount()} active`} 
                size="small" 
                color="primary" 
              />
            )}
          </Box>
          <IconButton onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ pt: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Gender Filter */}
          <FormControl fullWidth>
            <InputLabel>Gender</InputLabel>
            <Select
              multiple
              value={filters.gender}
              onChange={(e) => handleFilterChange('gender', e.target.value as string[])}
              input={<OutlinedInput label="Gender" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} size="small" />
                  ))}
                </Box>
              )}
            >
              {availableFilters.gender?.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              )) || [
                <MenuItem key="male" value="male">Male</MenuItem>,
                <MenuItem key="female" value="female">Female</MenuItem>,
                <MenuItem key="other" value="other">Other</MenuItem>,
              ]}
            </Select>
          </FormControl>

          {/* Role Filter */}
          <FormControl fullWidth>
            <InputLabel>Role</InputLabel>
            <Select
              multiple
              value={filters.role}
              onChange={(e) => handleFilterChange('role', e.target.value as string[])}
              input={<OutlinedInput label="Role" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} size="small" />
                  ))}
                </Box>
              )}
            >
              {availableFilters.role?.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              )) || [
                <MenuItem key="farmer" value="farmer">Farmer</MenuItem>,
                <MenuItem key="advisor" value="advisor">Advisor</MenuItem>,
                <MenuItem key="worker" value="worker">Worker</MenuItem>,
                <MenuItem key="manager" value="manager">Manager</MenuItem>,
              ]}
            </Select>
          </FormControl>

          {/* Organization Filter */}
          <FormControl fullWidth>
            <InputLabel>Organization</InputLabel>
            <Select
              multiple
              value={filters.organization}
              onChange={(e) => handleFilterChange('organization', e.target.value as string[])}
              input={<OutlinedInput label="Organization" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} size="small" />
                  ))}
                </Box>
              )}
            >
              {availableFilters.organization?.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              )) || [
                <MenuItem key="sample-org-1" value="sample-org-1">Sample Organization 1</MenuItem>,
                <MenuItem key="sample-org-2" value="sample-org-2">Sample Organization 2</MenuItem>,
              ]}
            </Select>
          </FormControl>

          {/* Active Filters Summary */}
          {getFilterCount() > 0 && (
            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Active Filters:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {Object.entries(filters).map(([filterType, values]) =>
                  values.map((value) => (
                    <Chip
                      key={`${filterType}-${value}`}
                      label={`${filterType}: ${value}`}
                      size="small"
                      variant="outlined"
                      onDelete={() => {
                        handleFilterChange(
                          filterType,
                          filters[filterType].filter(v => v !== value)
                        )
                      }}
                    />
                  ))
                )}
              </Box>
            </Box>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 2 }}>
        <Button
          onClick={handleClearFilters}
          startIcon={<ClearIcon />}
          disabled={getFilterCount() === 0}
        >
          Clear All
        </Button>
        <Box sx={{ flex: 1 }} />
        <Button onClick={handleClose} variant="outlined">
          Cancel
        </Button>
        <Button onClick={handleApplyFilters} variant="contained">
          Apply Filters
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default ContactFilterDialog
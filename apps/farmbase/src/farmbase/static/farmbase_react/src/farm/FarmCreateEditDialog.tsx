import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  Box,
  IconButton,
  Typography,
  Divider,
} from '@mui/material'
import {
  Close as CloseIcon,
  Save as SaveIcon,
  Agriculture as FarmIcon,
} from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import { useFarmStore, type FarmWithContacts } from '@/stores/farmStore'

interface FarmFormData {
  farm_name: string
  description: string
  area: string
  owner: string
  latitude: string
  longitude: string
  address: string
}

// Basic form validation rules
const validateForm = (data: FarmFormData) => {
  const errors: Partial<Record<keyof FarmFormData, string>> = {}
  
  if (!data.farm_name || data.farm_name.trim().length < 2) {
    errors.farm_name = 'Farm name is required and must be at least 2 characters'
  }
  
  if (data.area && Number(data.area) <= 0) {
    errors.area = 'Area must be positive'
  }
  
  if (data.latitude && (Number(data.latitude) < -90 || Number(data.latitude) > 90)) {
    errors.latitude = 'Latitude must be between -90 and 90'
  }
  
  if (data.longitude && (Number(data.longitude) < -180 || Number(data.longitude) > 180)) {
    errors.longitude = 'Longitude must be between -180 and 180'
  }
  
  return errors
}

const FarmCreateEditDialog: React.FC = () => {
  const {
    dialogs,
    selected,
    closeCreateEdit,
    save,
  } = useFarmStore()

  const isEdit = Boolean(selected?.id)

  const {
    control,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FarmFormData>({
    defaultValues: {
      farm_name: '',
      description: '',
      area: '',
      owner: '',
      latitude: '',
      longitude: '',
      address: '',
    },
  })

  // Reset form when dialog opens/closes or selected farm changes
  React.useEffect(() => {
    if (dialogs.showCreateEdit && selected) {
      reset({
        farm_name: selected.farm_name || '',
        description: selected.description || '',
        area: selected.area?.toString() || '',
        owner: selected.owner || '',
        latitude: selected.location?.latitude?.toString() || '',
        longitude: selected.location?.longitude?.toString() || '',
        address: selected.location?.address || '',
      })
    } else if (dialogs.showCreateEdit) {
      reset({
        farm_name: '',
        description: '',
        area: '',
        owner: '',
        latitude: '',
        longitude: '',
        address: '',
      })
    }
  }, [dialogs.showCreateEdit, selected, reset])

  const onSubmit = async (data: FarmFormData) => {
    // Validate form
    const validationErrors = validateForm(data)
    if (Object.keys(validationErrors).length > 0) {
      Object.entries(validationErrors).forEach(([field, message]) => {
        setError(field as keyof FarmFormData, { message })
      })
      return
    }

    try {
      // Update the selected farm with form data
      if (selected) {
        const farmData: FarmWithContacts = {
          ...selected,
          farm_name: data.farm_name,
          name: data.farm_name,
          description: data.description,
          area: data.area ? Number(data.area) : undefined,
          owner: data.owner,
          location: (data.latitude && data.longitude) ? {
            latitude: Number(data.latitude),
            longitude: Number(data.longitude),
            address: data.address || undefined,
          } : undefined,
        }
        
        // Temporarily update selected to match form data
        const originalSelected = selected
        useFarmStore.setState({ selected: farmData })
        
        try {
          await save()
        } catch (error) {
          // Restore original state on error
          useFarmStore.setState({ selected: originalSelected })
          throw error
        }
      }
    } catch (error) {
      console.error('Failed to save farm:', error)
    }
  }

  const handleClose = () => {
    if (!isSubmitting) {
      closeCreateEdit()
    }
  }

  return (
    <Dialog
      open={dialogs.showCreateEdit}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FarmIcon />
            <Typography variant="h6">
              {isEdit ? 'Edit Farm' : 'Create New Farm'}
            </Typography>
          </Box>
          <IconButton onClick={handleClose} disabled={isSubmitting}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <Divider />

      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent sx={{ pt: 3 }}>
          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Basic Information
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="farm_name"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Farm Name"
                    fullWidth
                    required
                    error={!!errors.farm_name}
                    helperText={errors.farm_name?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="owner"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Owner"
                    fullWidth
                    error={!!errors.owner}
                    helperText={errors.owner?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Description"
                    fullWidth
                    multiline
                    rows={3}
                    error={!!errors.description}
                    helperText={errors.description?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="area"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Area (hectares)"
                    fullWidth
                    type="number"
                    error={!!errors.area}
                    helperText={errors.area?.message}
                    disabled={isSubmitting}
                    InputProps={{
                      inputProps: { min: 0, step: 0.01 }
                    }}
                  />
                )}
              />
            </Grid>

            {/* Location Information */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                Location Information
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Controller
                name="address"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Address"
                    fullWidth
                    error={!!errors.address}
                    helperText={errors.address?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="latitude"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Latitude"
                    fullWidth
                    type="number"
                    error={!!errors.latitude}
                    helperText={errors.latitude?.message || 'Decimal degrees (-90 to 90)'}
                    disabled={isSubmitting}
                    InputProps={{
                      inputProps: { min: -90, max: 90, step: 0.000001 }
                    }}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="longitude"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Longitude"
                    fullWidth
                    type="number"
                    error={!!errors.longitude}
                    helperText={errors.longitude?.message || 'Decimal degrees (-180 to 180)'}
                    disabled={isSubmitting}
                    InputProps={{
                      inputProps: { min: -180, max: 180, step: 0.000001 }
                    }}
                  />
                )}
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 3, pt: 2 }}>
          <Button
            onClick={handleClose}
            disabled={isSubmitting}
            variant="outlined"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isSubmitting}
            startIcon={isSubmitting ? <></> : <SaveIcon />}
          >
            {isSubmitting ? 'Saving...' : (isEdit ? 'Update Farm' : 'Create Farm')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}

export default FarmCreateEditDialog
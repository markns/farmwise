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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from '@mui/material'
import {
  Close as CloseIcon,
  Save as SaveIcon,
  Person as PersonIcon,
  Add as AddIcon,
} from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import { useContactStore, type Contact } from '@/stores/contactStore'

interface ContactFormData {
  name: string
  external_id: string
  external_url: string
  phone_number: string
  email: string
  preferred_form_of_address: string
  gender: string
  date_of_birth: string
  estimated_age: string
  role: string
  experience: string
  organization: string
  product_interests_crops: string[]
  product_interests_livestock: string[]
  product_interests_other: string[]
}

// Basic form validation rules
const validateForm = (data: ContactFormData) => {
  const errors: Partial<Record<keyof ContactFormData, string>> = {}
  
  if (!data.name || data.name.trim().length < 2) {
    errors.name = 'Name is required and must be at least 2 characters'
  }
  
  if (!data.external_id || data.external_id.trim().length < 1) {
    errors.external_id = 'External ID is required'
  }
  
  if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.email = 'Please enter a valid email address'
  }
  
  if (data.estimated_age && (Number(data.estimated_age) < 0 || Number(data.estimated_age) > 150)) {
    errors.estimated_age = 'Age must be between 0 and 150'
  }
  
  if (data.experience && Number(data.experience) < 0) {
    errors.experience = 'Experience cannot be negative'
  }
  
  return errors
}

const ContactCreateEditDialog: React.FC = () => {
  const {
    dialogs,
    selected,
    closeCreateEdit,
    save,
    setSelected,
  } = useContactStore()

  const isEdit = Boolean(selected?.id)

  const {
    control,
    handleSubmit,
    reset,
    setError,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<ContactFormData>({
    defaultValues: {
      name: '',
      external_id: '',
      external_url: '',
      phone_number: '',
      email: '',
      preferred_form_of_address: '',
      gender: '',
      date_of_birth: '',
      estimated_age: '',
      role: '',
      experience: '',
      organization: '',
      product_interests_crops: [],
      product_interests_livestock: [],
      product_interests_other: [],
    },
  })

  const [newCropInterest, setNewCropInterest] = React.useState('')
  const [newLivestockInterest, setNewLivestockInterest] = React.useState('')
  const [newOtherInterest, setNewOtherInterest] = React.useState('')

  // Reset form when dialog opens/closes or selected contact changes
  React.useEffect(() => {
    if (dialogs.showCreateEdit && selected) {
      reset({
        name: selected.name || '',
        external_id: selected.external_id || '',
        external_url: selected.external_url || '',
        phone_number: selected.phone_number || '',
        email: selected.email || '',
        preferred_form_of_address: selected.preferred_form_of_address || '',
        gender: selected.gender || '',
        date_of_birth: selected.date_of_birth || '',
        estimated_age: selected.estimated_age?.toString() || '',
        role: selected.role || '',
        experience: selected.experience?.toString() || '',
        organization: selected.organization || '',
        product_interests_crops: selected.product_interests?.crops || [],
        product_interests_livestock: selected.product_interests?.livestock || [],
        product_interests_other: selected.product_interests?.other || [],
      })
    } else if (dialogs.showCreateEdit) {
      reset({
        name: '',
        external_id: '',
        external_url: '',
        phone_number: '',
        email: '',
        preferred_form_of_address: '',
        gender: '',
        date_of_birth: '',
        estimated_age: '',
        role: '',
        experience: '',
        organization: '',
        product_interests_crops: [],
        product_interests_livestock: [],
        product_interests_other: [],
      })
    }
  }, [dialogs.showCreateEdit, selected, reset])

  const onSubmit = async (data: ContactFormData) => {
    // Validate form
    const validationErrors = validateForm(data)
    if (Object.keys(validationErrors).length > 0) {
      Object.entries(validationErrors).forEach(([field, message]) => {
        setError(field as keyof ContactFormData, { message })
      })
      return
    }

    try {
      // Update the selected contact with form data
      if (selected) {
        const contactData: Contact = {
          ...selected,
          name: data.name,
          external_id: data.external_id,
          external_url: data.external_url || undefined,
          phone_number: data.phone_number || undefined,
          email: data.email || undefined,
          preferred_form_of_address: data.preferred_form_of_address || undefined,
          gender: data.gender || undefined,
          date_of_birth: data.date_of_birth || undefined,
          estimated_age: data.estimated_age ? Number(data.estimated_age) : undefined,
          role: data.role || undefined,
          experience: data.experience ? Number(data.experience) : undefined,
          organization: data.organization || undefined,
          product_interests: {
            crops: data.product_interests_crops,
            livestock: data.product_interests_livestock,
            other: data.product_interests_other,
          },
        }
        
        // Temporarily update selected to match form data
        const originalSelected = selected
        setSelected(contactData)
        
        try {
          await save()
        } catch (error) {
          // Restore original state on error
          setSelected(originalSelected)
          throw error
        }
      }
    } catch (error) {
      console.error('Failed to save contact:', error)
    }
  }

  const handleClose = () => {
    if (!isSubmitting) {
      closeCreateEdit()
    }
  }

  const addInterest = (type: 'crops' | 'livestock' | 'other', value: string) => {
    if (!value.trim()) return

    const currentInterests = watch(`product_interests_${type}`)
    if (!currentInterests.includes(value.trim())) {
      setValue(`product_interests_${type}`, [...currentInterests, value.trim()])
    }

    // Clear the input
    if (type === 'crops') setNewCropInterest('')
    if (type === 'livestock') setNewLivestockInterest('')
    if (type === 'other') setNewOtherInterest('')
  }

  const removeInterest = (type: 'crops' | 'livestock' | 'other', value: string) => {
    const currentInterests = watch(`product_interests_${type}`)
    setValue(`product_interests_${type}`, currentInterests.filter(interest => interest !== value))
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
            <PersonIcon />
            <Typography variant="h6">
              {isEdit ? 'Edit Contact' : 'Create New Contact'}
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
                name="name"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Name"
                    fullWidth
                    required
                    error={!!errors.name}
                    helperText={errors.name?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="external_id"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="External ID"
                    fullWidth
                    required
                    error={!!errors.external_id}
                    helperText={errors.external_id?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Controller
                name="external_url"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="External URL"
                    fullWidth
                    error={!!errors.external_url}
                    helperText={errors.external_url?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            {/* Contact Details */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                Contact Details
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="phone_number"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Phone Number"
                    fullWidth
                    error={!!errors.phone_number}
                    helperText={errors.phone_number?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="email"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Email"
                    fullWidth
                    type="email"
                    error={!!errors.email}
                    helperText={errors.email?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Controller
                name="preferred_form_of_address"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Preferred Form of Address"
                    fullWidth
                    error={!!errors.preferred_form_of_address}
                    helperText={errors.preferred_form_of_address?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            {/* Personal Information */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                Personal Information
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <Controller
                name="gender"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Gender</InputLabel>
                    <Select
                      {...field}
                      label="Gender"
                      disabled={isSubmitting}
                    >
                      <MenuItem value="">Not specified</MenuItem>
                      <MenuItem value="male">Male</MenuItem>
                      <MenuItem value="female">Female</MenuItem>
                      <MenuItem value="other">Other</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <Controller
                name="date_of_birth"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Date of Birth"
                    fullWidth
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.date_of_birth}
                    helperText={errors.date_of_birth?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <Controller
                name="estimated_age"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Estimated Age"
                    fullWidth
                    type="number"
                    error={!!errors.estimated_age}
                    helperText={errors.estimated_age?.message}
                    disabled={isSubmitting}
                    InputProps={{
                      inputProps: { min: 0, max: 150 }
                    }}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="role"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Role"
                    fullWidth
                    error={!!errors.role}
                    helperText={errors.role?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="experience"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Experience (years)"
                    fullWidth
                    type="number"
                    error={!!errors.experience}
                    helperText={errors.experience?.message}
                    disabled={isSubmitting}
                    InputProps={{
                      inputProps: { min: 0 }
                    }}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Controller
                name="organization"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Organization"
                    fullWidth
                    error={!!errors.organization}
                    helperText={errors.organization?.message}
                    disabled={isSubmitting}
                  />
                )}
              />
            </Grid>

            {/* Product Interests */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                Product Interests
              </Typography>
            </Grid>

            {/* Crops */}
            <Grid item xs={12} md={4}>
              <Typography variant="body2" gutterBottom>Crops</Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  size="small"
                  placeholder="Add crop interest"
                  value={newCropInterest}
                  onChange={(e) => setNewCropInterest(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addInterest('crops', newCropInterest)
                    }
                  }}
                />
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => addInterest('crops', newCropInterest)}
                  startIcon={<AddIcon />}
                >
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {watch('product_interests_crops').map((crop, index) => (
                  <Chip
                    key={index}
                    label={crop}
                    size="small"
                    onDelete={() => removeInterest('crops', crop)}
                    sx={{
                      bgcolor: '#c8e6c9',
                      color: '#2e7d32',
                    }}
                  />
                ))}
              </Box>
            </Grid>

            {/* Livestock */}
            <Grid item xs={12} md={4}>
              <Typography variant="body2" gutterBottom>Livestock</Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  size="small"
                  placeholder="Add livestock interest"
                  value={newLivestockInterest}
                  onChange={(e) => setNewLivestockInterest(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addInterest('livestock', newLivestockInterest)
                    }
                  }}
                />
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => addInterest('livestock', newLivestockInterest)}
                  startIcon={<AddIcon />}
                >
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {watch('product_interests_livestock').map((livestock, index) => (
                  <Chip
                    key={index}
                    label={livestock}
                    size="small"
                    onDelete={() => removeInterest('livestock', livestock)}
                    sx={{
                      bgcolor: '#d7ccc8',
                      color: '#5d4037',
                    }}
                  />
                ))}
              </Box>
            </Grid>

            {/* Other */}
            <Grid item xs={12} md={4}>
              <Typography variant="body2" gutterBottom>Other</Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  size="small"
                  placeholder="Add other interest"
                  value={newOtherInterest}
                  onChange={(e) => setNewOtherInterest(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addInterest('other', newOtherInterest)
                    }
                  }}
                />
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => addInterest('other', newOtherInterest)}
                  startIcon={<AddIcon />}
                >
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {watch('product_interests_other').map((other, index) => (
                  <Chip
                    key={index}
                    label={other}
                    size="small"
                    onDelete={() => removeInterest('other', other)}
                    sx={{
                      bgcolor: '#bbdefb',
                      color: '#1976d2',
                    }}
                  />
                ))}
              </Box>
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
            {isSubmitting ? 'Saving...' : (isEdit ? 'Update Contact' : 'Create Contact')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}

export default ContactCreateEditDialog
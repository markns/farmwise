<template>
  <v-chip
    color="primary"
    variant="tonal"
    size="small"
    @click="openMaps"
    class="location-chip"
  >
    <v-icon start>mdi-map-marker</v-icon>
    {{ formatLocation(location) }}
  </v-chip>
</template>

<script>
export default {
  name: "LocationChip",
  props: {
    location: {
      type: Object,
      required: true,
      validator: (value) => {
        return value && typeof value.latitude === 'number' && typeof value.longitude === 'number'
      }
    }
  },
  methods: {
    formatLocation(location) {
      return `${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}`
    },
    openMaps() {
      const url = `https://www.google.com/maps?q=${this.location.latitude},${this.location.longitude}`
      window.open(url, '_blank')
    }
  }
}
</script>

<style scoped>
.location-chip {
  cursor: pointer;
}

.location-chip:hover {
  opacity: 0.8;
}
</style>
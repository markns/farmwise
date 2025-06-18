<template>
  <v-menu
    v-model="showPopover"
    :close-on-content-click="false"
    location="bottom"
    origin="auto"
    max-width="400"
  >
    <template #activator="{ props }">
      <v-btn
        v-bind="props"
        variant="text"
        color="primary"
        size="small"
        class="text-none"
      >
        <v-icon start>mdi-map-marker</v-icon>
        {{ formatLocation(location) }}
      </v-btn>
    </template>

    <v-card class="pa-4" min-width="350">
      <v-card-title class="text-h6 pb-2">
        <v-icon start>mdi-map-marker</v-icon>
        {{ farmName }} Location
      </v-card-title>
      
      <v-card-text>
        <div class="mb-3">
          <div class="text-caption text-grey">Coordinates</div>
          <div class="text-body-2">
            <strong>Latitude:</strong> {{ location.latitude.toFixed(6) }}<br>
            <strong>Longitude:</strong> {{ location.longitude.toFixed(6) }}
          </div>
        </div>
        
        <!-- Simple map placeholder - in a real app you'd use a proper map component -->
        <div class="map-container">
          <div class="map-placeholder">
            <v-icon size="64" color="primary">mdi-map</v-icon>
            <div class="text-body-2 mt-2">Map View</div>
            <div class="text-caption text-grey">
              {{ location.latitude.toFixed(4) }}, {{ location.longitude.toFixed(4) }}
            </div>
          </div>
        </div>
        
        <div class="mt-3">
          <v-btn
            :href="getGoogleMapsLink()"
            target="_blank"
            color="primary"
            variant="outlined"
            size="small"
            block
          >
            <v-icon start>mdi-open-in-new</v-icon>
            View in Google Maps
          </v-btn>
        </div>
      </v-card-text>
      
      <v-card-actions>
        <v-spacer />
        <v-btn @click="showPopover = false" color="primary">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script>
export default {
  name: "LocationPopover",
  props: {
    location: {
      type: Object,
      required: true,
      validator: (value) => {
        return value && typeof value.latitude === 'number' && typeof value.longitude === 'number'
      }
    },
    farmName: {
      type: String,
      default: "Farm"
    }
  },
  data() {
    return {
      showPopover: false,
    }
  },
  methods: {
    formatLocation(location) {
      return `${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}`
    },
    getGoogleMapsLink() {
      return `https://www.google.com/maps?q=${this.location.latitude},${this.location.longitude}`
    }
  }
}
</script>

<style scoped>
.map-container {
  height: 150px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.map-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
  color: #666;
}
</style>
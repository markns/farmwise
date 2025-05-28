<template>
  <v-navigation-drawer
    v-model="showDialog"
    location="right"
    temporary
    width="600"
    class="notes-drawer"
  >
    <v-card flat>
      <v-card-title class="d-flex align-center justify-space-between">
        <span>
          <v-icon start>mdi-note-text</v-icon>
          Farm Notes
        </span>
        <v-btn icon variant="text" @click="closeNotes">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      
      <v-divider />
      
      <v-card-subtitle v-if="selected.farm_name" class="py-2">
        {{ selected.farm_name }}
      </v-card-subtitle>
      
      <v-card-text v-if="notesLoading" class="text-center">
        <v-progress-circular indeterminate />
        <div class="mt-2">Loading notes...</div>
      </v-card-text>
      
      <v-card-text v-else class="notes-content">
        <div v-if="notes.items.length === 0" class="text-center text-grey py-8">
          <v-icon size="64" color="grey-lighten-1">mdi-note-off</v-icon>
          <div class="mt-2">No notes found for this farm</div>
        </div>
        
        <div v-else class="notes-list">
          <v-card
            v-for="note in notes.items"
            :key="note.id"
            variant="outlined"
            class="mb-4"
          >
            <v-card-text>
              <div class="note-content">
                {{ note.note_text }}
              </div>
              
              <div v-if="note.tags" class="mt-3">
                <v-chip-group>
                  <v-chip
                    v-for="tag in note.tags.split(',')"
                    :key="tag.trim()"
                    size="small"
                    color="primary"
                    variant="tonal"
                  >
                    {{ tag.trim() }}
                  </v-chip>
                </v-chip-group>
              </div>
              
              <div v-if="note.location" class="mt-3">
                <div class="text-caption text-grey mb-1">Location</div>
                <location-chip :location="note.location" />
              </div>
              
              <div v-if="note.image_path" class="mt-3">
                <div class="text-caption text-grey mb-2">Attached Image</div>
                <v-img
                  :src="getImageUrl(note.image_path)"
                  :alt="`Image for note ${note.id}`"
                  max-height="300"
                  max-width="100%"
                  class="rounded"
                  @error="handleImageError"
                >
                  <template #placeholder>
                    <div class="d-flex align-center justify-center fill-height">
                      <v-progress-circular indeterminate />
                    </div>
                  </template>
                  <template #error>
                    <div class="d-flex align-center justify-center fill-height bg-grey-lighten-4">
                      <div class="text-center">
                        <v-icon size="48" color="grey">mdi-image-broken</v-icon>
                        <div class="text-caption">Failed to load image</div>
                      </div>
                    </div>
                  </template>
                </v-img>
              </div>
            </v-card-text>
            
            <v-card-actions class="pt-0">
              <v-spacer />
              <div class="text-caption text-grey">
                Note ID: {{ note.id }}
              </div>
            </v-card-actions>
          </v-card>
        </div>
        
        <div v-if="notes.total > notes.items.length" class="text-center mt-4">
          <div class="text-caption text-grey">
            Showing {{ notes.items.length }} of {{ notes.total }} notes
          </div>
        </div>
      </v-card-text>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import LocationChip from "./LocationChip.vue"

export default {
  name: "NotesDrawer",
  components: { LocationChip },
  
  computed: {
    ...mapFields("farm", [
      "dialogs.showNotes",
      "selected",
      "notes",
      "notes.loading",
    ]),
    showDialog: {
      get() {
        return this.showNotes
      },
      set(value) {
        if (!value) {
          this.closeNotes()
        }
      }
    },
    notesLoading() {
      return this.loading
    }
  },
  
  methods: {
    ...mapActions("farm", ["closeNotes"]),
    getImageUrl(imagePath) {
      // If the image path is already a full URL, return it as is
      if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
        return imagePath
      }
      console.log(`file://${imagePath}`)
      // If it's a relative path, assume it's relative to the API base
      // This will work with the farmbase API structure
      if (imagePath.startsWith('/')) {
        return `file://${imagePath}`
      }
      
      // For paths without leading slash, prepend with standard path
      return `/api/v1/${this.$route.params.organization || 'default'}/files/${imagePath}`
    },
    handleImageError(error) {
      console.warn('Failed to load image:', error)
    }
  }
}
</script>

<style scoped>
.notes-drawer {
  z-index: 1000;
}

.notes-content {
  max-height: 70vh;
  overflow-y: auto;
}

.note-content {
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.notes-list {
  padding-bottom: 20px;
}
</style>
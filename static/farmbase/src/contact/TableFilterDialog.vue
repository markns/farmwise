<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Contact Instance Filters</span>
      </v-card-title>
      <v-list density="compact">
        <v-list-item>
          <contact-definition-combobox v-model="local_contact" label="Contact Definitions" />
        </v-list-item>
      </v-list>
      <v-card-actions>
        <v-spacer />
        <v-btn color="info" variant="text" @click="applyFilters()"> Apply Filters </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"

import ContactDefinitionCombobox from "@/contact/ContactDefinitionCombobox.vue"

export default {
  name: "ContactInstanceTableFilterDialog",

  components: {
    ContactDefinitionCombobox,
  },

  data() {
    return {
      display: false,
      local_contact: [],
    }
  },

  computed: {
    ...mapFields("contact", ["instanceTable.options.filters.contact"]),
    numFilters: function () {
      return sum([this.contact.length])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.contact = this.local_contact

      // we close the dialog
      this.display = false
    },
  },
}
</script>

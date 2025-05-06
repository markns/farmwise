<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Farmer Instance Filters</span>
      </v-card-title>
      <v-list density="compact">
        <v-list-item>
          <farmer-definition-combobox v-model="local_farmer" label="Farmer Definitions" />
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

import FarmerDefinitionCombobox from "@/farmer/FarmerDefinitionCombobox.vue"

export default {
  name: "FarmerInstanceTableFilterDialog",

  components: {
    FarmerDefinitionCombobox,
  },

  data() {
    return {
      display: false,
      local_farmer: [],
    }
  },

  computed: {
    ...mapFields("farmer", ["instanceTable.options.filters.farmer"]),
    numFilters: function () {
      return sum([this.farmer.length])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.farmer = this.local_farmer

      // we close the dialog
      this.display = false
    },
  },
}
</script>

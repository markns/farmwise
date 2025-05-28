<template>
  <div>
    <v-menu v-model="menu" origin="overlap">
      <template #activator="{ props }">
        <v-chip pill size="small" v-bind="props">
          <template #prepend>
            <v-avatar color="teal">
              {{ initials(value.name) }}
            </v-avatar>
          </template>
          {{ value.name }}
        </v-chip>
      </template>
      <v-card width="300">
        <v-list>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>ID: {{ value.id }}</v-list-item-title>
              <v-list-item-subtitle>Name: {{ value.name }}</v-list-item-subtitle>
            </v-list-item-content>
            <template #append>
              <v-btn icon variant="text" @click="menu = false">
                <v-icon>mdi-close-circle</v-icon>
              </v-btn>
            </template>
          </v-list-item>
          <v-divider />
          <v-list-item v-if="value.phone_number">
            <template #prepend>
              <v-icon>mdi-phone</v-icon>
            </template>
            <v-list-item-subtitle>{{ value.phone_number }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="value.email">
            <template #prepend>
              <v-icon>mdi-email</v-icon>
            </template>
            <v-list-item-subtitle>{{ value.email }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="value.preferred_form_of_address">
            <template #prepend>
              <v-icon>mdi-account</v-icon>
            </template>
            <v-list-item-subtitle>
              Addressed As: {{ value.preferred_form_of_address }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="value.gender">
            <template #prepend>
              <v-icon>mdi-gender-male-female</v-icon>
            </template>
            <v-list-item-subtitle>Gender: {{ value.gender }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="value.date_of_birth">
            <template #prepend>
              <v-icon>mdi-calendar</v-icon>
            </template>
            <v-list-item-subtitle>DOB: {{ value.date_of_birth }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="value.estimated_age">
            <template #prepend>
              <v-icon>mdi-cake-variant</v-icon>
            </template>
            <v-list-item-subtitle>
              Estimated Age: {{ value.estimated_age }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="value.role">
            <template #prepend>
              <v-icon>mdi-briefcase-outline</v-icon>
            </template>
            <v-list-item-subtitle>Role: {{ value.role }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="value.experience != null">
            <template #prepend>
              <v-icon>mdi-star-circle</v-icon>
            </template>
            <v-list-item-subtitle>
              Experience: {{ value.experience }} years
            </v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="value.organization">
            <template #prepend>
              <v-icon>mdi-domain</v-icon>
            </template>
            <v-list-item-subtitle>Org: {{ value.organization.name }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="value.farms && value.farms.length">
            <template #prepend>
              <v-icon>mdi-farm</v-icon>
            </template>
            <v-list-item-subtitle>
              Farms:
              <span v-for="(farm, idx) in value.farms" :key="farm.id">
                {{ farm.farm_name }}<span v-if="idx < value.farms.length - 1">, </span>
              </span>
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
import { initials } from "@/filters"

export default {
  name: "FarmerPopover",

  data: () => ({
    menu: false,
  }),

  setup() {
    return { initials }
  },

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },
}
</script>
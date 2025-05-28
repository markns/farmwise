<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col>
        <div class="text-h5">Farmers</div>
      </v-col>
      <v-col class="text-right">
        <table-filter-dialog />
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card variant="flat">
          <!-- <v-card-title> -->
          <!--   <v-text-field -->
          <!--     v-model="q" -->
          <!--     append-icon="search" -->
          <!--     label="Search" -->
          <!--     single-line -->
          <!--     hide-details -->
          <!--     clearable -->
          <!--   /> -->
          <!-- </v-card-title> -->
          <v-data-table-server
            :headers="headers"
            :items="items"
            :items-length="total || 0"
            v-model:page="page"
            v-model:items-per-page="itemsPerPage"
            :footer-props="{
              'items-per-page-options': [10, 25, 50, 100],
            }"
            v-model:sort-by="sortBy"
            v-model:sort-desc="descending"
            :loading="loading"
            loading-text="Loading... Please wait"
          >
          <!--            <template #item.case="{ value }">
            <case-popover v-if="value" :value="value" />
            </template>
            <template #item.farmer="{ value }">
              <farmer-popover :value="value" />
            </template>
            <template #item.farmer.project.display_name="{ item, value }">
              <v-chip size="small" :color="item.farmer.project.color">
                {{ value }}
              </v-chip>
            </template>
            <template #item.filter_action="{ value }">
              <v-chip
                size="small"
                :color="
                  {
                    snooze: 'blue-accent-4',
                    deduplicate: 'blue-accent-2',
                  }[value]
                "
              >
                {{
                  {
                    snooze: "Snoozed",
                    deduplicate: "Duplicate",
                  }[value] || "Not Filtered"
                }}
              </v-chip>
            </template>-->
          <template #item.email="{ value }">
            {{ value }}
          </template>
          <template #item.preferred_form_of_address="{ value }">
            {{ value }}
          </template>
          <template #item.gender="{ value }">
            {{ value }}
          </template>
          <template #item.date_of_birth="{ value }">
            {{ value }}
          </template>
          <template #item.estimated_age="{ value }">
            {{ value }}
          </template>
          <template #item.role="{ value }">
            {{ value }}
          </template>
          <template #item.experience="{ value }">
            {{ value }}
          </template>
          <template #item.organization\.name="{ item }">
            <v-chip small>{{ item.organization.name }}</v-chip>
          </template>
          <template #item.farms="{ value }">
            <v-row>
              <v-chip v-for="farm in value" :key="farm.id" class="mr-2" small>
                {{ farm.farm_name }}
              </v-chip>
            </v-row>
          </template>
            <template #item.created_at="{ value }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(value) }}</span>
                </template>
                <span>{{ formatDate(value) }}</span>
              </v-tooltip>
            </template>
            <template #item.updated_at="{ value }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(value) }}</span>
                </template>
                <span>{{ formatDate(value) }}</span>
              </v-tooltip>
            </template>
            <template #item.data-table-actions="{ item }">
              <raw-farmer-viewer :value="item.raw" />
            </template>
          </v-data-table-server>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"

import CasePopover from "@/case/CasePopover.vue"
import RawFarmerViewer from "@/farmer/RawFarmerViewer.vue"
import RouterUtils from "@/router/utils"
import FarmerPopover from "@/farmer/FarmerPopover.vue"
import TableFilterDialog from "@/farmer/TableFilterDialog.vue"

export default {
  name: "FarmerInstanceTable",

  components: {
    CasePopover,
    RawFarmerViewer,
    FarmerPopover,
    TableFilterDialog,
  },

  data() {
    return {
      headers: [
        { title: "Name", value: "name", sortable: true },
        { title: "Phone Number", value: "phone_number", sortable: true },
        { title: "Preferred Form Of Address", value: "preferred_form_of_address", sortable: false },
        { title: "Gender", value: "gender", sortable: true },
        { title: "Role", value: "role", sortable: true },
        { title: "Date Of Birth", value: "date_of_birth", sortable: true },
        { title: "Estimated Age", value: "estimated_age", sortable: true },
        { title: "Experience", value: "experience", sortable: true },
        { title: "Farms", value: "farms", sortable: false },
        { title: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
  },

  computed: {
    ...mapFields("farmer", [
      "instanceTable.loading",
      "instanceTable.options.descending",
      "instanceTable.options.filters",
      "instanceTable.options.filters.farmer",
      "instanceTable.options.itemsPerPage",
      "instanceTable.options.page",
      // "instanceTable.options.q",
      "instanceTable.options.sortBy",
      "instanceTable.rows.items",
      "instanceTable.rows.total",
    ]),
    ...mapFields("auth", ["currentUser.projects"]),

    defaultUserProjects: {
      get() {
        let d = null
        if (this.projects) {
          let d = this.projects.filter((v) => v.default === true)
          return d.map((v) => v.project)
        }
        return d
      },
    },
  },

  methods: {
    ...mapActions("farmer", ["getAllInstances"]),
  },

  created() {
    this.filters = {
      ...this.filters,
      ...RouterUtils.deserializeFilters(this.$route.query),
      project: this.defaultUserProjects,
    }

    this.getAllInstances()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAllInstances()
      }
    )

    this.$watch(
      (vm) => [
        // vm.q,
        vm.sortBy,
        vm.itemsPerPage,
        vm.descending,
        vm.created_at,
        vm.project,
        vm.farmer,
      ],
      () => {
        this.page = 1
        RouterUtils.updateURLFilters(this.filters)
        this.getAllInstances()
      }
    )
  },
}
</script>

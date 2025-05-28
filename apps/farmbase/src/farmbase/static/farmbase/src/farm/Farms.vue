<template>
  <v-container fluid>
    <notes-drawer/>
    <!--    <v-row no-gutters>-->
    <!--      <v-col>-->
    <!--        <v-alert closable icon="mdi-barn" prominent text type="info">-->
    <!--          Farms are agricultural properties managed by your organization. You can track farm details,-->
    <!--          contacts, and notes for each farm.-->
    <!--        </v-alert>-->
    <!--      </v-col>-->
    <!--    </v-row>-->
    <v-row align="center" justify="space-between" no-gutters>
      <!--      <v-col cols="8">-->
      <!--        <settings-breadcrumbs v-model="project" />-->
      <!--      </v-col>-->
      <v-col class="text-right">
        <v-btn color="info" class="ml-2" @click="createEditShow()"> New</v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card variant="flat">
          <!--          <v-card-title>-->
          <!--            <v-text-field-->
          <!--              v-model="q"-->
          <!--              append-inner-icon="mdi-magnify"-->
          <!--              label="Search"-->
          <!--              single-line-->
          <!--              hide-details-->
          <!--              clearable-->
          <!--            />-->
          <!--          </v-card-title>-->
          <v-data-table-server
              :headers="headers"
              :items="items"
              :items-length="total || 0"
              v-model:page="page"
              v-model:items-per-page="itemsPerPage"
              v-model:sort-by="sortBy"
              v-model:sort-desc="descending"
              :loading="loading"
              loading-text="Loading... Please wait"
          >
            <template #item.farm_name="{ item }">
              <div class="font-weight-medium">{{ item.farm_name }}</div>
            </template>

            <template #item.location="{ item }">
              <location-popover
                  v-if="item.location"
                  :location="item.location"
                  :farm-name="item.farm_name"
              />
              <span v-else class="text-grey">No location</span>
            </template>

            <template #item.contacts="{ item }">
              <v-chip-group v-if="item.contacts && item.contacts.length > 0">
                <v-chip
                    v-for="contact in item.contacts"
                    :key="contact.id"
                    :color="getContactRoleColor(contact.role)"
                    size="small"
                    class="ma-1"
                    @click="navigateToContact(contact.id)"
                    style="cursor: pointer;"
                >
                  {{ contact.name }}
                </v-chip>
              </v-chip-group>
              <span v-else class="text-grey">No contacts</span>
            </template>

            <template #item.data-table-actions="{ item }">
              <div class="d-flex align-center">
                <v-tooltip location="top">
                  <template #activator="{ props }">
                    <v-btn
                        icon
                        variant="text"
                        color="primary"
                        size="small"
                        @click="showNotes(item)"
                        class="mr-2"
                        v-bind="props"
                    >
                      <v-icon>mdi-note</v-icon>
                    </v-btn>
                  </template>
                  <span>View Notes</span>
                </v-tooltip>
<!--                <raw-contact-viewer :value="item.raw"/>-->
              </div>

<!--              <v-menu location="right" origin="overlap">-->
<!--                <template #activator="{ props }">-->
<!--                  <v-btn icon variant="text" v-bind="props">-->
<!--                    <v-icon>mdi-dots-vertical</v-icon>-->
<!--                  </v-btn>-->
<!--                </template>-->
<!--                <v-list>-->
<!--                  <v-list-item @click="createEditShow(item)">-->
<!--                    <v-list-item-title>View / Edit</v-list-item-title>-->
<!--                  </v-list-item>-->
<!--                  <v-list-item @click="showNotes(item)">-->
<!--                    <v-list-item-title>Notes</v-list-item-title>-->
<!--                  </v-list-item>-->
<!--                </v-list>-->
<!--              </v-menu>-->
            </template>
          </v-data-table-server>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import {mapFields} from "vuex-map-fields"
import {mapActions} from "vuex"
import NotesDrawer from "./NotesDrawer.vue"
import LocationPopover from "./LocationPopover.vue"
import RawContactViewer from "@/contact/RawContactViewer.vue";

export default {
  name: "FarmsTable",
  components: {RawContactViewer, NotesDrawer, LocationPopover},
  props: {
    name: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
      headers: [
        {title: "Farm Name", value: "farm_name", align: "left", width: "25%"},
        {title: "Location", value: "location", sortable: false, width: "20%"},
        {title: "Contacts", value: "contacts", sortable: false, width: "45%"},
        {title: "", key: "data-table-actions", sortable: false, align: "end", width: "10%"},
      ],
    }
  },
  computed: {
    ...mapFields("farm", [
      "table.loading",
      "table.options.descending",
      "table.options.filters.project",
      "table.options.itemsPerPage",
      "table.options.page",
      "table.options.q",
      "table.options.sortBy",
      "table.rows.items",
      "table.rows.total",
    ]),
    ...mapFields("auth", ["currentUser.projects"]),
  },
  methods: {
    ...mapActions("farm", ["getAll", "createEditShow", "removeShow", "showNotes"]),
    getContactRoleColor(role) {
      switch (role?.toLowerCase()) {
        case "owner":
          return "success"
        case "worker":
          return "info"
        case "advisor":
          return "warning"
        default:
          return "grey"
      }
    },
    navigateToContact(contactId) {
      this.$router.push({
        name: "ContactInstanceTable",
        params: {organization: this.$route.params.organization},
        query: {contact_id: contactId}
      })
    },
  },
  created() {
    this.project = [{name: this.$route.query.project}]
    this.getAll()

    this.$watch(
        (vm) => [vm.page],
        () => {
          this.getAll()
        }
    )

    this.$watch(
        (vm) => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending, vm.project],
        () => {
          this.page = 1
          this.$router.push({query: {project: this.project[0].name}})
          this.getAll()
        }
    )
  },
}
</script>

<style>
.mdi-barn {
  color: white !important;
}
</style>
import { getField, updateField } from "vuex-map-fields"
import ContactEngagementApi from "@/contact/engagement/api"

const getDefaultSelectedState = () => {
  return {
    name: null,
    description: null,
    require_mfa: false,
    entity_type: null,
    message: null,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
}

const getters = {
  getField,
  tableOptions({ state }) {
    // format our filters
    return state.table.options
  },
}

const actions = {
  save({ commit, state }) {
    commit("SET_SELECTED_LOADING", true)
    console.log("%O", state.selected)
    if (!state.selected.id) {
      return ContactEngagementApi.create(state.selected)
        .then((resp) => {
          commit(
            "notification_backend/addBeNotification",
            { text: "Contact engagement created successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
          commit("RESET_SELECTED")
          return resp.data
        })
        .catch((err) => {
          let errorText = err.response.data.detail.map(({ msg }) => msg).join(" ")
          commit(
            "notification_backend/addBeNotification",
            { text: `Error trying to save: ${errorText}`, type: "exception" },
            { root: true }
          )
          commit("RESET_SELECTED")
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return ContactEngagementApi.update(state.selected.id, state.selected)
        .then(() => {
          commit(
            "notification_backend/addBeNotification",
            { text: "Contact engagement updated successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
        .catch((err) => {
          let errorText = err.response.data.detail.map(({ msg }) => msg).join(" ")
          commit(
            "notification_backend/addBeNotification",
            { text: `Error trying to save: ${errorText}`, type: "exception" },
            { root: true }
          )
          commit("RESET_SELECTED")
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  createEditShow({ commit }, contact) {
    if (contact) {
      commit("SET_SELECTED", contact)
    }
    commit("SET_DIALOG_CREATE_EDIT", true)
  },
  closeCreateEditDialog({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
}

const mutations = {
  updateField,
  SET_SELECTED(state, value) {
    state.selected = Object.assign(state.selected, value)
  },
  SET_SELECTED_LOADING(state, value) {
    state.selected.loading = value
  },
  SET_TABLE_LOADING(state, value) {
    state.table.loading = value
  },
  SET_TABLE_ROWS(state, value) {
    state.table.rows = value
  },

  RESET_SELECTED(state) {
    // do not reset project
    let project = state.selected.project
    state.selected = { ...getDefaultSelectedState() }
    state.selected.project = project
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}

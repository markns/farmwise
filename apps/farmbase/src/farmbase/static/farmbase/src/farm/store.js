import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import FarmApi from "@/farm/api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    farm_name: null,
    location: null,
    contacts: [],
    loading: false,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showCreateEdit: false,
    showRemove: false,
    showNotes: false,
  },
  table: {
    rows: {
      items: [],
      total: null,
    },
    options: {
      filters: {},
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["farm_name"],
      descending: [false],
    },
    loading: false,
  },
  notes: {
    items: [],
    total: null,
    loading: false,
  },
}

const getters = {
  getField,
  tableOptions({ state }) {
    return state.table.options
  },
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "farm")
    return FarmApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  get({ commit, state }) {
    return FarmApi.get(state.selected.id).then((response) => {
      commit("SET_SELECTED", response.data)
    })
  },
  getNotes: debounce(({ commit, state }) => {
    if (!state.selected.id) return
    commit("SET_NOTES_LOADING", "primary")
    return FarmApi.getNotes(state.selected.id)
      .then((response) => {
        commit("SET_NOTES_LOADING", false)
        commit("SET_NOTES", response.data)
      })
      .catch(() => {
        commit("SET_NOTES_LOADING", false)
      })
  }, 500),
  createEditShow({ commit }, farm) {
    if (farm) {
      commit("SET_SELECTED", farm)
    }
    commit("SET_DIALOG_CREATE_EDIT", true)
  },
  showNotes({ commit, dispatch }, farm) {
    if (farm) {
      commit("SET_SELECTED", farm)
    }
    commit("SET_DIALOG_NOTES", true)
    dispatch("getNotes")
  },
  removeShow({ commit }, farm) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", farm)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  closeNotes({ commit }) {
    commit("SET_DIALOG_NOTES", false)
    commit("RESET_SELECTED")
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return FarmApi.create(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Farm created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return FarmApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Farm updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch }) {
    return FarmApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Farm deleted successfully.", type: "success" },
        { root: true }
      )
    })
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
  SET_NOTES_LOADING(state, value) {
    state.notes.loading = value
  },
  SET_NOTES(state, value) {
    state.notes.items = value.items
    state.notes.total = value.total
  },
  SET_DIALOG_CREATE_EDIT(state, value) {
    state.dialogs.showCreateEdit = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showRemove = value
  },
  SET_DIALOG_NOTES(state, value) {
    state.dialogs.showNotes = value
  },
  RESET_SELECTED(state) {
    state.selected = { ...getDefaultSelectedState() }
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
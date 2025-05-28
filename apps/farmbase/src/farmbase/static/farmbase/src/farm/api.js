import API from "@/api"

const resource = "/farms"

export default {
  getAll(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  get(farmId) {
    return API.get(`${resource}/${farmId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(farmId, payload) {
    return API.put(`${resource}/${farmId}`, payload)
  },

  delete(farmId) {
    return API.delete(`${resource}/${farmId}`)
  },

  getNotes(farmId, options = {}) {
    return API.get("/notes", {
      params: { farm_id: farmId, ...options },
    })
  },
}
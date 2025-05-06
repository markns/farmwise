import API from "@/api"

const resource = "/farmers/filters"

export default {
  getAll(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  get(farmerFilterId) {
    return API.get(`${resource}/${farmerFilterId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(farmerFilterId, payload) {
    return API.put(`${resource}/${farmerFilterId}`, payload)
  },

  delete(farmerFilterId) {
    return API.delete(`${resource}/${farmerFilterId}`)
  },
}

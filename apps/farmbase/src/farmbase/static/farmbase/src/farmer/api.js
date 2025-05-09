import API from "@/api"

const resource = "/contacts"

export default {
  getAll(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  get(farmerId) {
    return API.get(`${resource}/${farmerId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(farmerId, payload) {
    return API.put(`${resource}/${farmerId}`, payload)
  },

  delete(farmerId) {
    return API.delete(`${resource}/${farmerId}`)
  },

  getAllFilters(options) {
    return API.get(`${resource}/filters`, {
      params: { ...options },
    })
  },

  getAllInstances(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  // getInstances(farmerId) {
  //   return API.get(`${resource}/${farmerId}`)
  // },

  getInstance(farmerId, instanceId) {
    return API.get(`${resource}/${farmerId}/${instanceId}`)
  },
}

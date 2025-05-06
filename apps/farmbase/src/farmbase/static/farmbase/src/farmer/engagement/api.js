import API from "@/api"

const resource = "/farmers/engagements"

export default {
  getAll(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  get(farmerEngagementId) {
    return API.get(`${resource}/${farmerEngagementId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(farmerEngagementId, payload) {
    return API.put(`${resource}/${farmerEngagementId}`, payload)
  },

  delete(farmerEngagementId) {
    return API.delete(`${resource}/${farmerEngagementId}`)
  },
}

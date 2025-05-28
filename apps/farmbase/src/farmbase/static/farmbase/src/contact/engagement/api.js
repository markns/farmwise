import API from "@/api"

const resource = "/contacts/engagements"

export default {
  getAll(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  get(contactEngagementId) {
    return API.get(`${resource}/${contactEngagementId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(contactEngagementId, payload) {
    return API.put(`${resource}/${contactEngagementId}`, payload)
  },

  delete(contactEngagementId) {
    return API.delete(`${resource}/${contactEngagementId}`)
  },
}

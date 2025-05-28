import API from "@/api"

const resource = "/contacts/filters"

export default {
  getAll(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  get(contactFilterId) {
    return API.get(`${resource}/${contactFilterId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(contactFilterId, payload) {
    return API.put(`${resource}/${contactFilterId}`, payload)
  },

  delete(contactFilterId) {
    return API.delete(`${resource}/${contactFilterId}`)
  },
}

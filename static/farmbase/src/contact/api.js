import API from "@/api"

const resource = "/contacts"

export default {
  getAll(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  get(contactId) {
    return API.get(`${resource}/${contactId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(contactId, payload) {
    return API.put(`${resource}/${contactId}`, payload)
  },

  delete(contactId) {
    return API.delete(`${resource}/${contactId}`)
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

  // getInstances(contactId) {
  //   return API.get(`${resource}/${contactId}`)
  // },

  getInstance(contactId, instanceId) {
    return API.get(`${resource}/${contactId}/${instanceId}`)
  },
}

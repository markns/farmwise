import store from "@/store"
import UserApi from "./api"

function load() {
  return UserApi.getUserInfo().then(function (response) {
  })
}

export default {
  load,
}

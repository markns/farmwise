import {createStore} from "vuex"

import app from "@/app/store"
import auth from "@/auth/store"
import definition from "@/definition/store"
import entity from "@/entity/store"
import entity_type from "@/entity_type/store"
import forms from "@/forms/store"
import forms_table from "@/forms/table/store"
import forms_type from "@/forms/types/store"
import individual from "@/individual/store"
import notification from "@/notification/store"
import notification_backend from "@/app/notificationStore"
import organization from "@/organization/store"
import playground from "@/entity_type/playground/store"
import plugin from "@/plugin/store"
import query from "@/data/query/store"
import search from "@/search/store"
import contact from "@/contact/store"
import farm from "@/farm/store"

export default createStore({
    modules: {
        app,
        auth,
        definition,
        entity,
        entity_type,
        forms,
        forms_table,
        forms_type,
        individual,
        notification,
        notification_backend,
        organization,
        playground,
        plugin,
        query,
        search,
        contact,
        farm,
    },
})

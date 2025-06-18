import { DefaultLayout, DashboardLayout, BasicLayout } from "@/components/layouts"

const registrationEnabled =
  import.meta.env.VITE_DISPATCH_AUTH_REGISTRATION_ENABLED === "false" ? false : true

const withPrefix = (prefix, routes) =>
  routes.map((route) => {
    route.path = prefix + route.path
    return route
  })

const authPages = [
  {
    path: "login",
    name: "BasicLogin",
    component: () => import("@/auth/Login.vue"),
  },
]

if (registrationEnabled) {
  authPages.push({
    path: "register",
    name: "BasicRegister",
    component: () => import("@/auth/Register.vue"),
  })
}

export const publicRoute = [
  {
    path: "/:organization/auth/",
    component: BasicLayout,
    meta: { title: "Auth", icon: "mdi-view-comfy-outline", group: "auth" },
    children: authPages,
  },
  {
    path: "/404",
    name: "404",
    meta: { title: "Not Found" },
    component: () => import("@/views/error/NotFound.vue"),
  },
  {
    path: "/500",
    name: "500",
    meta: { title: "Server Error" },
    component: () => import("@/views/error/Error.vue"),
  },
  {
    path: "/implicit/callback",
    name: "PKCEImplicitlyCallback",
    meta: { requiresAuth: true },
  },
  {
    path: "/:pathMatch(.*)*",
    meta: { title: "Dispatch" },
    component: () => import("@/views/error/NotFound.vue"),
  },
]

// NOTE: The order in which routes are added to the list matters when evaluated. For example, /incidents/report will take precedence over /incidents/:name.
export const protectedRoute = [
  {
    path: "/",
    meta: { requiresAuth: true },
    redirect: {
      name: "IncidentTable",
      params: { organization: "default" },
    },
  },
  ...withPrefix("/:organization/", [
    {
      path: "mfa",
      name: "mfa",
      meta: { title: "Dispatch Mfa", requiresAuth: true },
      component: () => import("@/auth/Mfa.vue"),
    },

    {
      path: "dashboards",
      component: DashboardLayout,
      name: "dashboards",
      redirect: { name: "FarmsTable" },
      meta: {
        title: "Dashboards",
        group: "dashboard",
        icon: "mdi-monitor-dashboard",
        menu: true,
        requiresAuth: true,
      },
      children: [

      ],
    },

    {
      path: "farms",
      component: DefaultLayout,
      name: "farms",
      meta: {
        title: "Farms",
        icon: "mdi-barn",
        group: "farms",
        requiresAuth: true,
        menu: true,
        showEditSheet: false,
      },
      redirect: { name: "FarmsTable" },
      children: [
        {
          path: "/:organization/farms",
          name: "FarmsTable",
          meta: { title: "List" },
          component: () => import("@/farm/Farms.vue"),
        },
      ],
    },
    {
      path: "contacts",
      component: DefaultLayout,
      name: "contacts",
      meta: {
        title: "Contacts",
        icon: "mdi-account",
        group: "contacts",
        requiresAuth: true,
        menu: true,
        showEditSheet: false,
      },
      redirect: { name: "ContactInstanceTable" },
      children: [
        {
          path: "/:organization/contacts",
          name: "ContactInstanceTable",
          meta: { title: "List" },
          component: () => import("@/contact/TableInstance.vue"),
        },
      ],
    },

    {
      path: "data",
      component: DefaultLayout,
      name: "Data",
      // redirect: { name: "QuerySummaryTable" },
      meta: {
        title: "Data",
        icon: "mdi-database",
        group: "data",
        menu: true,
        requiresAuth: true,
      },
      children: [

      ],
    },

    {
      path: "settings",
      component: DefaultLayout,
      name: "settings",
      meta: {
        title: "Settings",
        icon: "mdi-cog",
        group: "settings",
        menu: true,
        requiresAuth: true,
      },
      redirect: { name: "OrganizationMemberTable" },
      children: [
        {
          path: "members",
          name: "OrganizationMemberTable",
          meta: { title: "Members", subMenu: "organization", group: "organization" },
          component: () => import("@/organization/OrganizationMemberTable.vue"),
        },
      ],
    },
    {
      path: "search",
      name: "GlobalSearch",
      component: DefaultLayout,
      meta: {
        title: "Search",
        icon: "mdi-view-comfy-outline",
        group: "search",
        noMenu: true,
        requiresAuth: true,
      },
      redirect: { name: "ResultList" },
      children: [
        {
          path: "results",
          meta: { name: "Results" },
          component: () => import("@/search/ResultList.vue"),
          name: "ResultList",
          props: true,
        },
      ],
    },
  ]),
]

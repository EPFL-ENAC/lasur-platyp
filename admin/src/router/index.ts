import { defineRouter } from '#q-app'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router'
import routes from './routes'
import { isFirstVisit, markVisited } from '@/utils/localStorage'
import { useAuthStore } from '@/stores/auth'

// Auth state read synchronously in the navigation guard: the router is created
// before Pinia installs in the boot sequence, so the store is resolved lazily.
function authIsAuthenticated(): boolean {
  try {
    return useAuthStore().isAuthenticated
  } catch {
    return false
  }
}

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter(function (/* { store, ssrContext } */) {
  const createHistory = import.meta.env.QUASAR_SERVER
    ? createMemoryHistory
    : import.meta.env.QUASAR_VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(import.meta.env.QUASAR_VUE_ROUTER_BASE),
  })

  Router.beforeEach((to, from, next) => {
    const docUrl = '/doc'

    // First-visit redirect lives in MainLayout's authenticated flow (this guard
    // runs before auth resolves, and redirecting while unauthenticated creates a
    // blank /doc hop that poisons the flag — see MainLayout.vue).
    // Leaving /doc only counts as "read the doc" when authenticated: the
    // unauthenticated bounce out of a blank /doc must not mark the visit.
    if (isFirstVisit() && to.path === docUrl && from.path !== docUrl && authIsAuthenticated()) {
      next()
      return
    }
    if (from.path === docUrl && authIsAuthenticated()) {
      markVisited()
    }
    next()
  })

  return Router
})

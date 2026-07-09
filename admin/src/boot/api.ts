import { boot } from 'quasar/wrappers'
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import Keycloak from 'keycloak-js'
import { notifyWarning, isSessionExpiredError } from 'src/utils/notify'

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance
    $api: AxiosInstance
  }
}

interface CustomWindow extends Window {
  env: {
    KEYCLOAK_URL?: string
    KEYCLOAK_REALM?: string
    AUTH_CLIENT_ID: string
    API_URL: string
    API_PATH: string
    COLLECT_URL: string
  }
}

const appEnv = (window as unknown as CustomWindow).env

const keycloak = new Keycloak({
  url: appEnv.KEYCLOAK_URL || 'https://enac-it-sso.epfl.ch/',
  realm: appEnv.KEYCLOAK_REALM || 'LASUR',
  clientId: appEnv.AUTH_CLIENT_ID,
})
const baseUrl = `${appEnv.API_URL}${appEnv.API_PATH}`
const api = axios.create({
  baseURL: baseUrl,
})
const collectUrl = appEnv.COLLECT_URL

// If a request slips through with a stale token despite updateToken()
// (e.g. clock skew, or a request racing a refresh), the backend rejects it
// with an "Expired at ..." detail message. Catch that here so the user is
// sent to sign in instead of being left stuck re-sending a dead token.
function isExpiredTokenError(error: unknown): boolean {
  if (!axios.isAxiosError(error)) return false
  const status = error.response?.status
  if (status !== 401 && status !== 403 && status !== 404) return false
  return isSessionExpiredError(error)
}

export default boot(({ app, router }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API

  api.interceptors.response.use(
    (response) => response,
    (error: unknown) => {
      if (isExpiredTokenError(error)) {
        const authStore = useAuthStore()
        authStore.profile = undefined
        authStore.realmRoles = []
        if (router.currentRoute.value.path !== '/signin') {
          notifyWarning('error.session_expired')
          void router.push('/signin')
        }
      }
      return Promise.reject(error)
    },
  )
})

export { api, baseUrl, keycloak, collectUrl }

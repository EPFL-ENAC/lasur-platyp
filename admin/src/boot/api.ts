import { boot } from 'quasar/wrappers'
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import Keycloak from 'keycloak-js'

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

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
})

export { api, baseUrl, keycloak, collectUrl }

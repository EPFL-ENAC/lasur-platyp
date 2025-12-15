import { defineStore } from 'pinia'
import { keycloak } from 'src/boot/api'
import type { KeycloakProfile } from 'keycloak-js'

export const useAuthStore = defineStore('auth', () => {
  const profile = ref<KeycloakProfile>()
  const realmRoles = ref<string[]>([])
  const isAuthenticated = computed(() => profile.value !== undefined)
  const isAdmin = computed(() => realmRoles.value.includes('platyp-admin'))
  const initialized = ref(false)

  const accessToken = computed(() => keycloak.token)

  async function init() {
    if (isAuthenticated.value || initialized.value) return Promise.resolve(true)
    profile.value = undefined
    realmRoles.value = []
    return keycloak
      .init({
        onLoad: 'check-sso', // Optional: 'login-required' forces login right away, 'check-sso' checks if the user is already logged in.
      })
      .then((authenticated: boolean) => {
        initialized.value = true
        if (authenticated) {
          realmRoles.value = keycloak.tokenParsed?.realm_access?.roles || []
          return keycloak.loadUserProfile().then((prof: KeycloakProfile) => {
            profile.value = prof
            return authenticated
          })
        } else {
          return authenticated
        }
      })
  }

  async function login() {
    if (isAuthenticated.value) return
    // Ensure keycloak is initialized before attempting login
    if (!keycloak.authenticated && !keycloak.didInitialize) {
      await init()
    }
    // redirects to keycloak login page
    return keycloak.login()
  }

  async function logout() {
    if (!keycloak.didInitialize) {
      // If keycloak was never initialized, just clear local state
      profile.value = undefined
      realmRoles.value = []
      return
    }
    if (!isAuthenticated.value) return
    return keycloak
      .logout({
        redirectUri: window.location.origin,
      })
      .then(() => {
        profile.value = undefined
        realmRoles.value = []
      })
  }

  async function updateToken() {
    //return Promise.resolve(true);
    return keycloak.updateToken(30).catch(() => {
      console.error('Failed to refresh token')
      return logout().finally(() => Promise.reject('Failed to refresh token'))
    })
  }

  return {
    isAuthenticated,
    isAdmin,
    profile,
    realmRoles,
    accessToken,
    keycloak,
    initialized,
    init,
    login,
    logout,
    updateToken,
  }
})

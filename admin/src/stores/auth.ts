import { defineStore } from 'pinia'
import { keycloak } from 'src/boot/api'
import type { KeycloakProfile } from 'keycloak-js'
import type { Company } from 'src/models'

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
    try {
      const authenticated = await keycloak.init({
        onLoad: 'check-sso', // Optional: 'login-required' forces login right away, 'check-sso' checks if the user is already logged in.
        pkceMethod: 'S256',
        checkLoginIframe: false,
      })

      initialized.value = true
      if (authenticated) {
        realmRoles.value = keycloak.tokenParsed?.realm_access?.roles || []
        profile.value = await keycloak.loadUserProfile()
        keycloak.onTokenExpired = () => void updateToken()
      }
      return authenticated
    } catch (error) {
      console.error('Keycloak initialization failed', error)
      initialized.value = true
      return false
    }
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

  /**
   * Update token (refresh if needed)
   */
  async function updateToken(minValidity = 30) {
    try {
      await keycloak.updateToken(minValidity)
      return keycloak.token
    } catch (error) {
      console.error('Token refresh error:', error)
      profile.value = undefined
      realmRoles.value = []
      return null
    }
  }

  function isAdminOfThisCompany(company: Company) {
    if (isAdmin.value) return true
    if (!company.administrators || !profile.value?.email) return false

    return company.administrators?.includes(profile.value.email)
  }

  function roleInThisCompany(company: Company): 'admin' | 'mobility_advisor' | 'none' {
    if (isAdminOfThisCompany(company)) return 'admin'
    if (company.mobility_advisors?.includes(profile.value?.email || '')) return 'mobility_advisor'
    return 'none'
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
    isAdminOfThisCompany,
    roleInThisCompany,
  }
})

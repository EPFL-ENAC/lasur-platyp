window.env = {
  API_URL: 'http://localhost:8000',
  API_PATH: '',
  // Keycloak (defaults: https://enac-it-sso2.epfl.ch/, realm external)
  // KEYCLOAK_URL: 'https://enac-it-sso2.epfl.ch/',
  // KEYCLOAK_REALM: 'external',
  // Keycloak client ID of the admin app
  AUTH_CLIENT_ID: 'platyp-local-admin',
  // Keycloak client ID of the backend, which holds the app roles (client roles). Unset when the
  // app roles are realm roles (prod)
  AUTH_API_CLIENT_ID: 'platyp-local-api',
  COLLECT_URL: 'http://localhost:9001',
}

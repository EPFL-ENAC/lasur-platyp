# LASUR - PLATYP

Plateforme typologie des choix modaux

# Development

## Environment 

What the .env file should look like for the PLATYP backend:

```sh
# Postgres
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=platyp
DB_PREFIX=postgresql+asyncpg
# FastAPI prefix
PATH_PREFIX=
# Keycloak
KEYCLOAK_REALM=LASUR
KEYCLOAK_URL=https://enac-it-sso.epfl.ch
KEYCLOAK_API_ID=local-api
KEYCLOAK_API_SECRET=xxxxx
# LASUR web services
LASUR_API_URL=https://lasur-ws.epfl.ch
LASUR_API_KEY=xxxxx
```

Note: the API Keycloak client is used to manage local users. The required role for this client are:
* `realm-management` manage-users
* `realm-management` query-users	
* `realm-management` view-users
* `realm-management` view-realm	


## Manage external services

Local Postgres database:

```sh
make run-db
```

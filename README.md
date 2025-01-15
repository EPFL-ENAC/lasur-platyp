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
```
## Manage external services

Local Postgres database:

```sh
make run-db
```

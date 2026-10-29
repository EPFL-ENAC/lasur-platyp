# Keycloak users migration

`migrate-users.sh` (export, transform, dry-run) and the partial import of the Keycloak admin console move the Platyp users of the local and dev deployments from the legacy Keycloak (https://enac-it-sso.epfl.ch, realm `LASUR`) to the shared realm `external` of https://enac-it-sso2.epfl.ch (see #567). Prod keeps its own Keycloak with realm roles, nothing to migrate.

What is kept and what changes:

- **User id**: kept (the token `sub`). Platyp does not refer to it though: company permissions are by email, `created_by`/`updated_by` hold the username.
- **Password hashes**: kept, so users sign in with their current password. OTP credentials and required actions are kept too.
- **Users**: the users with the `platyp-user` realm role, the Platyp users (as listed in the admin app).
- **Roles**: the `platyp-*` realm roles of the legacy realm become client roles of the backend client of the target environment (e.g. `platyp-dev-api`). Users also get the target realm's default role (`default-roles-external`).
- **Dropped**: users without the `platyp-user` role (not exported), users without password (e.g. signing in with EPFL LDAP: their password is not in Keycloak), service accounts, groups, consents, and links to identity providers or user federation (LDAP) of the legacy realm.

## Prerequisites

- `docker` and `jq`. `kcadm.sh` runs in the Keycloak docker image, nothing to install.
- A shell in the legacy Keycloak container (e.g. `kubectl exec` on its pod), for the export. The password hashes are not available through the admin API.
- An admin account of the target realm, with the `realm-management` roles `manage-realm` (the partial import requires it) and, for the dry-run, `view-realm`, `view-clients`, `view-users` and `query-users`. Or an admin of the `master` realm (`KC_LOGIN_REALM=master` for the dry-run).
- For the dry-run, a client to log in with. The default is `admin-cli`, but Keycloak only grants the admin roles that are in the scope of the client used: if `admin-cli` of the target realm has "Full scope allowed" off, every call fails with `HTTP 403` (the token has no roles). Then add a client, e.g. `platyp-migration`: public, "Direct access grants" on, "Standard flow" off, "Full scope allowed" on (Client scopes > Dedicated scope > Scope), set `KC_CLIENT=platyp-migration`, and delete it after the migration.
- In the target realm, for each environment:
  - the backend client (e.g. `platyp-dev-api`) with the client roles `platyp-admin` and `platyp-user`,
  - the admin app client (e.g. `platyp-dev-admin`).

## Steps

Run the script from the `migration/` folder: it is git-ignored, and the exported files contain password hashes.

```bash
cd migration
```

### 1. Export the legacy realm

`kc.sh export` runs in the legacy Keycloak container, where it finds the database settings. `KC_EXEC` is the command prefix that runs a command in that container:

```bash
KC_EXEC="kubectl exec -i -n <namespace> <keycloak pod> --" ../keycloak/migrate-users.sh export LASUR > LASUR.json
```

The legacy server is deployed with the Bitnami chart `keycloak-21.0.2` (Keycloak 24), `kc.sh` is expected at `/opt/bitnami/keycloak/bin/kc.sh`. Check the image of the pod (`kubectl get pod <pod> -n <namespace> -o jsonpath='{..image}'`) and set `KC_SH` if it differs.

The export goes to a directory in the pod, with the users in pages of 100 local users, one transaction each. A single file export would list all the users of the legacy realm's user federation (EPFL LDAP) in one transaction, which times out after 5 minutes. With pages, LDAP is only queried for a few users on the last page (Keycloak may import these few into the legacy database, as on their sign-in).

The export stays in the container (`/tmp/LASUR-export`), and each users file is fetched by a separate `KC_EXEC` and checked by `jq`: large outputs of `kubectl exec` can be truncated (`jq: parse error: Unfinished JSON term`). On such a failure, run the same export command again: it finds the export and only fetches the files, instead of exporting again (about 10 minutes for LASUR, because of its EPFL LDAP user federation). When done, or to start a new export, remove it (it holds the password hashes):

```bash
KC_EXEC="kubectl exec -i -n <namespace> <keycloak pod> --" ../keycloak/migrate-users.sh cleanup LASUR
```

Only the users with the `platyp-user` realm role are kept: the exported users are filtered as they are received, the other users and their password hashes are not written.

The export runs while the server is running (a few seconds). It starts a second Keycloak process in the pod, which must stay out of the server's cache cluster (JGroups `kubernetes` stack): the script makes it discover no peer and bind another port than the server's (7800), see `KC_EXPORT_JAVA_OPTS`. It only reads the database.

### 2. Transform

Offline. Keeps the users having the `platyp-user` realm role (all of them after the export) and a password, and converts their `platyp-*` realm roles to client roles of the given backend client:

```bash
../keycloak/migrate-users.sh transform LASUR.json platyp-dev-api > users-dev.json
```

It reports on stderr what needs attention:

- users not migrated (no `platyp-user` role),
- users not migrated (no password): e.g. signing in with EPFL LDAP, whose password is not in Keycloak,
- migrated users whose links to an identity provider or to user federation are dropped (they keep their password),
- users with OTP: their codes keep working only if the OTP policy (algorithm, digits, period) of the target realm is the same as the legacy one.

### 3. Dry-run

Read only. Prompts for the admin password.

```bash
KC_USER=<admin> ../keycloak/migrate-users.sh dry-run users-dev.json platyp-dev-api
```

It reports:

- missing backend client, client roles or default role in the target realm,
- for each user:
  - **new**: will be imported,
  - **existing**: a user with the same id is already there (e.g. imported for another environment's client): the import skips it, add the client roles of this environment by hand (see below),
  - **COLLISION**: another user of the realm has the same username or email (case-insensitive): remove it from the file (see below), it is not migrated.

### 4. Import in the admin console

1. In the admin console of the target realm (`external`): **Realm settings** > **Action** (top right) > **Partial import**.
2. Choose `users-dev.json`. The dialog shows the number of users.
3. Set **If a resource exists** to **Skip**, then **Import**.
4. The result lists each user as **Added** or **Skipped**.

Before importing, remove the collisions of the dry-run from the file:

```bash
jq '.users |= map(select(.username | IN("<username>", "<username>") | not))' users-dev.json > users-dev-import.json
```

Keycloak's partial import fails as a whole (generic error, nothing imported) on a user whose email already exists with another username. Without the dry-run, find that user in the target realm (Users, search by email) and remove it from the file.

A skipped user is not updated: for the **existing** users of the dry-run (same id, e.g. imported for `platyp-local-api` before), add the client roles of this environment by hand (Users > user > **Role mapping** > **Assign role** > filter by clients), as listed in their `clientRoles` in the file:

```bash
jq -r '.users[] | "\(.username): \(.clientRoles[] | join(", "))"' users-dev.json
```

### 5. After the import

- Check the users in the admin app.
- For a collision, assign the client roles to the existing account of the target realm (Users > user > **Role mapping**), or the user signs in with it and joins the app (when sign-up is enabled). Nothing else to move: company permissions are by email (check the email is the same), `created_by`/`updated_by` keep the legacy username.
- Run `cleanup LASUR` if not done yet (export in the legacy container), delete `LASUR.json`, `users-*.json` and `.kcadm.config` (it holds the admin tokens) when done.

## Settings

Environment variables, with their defaults:

| Variable | Default | Description |
| --- | --- | --- |
| `KC_URL` | `https://enac-it-sso2.epfl.ch` | Target Keycloak |
| `KC_REALM` | `external` | Target realm |
| `KC_LOGIN_REALM` | `$KC_REALM` | Realm of the admin account, e.g. `master` |
| `KC_USER` | | Admin username (dry-run) |
| `KC_CLIENT` | `admin-cli` | Client to log in with (dry-run) |
| `KC_DEFAULT_ROLE` | `default-roles-$KC_REALM` | Realm role given to the imported users |
| `KC_IMAGE` | `quay.io/keycloak/keycloak:26.4` | Image running `kcadm.sh` (dry-run) |
| `KC_EXEC` | | Command prefix running a command in the legacy Keycloak container (export) |
| `KC_SH` | `/opt/bitnami/keycloak/bin/kc.sh` | `kc.sh` in the legacy Keycloak container (export) |
| `KC_EXPORT_JAVA_OPTS` | `-Djgroups.dns.query=export.invalid -Djgroups.bind.port=7801` | Java options of the export process, replace the pod's `JAVA_OPTS_APPEND` (export) |

## Tested

Locally, with a legacy Keycloak `bitnamilegacy/keycloak:24.0.2` on Postgres with the `ispn` cache and `kubernetes` stack (as the Bitnami chart) and a target Keycloak 26.4: after the partial import, the users sign in with their legacy password, the token `sub` is their legacy id and it has the client roles of the backend client. The export and the import into `external` of enac-it-sso2 were also run for the AREMA dev deployment (EPFL-ENAC/ALICE-ETHZ-AREMA#265), from which this script is taken. For Platyp, only the role names and the realm differ (the `transform` was checked offline).

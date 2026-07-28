from fastapi import HTTPException, status
from enacit4r_auth.services.auth import KeycloakService, User
from enacit4r_auth.services.admin import KeycloakAdminService
from api.config import config
from api.db import get_session
from api.services.authz import ACLService

ADMIN_ROLE = "platyp-admin"
USER_ROLE = "platyp-user"

kc_service = KeycloakService(config.KEYCLOAK_URL, config.KEYCLOAK_REALM,
                             config.KEYCLOAK_API_ID, config.KEYCLOAK_API_SECRET, ADMIN_ROLE)

kc_admin_service = KeycloakAdminService(config.KEYCLOAK_URL, config.KEYCLOAK_REALM,
                                        config.KEYCLOAK_API_ID, config.KEYCLOAK_API_SECRET, USER_ROLE)


def is_admin(user: User) -> bool:
    return ADMIN_ROLE in user.realm_roles


async def check_admin_or_perm(user: User, resource: str, permission: str):
    # check is admin
    if is_admin(user):
        return True
    # else check permission was granted
    async for session in get_session():
        acl_service = ACLService(session)
        permitted = await acl_service.check_user_permission(
            resource, permission, user.email)
        if permitted:
            return True
    return False


async def require_admin_or_perm(user: User, resource: str, permission: str):
    permitted = await check_admin_or_perm(user, resource, permission)
    if not permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised to perform this operation"
        )

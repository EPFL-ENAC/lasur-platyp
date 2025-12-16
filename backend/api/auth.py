from fastapi import HTTPException, status
from enacit4r_auth.services.auth import KeycloakService, User
from enacit4r_auth.services.admin import KeycloakAdminService
from api.config import config
from api.db import get_session
from api.services.authz import ACLService

kc_service = KeycloakService(config.KEYCLOAK_URL, config.KEYCLOAK_REALM,
                             config.KEYCLOAK_API_ID, config.KEYCLOAK_API_SECRET, "platyp-admin")

kc_admin_service = KeycloakAdminService(config.KEYCLOAK_URL, config.KEYCLOAK_REALM,
                                        config.KEYCLOAK_API_ID, config.KEYCLOAK_API_SECRET, "platyp-user")


async def check_admin_or_perm(user: User, resource: str, permission: str):
    # check is admin
    try:
        checker = kc_service.require_admin()
        await checker(user)
        return True
    except Exception as e:
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

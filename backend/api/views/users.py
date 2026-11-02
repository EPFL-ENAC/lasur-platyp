from fastapi import APIRouter, Depends, HTTPException, Request
from keycloak.exceptions import KeycloakError
from pydantic import BaseModel
from api.db import get_session, AsyncSession
from api.models.users import AppUser, AppUserListItem, AppUserResult, AppUserDraft, AppUserPassword
from api.services.settings import SettingsService
from api.auth import USER_ROLE, kc_service, User, kc_admin_service
from api.config import config
from api.rate_limit import limiter

router = APIRouter()


class SignupSetting(BaseModel):
    enabled: bool


def get_identity_providers(id: str) -> list[str]:
    """Get the identity providers (e.g. github, google) the user signs in with"""
    return [link["identityProvider"] for link in kc_admin_service.kc_admin.get_user_social_logins(id)]


async def get_app_user(id: str) -> AppUser:
    """Get a user of the app by id or name. In a realm shared with other apps (client roles),
    the users without the app user role are not users of the app."""
    app_user = await kc_admin_service.get_user(id)
    if config.KEYCLOAK_CLIENT_ROLES and USER_ROLE not in app_user.roles:
        raise HTTPException(status_code=404, detail="User not found")
    return app_user


@router.get("/", response_model=AppUserResult, response_model_exclude_none=True)
async def find(user: User = Depends(kc_service.require_admin())):
    """Get users"""
    # ponytail: one Keycloak call per user, as for the roles in enacit4r-auth
    app_users = [
        AppUserListItem(**app_user.model_dump(), identity_providers=get_identity_providers(app_user.id))
        for app_user in await kc_admin_service.get_users()
    ]
    return AppUserResult(
        skip=0, limit=len(app_users), total=len(app_users), data=app_users
    )


@router.get("/_signup", response_model=SignupSetting)
async def get_signup(session: AsyncSession = Depends(get_session)) -> SignupSetting:
    """Whether user self-registration is enabled (public)"""
    return SignupSetting(enabled=await SettingsService(session).is_signup_enabled())


@router.put("/_signup", response_model=SignupSetting)
async def set_signup(
    payload: SignupSetting,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin()),
) -> SignupSetting:
    """Enable or disable user self-registration"""
    enabled = await SettingsService(session).set_signup_enabled(payload.enabled)
    return SignupSetting(enabled=enabled)


@router.get("/{id}", response_model=AppUser, response_model_exclude_none=True)
async def get(id: str, user: User = Depends(kc_service.require_admin())) -> AppUser:
    """Get a user by id or name"""
    return await get_app_user(id)


@router.delete("/{id}", response_model=AppUser, response_model_exclude_none=True)
async def delete(id: str, user: User = Depends(kc_service.require_admin())):
    """Delete a user by id or name. In a realm shared with other apps (client roles),
    the account is kept and only the app roles are removed."""
    app_user = await get_app_user(id)
    if not config.KEYCLOAK_CLIENT_ROLES:
        return await kc_admin_service.delete_user(app_user.id)
    kc_admin = kc_admin_service.kc_admin
    client_id = kc_admin.get_client_id(config.KEYCLOAK_API_ID)
    kc_admin.delete_client_roles_of_user(
        app_user.id, client_id, kc_admin.get_client_roles_of_user(app_user.id, client_id))
    return app_user


@router.post("/", response_model=AppUser, response_model_exclude_none=True)
async def create(
    item: AppUserDraft, user: User = Depends(kc_service.require_admin())
) -> AppUser:
    """Create a user"""
    actions = ["UPDATE_PASSWORD"]
    if config.KEYCLOAK_TOTP:
        actions.append("CONFIGURE_TOTP")
    if kc_admin_service.check_valid_password(item.password) is False:
        raise HTTPException(
            status_code=400, detail="error.password_complexity_not_met")
    return await kc_admin_service.create_user(item, actions)


@router.post("/_register", response_model=AppUser, response_model_exclude_none=True)
@limiter.limit(config.RATE_LIMIT_USERS_REGISTER)
async def register(
    request: Request,
    item: AppUserDraft,
    session: AsyncSession = Depends(get_session),
) -> AppUser:
    """User self-registration"""
    if not await SettingsService(session).is_signup_enabled():
        raise HTTPException(status_code=403, detail="error.signup_disabled")
    # check user does not exist
    try:
        existing_user = await kc_admin_service.get_user(item.username)
    except KeycloakError as e:
        # Keycloak raises 404 when the user is not found, anything else is a real failure
        if e.response_code != 404:
            raise
        existing_user = None
    if existing_user:
        raise HTTPException(
            status_code=400, detail="error.registration_failed")

    if kc_admin_service.check_valid_password(item.password) is False:
        raise HTTPException(
            status_code=400, detail="error.password_complexity_not_met")
    new_user = AppUserDraft(
        username=item.username,
        email=item.email,
        first_name=item.first_name,
        last_name=item.last_name,
        password=item.password,
        enabled=True,
        email_verified=False,
    )
    actions = ["VERIFY_EMAIL"]
    if config.KEYCLOAK_TOTP:
        actions.append("CONFIGURE_TOTP")
    try:
        return await kc_admin_service.create_user(new_user, actions)
    except KeycloakError as e:
        # 409: username or email already taken
        if e.response_code == 409:
            raise HTTPException(
                status_code=400, detail="error.registration_failed")
        raise


@router.post("/_join", response_model=AppUser, response_model_exclude_none=True)
async def join(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info()),
) -> AppUser:
    """Signed-in user of the realm (e.g. registered for another app, or signed in
    with an identity provider) joins this app, as if signed up"""
    app_user = await kc_admin_service.get_user(user.id)
    if USER_ROLE in app_user.roles:
        return app_user
    if not await SettingsService(session).is_signup_enabled():
        raise HTTPException(status_code=403, detail="error.signup_disabled")
    app_user.roles = app_user.roles + [USER_ROLE]
    return await kc_admin_service.update_user(app_user)


@router.put("/{id}", response_model=AppUser, response_model_exclude_none=True)
async def update(
    id: str, item: AppUser, user: User = Depends(kc_service.require_admin())
) -> AppUser:
    """Update a user by id"""
    if id != item.id:
        raise Exception("id does not match")
    await get_app_user(id)
    return await kc_admin_service.update_user(item)


@router.put("/{id}/password")
async def update_password(
    id: str, payload: AppUserPassword, user: User = Depends(kc_service.require_admin())
) -> None:
    """Set a temporary user password by id"""
    if payload.password is None:
        raise Exception("password is required")
    app_user = await get_app_user(id)
    if get_identity_providers(app_user.id):
        raise HTTPException(status_code=400, detail="error.password_with_identity_provider")
    return await kc_admin_service.update_user_password(app_user.id, payload.password)

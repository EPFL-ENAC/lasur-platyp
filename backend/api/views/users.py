from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from api.db import get_session, AsyncSession
from api.models.users import AppUser, AppUserResult, AppUserDraft, AppUserPassword
from api.services.settings import SettingsService
from api.auth import kc_service, User, kc_admin_service
from api.config import config
from api.rate_limit import limiter

router = APIRouter()


class SignupSetting(BaseModel):
    enabled: bool


@router.get("/", response_model=AppUserResult, response_model_exclude_none=True)
async def find(user: User = Depends(kc_service.require_admin())):
    """Get users"""
    app_users = await kc_admin_service.get_users()
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
    return await kc_admin_service.get_user(id)


@router.delete("/{id}", response_model=AppUser, response_model_exclude_none=True)
async def delete(id: str, user: User = Depends(kc_service.require_admin())):
    """Delete a user by id or name"""
    return await kc_admin_service.delete_user(id)


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
    except Exception:
        # Keycloak raises when the user is not found
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
    return await kc_admin_service.create_user(new_user, actions)


@router.put("/{id}", response_model=AppUser, response_model_exclude_none=True)
async def update(
    id: str, item: AppUser, user: User = Depends(kc_service.require_admin())
) -> AppUser:
    """Update a user by id"""
    if id != item.id:
        raise Exception("id does not match")
    return await kc_admin_service.update_user(item)


@router.put("/{id}/password")
async def update_password(
    id: str, payload: AppUserPassword, user: User = Depends(kc_service.require_admin())
) -> None:
    """Set a temporary user password by id"""
    if payload.password is None:
        raise Exception("password is required")
    return await kc_admin_service.update_user_password(id, payload.password)

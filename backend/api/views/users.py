from fastapi import APIRouter, Depends
from api.services.users import UserService
from api.models.users import AppUser, AppUserResult, AppUserDraft, AppUserPassword
from api.auth import kc_service, User

router = APIRouter()


@router.get("/", response_model=AppUserResult, response_model_exclude_none=True)
async def find(user: User = Depends(kc_service.require_admin())):
    """Get users"""
    return await UserService().get_users()


@router.get("/{id}", response_model=AppUser, response_model_exclude_none=True)
async def get(id: str, user: User = Depends(kc_service.require_admin())) -> AppUser:
    """Get a user by id or name"""
    return await UserService().get_user(id)


@router.delete("/{id}", response_model=AppUser, response_model_exclude_none=True)
async def delete(id: str, user: User = Depends(kc_service.require_admin())):
    """Delete a user by id or name"""
    return await UserService().delete_user(id)


@router.post("/", response_model=AppUser, response_model_exclude_none=True)
async def create(item: AppUserDraft, user: User = Depends(kc_service.require_admin())) -> AppUser:
    """Create a user"""
    return await UserService().create_user(item)


@router.put("/{id}", response_model=AppUser, response_model_exclude_none=True)
async def update(
    id: str,
    item: AppUser,
    user: User = Depends(kc_service.require_admin())
) -> AppUser:
    """Update a user by id"""
    if id != item.id:
        raise Exception("id does not match")
    return await UserService().update_user(item)


@router.put("/{id}/password")
async def update(
    id: str,
    payload: AppUserPassword,
    user: User = Depends(kc_service.require_admin())
) -> None:
    """Set a temporary user password by id"""
    if payload.password is None:
        raise Exception("password is required")
    return await UserService().update_user_password(id, payload.password)

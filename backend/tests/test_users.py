from unittest.mock import AsyncMock, MagicMock

import pytest
from enacit4r_auth.models.auth import AppUser, User
from fastapi import HTTPException

from api import auth
from api.views import users


def make_app_user(roles: list[str]) -> AppUser:
    return AppUser(id="abc", username="test", email="test@me.com", email_verified=True,
                   first_name="Foo", last_name="Bar", enabled=True, totp=False, roles=roles)


def make_user(realm_roles: list[str] = [], client_roles: list[str] = []) -> User:
    return User(id="abc", username="test", email="test@me.com", first_name="Foo", last_name="Bar",
                realm_roles=realm_roles, client_roles=client_roles)


@pytest.fixture
def kc_admin(monkeypatch):
    kc_admin = MagicMock()
    kc_admin.get_user = AsyncMock()
    kc_admin.update_user = AsyncMock(side_effect=lambda app_user: app_user)
    kc_admin.delete_user = AsyncMock()
    kc_admin.update_user_password = AsyncMock()
    kc_admin.kc_admin.get_user_social_logins.return_value = []
    monkeypatch.setattr(users, "kc_admin_service", kc_admin)
    return kc_admin


@pytest.fixture
def client_roles(monkeypatch):
    monkeypatch.setattr(users.config, "KEYCLOAK_CLIENT_ROLES", True)


@pytest.fixture
def signup(monkeypatch):
    settings = MagicMock()
    settings.is_signup_enabled = AsyncMock(return_value=True)
    monkeypatch.setattr(users, "SettingsService", lambda session: settings)
    return settings


@pytest.mark.asyncio
async def test_join(kc_admin, signup):
    kc_admin.get_user.return_value = make_app_user(["other-role"])
    app_user = await users.join(MagicMock(), make_user())
    assert app_user.roles == ["other-role", "platyp-user"]
    kc_admin.update_user.assert_called_once()


@pytest.mark.asyncio
async def test_join_already_member(kc_admin, signup):
    signup.is_signup_enabled.return_value = False
    kc_admin.get_user.return_value = make_app_user(["platyp-user"])
    app_user = await users.join(MagicMock(), make_user())
    assert app_user.roles == ["platyp-user"]
    kc_admin.update_user.assert_not_called()


@pytest.mark.asyncio
async def test_join_signup_disabled(kc_admin, signup):
    signup.is_signup_enabled.return_value = False
    kc_admin.get_user.return_value = make_app_user([])
    with pytest.raises(HTTPException) as e:
        await users.join(MagicMock(), make_user())
    assert e.value.detail == "error.signup_disabled"
    kc_admin.update_user.assert_not_called()


@pytest.mark.asyncio
async def test_delete_realm_roles(kc_admin):
    kc_admin.get_user.return_value = make_app_user(["platyp-user"])
    await users.delete("abc", make_user())
    kc_admin.delete_user.assert_called_once_with("abc")


@pytest.mark.asyncio
async def test_delete_client_roles(kc_admin, client_roles):
    kc_admin.get_user.return_value = make_app_user(["platyp-user", "platyp-admin"])
    kc = kc_admin.kc_admin
    kc.get_client_id.return_value = "cid"
    kc.get_client_roles_of_user.return_value = [{"name": "platyp-user"}, {"name": "platyp-admin"}]
    await users.delete("abc", make_user())
    kc_admin.delete_user.assert_not_called()
    kc.delete_client_roles_of_user.assert_called_once_with(
        "abc", "cid", [{"name": "platyp-user"}, {"name": "platyp-admin"}])


@pytest.mark.asyncio
async def test_get_not_app_user(kc_admin, client_roles):
    kc_admin.get_user.return_value = make_app_user([])
    with pytest.raises(HTTPException) as e:
        await users.get("abc", make_user())
    assert e.value.status_code == 404


@pytest.mark.asyncio
async def test_update_password_not_app_user(kc_admin, client_roles):
    kc_admin.get_user.return_value = make_app_user([])
    with pytest.raises(HTTPException):
        await users.update_password("abc", users.AppUserPassword(password="Passw0rd!"), make_user())
    kc_admin.update_user_password.assert_not_called()


@pytest.mark.asyncio
async def test_find_with_identity_providers(kc_admin):
    kc_admin.get_users = AsyncMock(return_value=[make_app_user(["platyp-user"])])
    kc_admin.kc_admin.get_user_social_logins.return_value = [{"identityProvider": "github", "userId": "123"}]
    result = await users.find(make_user())
    assert result.data[0].identity_providers == ["github"]


@pytest.mark.asyncio
async def test_update_password_with_identity_provider(kc_admin):
    kc_admin.get_user.return_value = make_app_user(["platyp-user"])
    kc_admin.kc_admin.get_user_social_logins.return_value = [{"identityProvider": "google", "userId": "123"}]
    with pytest.raises(HTTPException) as e:
        await users.update_password("abc", users.AppUserPassword(password="Passw0rd!"), make_user())
    assert e.value.detail == "error.password_with_identity_provider"
    kc_admin.update_user_password.assert_not_called()


def test_is_admin(monkeypatch):
    user = make_user(realm_roles=["platyp-admin"], client_roles=[])
    assert auth.is_admin(user)
    monkeypatch.setattr(auth.kc_service, "client_roles", True)
    assert not auth.is_admin(user)
    assert auth.is_admin(make_user(client_roles=["platyp-admin"]))

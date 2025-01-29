from api.auth import kc_admin
from api.models.users import AppUser, AppUserResult, AppUserDraft

APP_USER_ROLE = "platyp-user"


class UserService:

    def __init__(self):
        pass

    async def get_users(self) -> AppUserResult:
        """Get the users of the application

        Returns:
            AppUserResult: The users found
        """
        users = kc_admin.get_realm_role_members(APP_USER_ROLE)

        # Fetch Roles for Each User
        app_users = []
        for user in users:
            app_user = self._as_app_user(user)
            app_users.append(app_user)

        return AppUserResult(
            total=len(app_users),
            skip=0,
            limit=len(app_users),
            data=app_users)

    async def get_user(self, id_or_name: str) -> AppUser:
        """Get a user by id or name

        Args:
            id_or_name (str): The user id or name

        Returns:
            AppUser: The user
        """
        user_id = id_or_name
        try:
            user_id = kc_admin.get_user_id(id_or_name)
        except:
            pass
        if user_id is None:
            user_id = id_or_name
        user = kc_admin.get_user(user_id)
        return self._as_app_user(user)

    async def create_user(self, user: AppUserDraft):
        """Create a user with temporary password (required user action: update password)

        Args:
            user (AppUserDraft): The user details

        Returns:
            AppUser: The user created
        """
        payload = {
            "username": user.username,
            "email": user.email,
            "emailVerified": user.email_verified,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "enabled": user.enabled,
            "credentials": [{"value": user.password, "type": "password"}],
            "requiredActions": ["UPDATE_PASSWORD"]
        }
        user_id = kc_admin.create_user(payload)
        if user.roles:
            # ensure app user role is always assigned
            if APP_USER_ROLE not in user.roles:
                user.roles.append(APP_USER_ROLE)
        else:
            user.roles = [APP_USER_ROLE]
        roles = [self._get_role(role) for role in user.roles]
        kc_admin.assign_realm_roles(user_id, roles)

        return await self.get_user(user_id)

    async def update_user(self, user: AppUser):
        """Update user details: email, first_name, last_name, enabled, roles

        Args:
            user (AppUser): The user details

        Returns:
            AppUser: The user updated
        """
        payload = {}
        if user.email:
            payload["email"] = user.email
        if user.first_name:
            payload["firstName"] = user.first_name
        if user.last_name:
            payload["lastName"] = user.last_name
        if user.enabled is not None:
            payload["enabled"] = user.enabled
        kc_admin.update_user(user.id, payload)

        if user.roles:
            # ensure app user role is always assigned
            if APP_USER_ROLE not in user.roles:
                user.roles.append(APP_USER_ROLE)
            roles = [self._get_role(role) for role in user.roles]
            kc_admin.assign_realm_roles(user.id, roles)
        return await self.get_user(user.id)

    async def update_user_password(self, id: str, password: str) -> None:
        """Set temporary password for user

        Args:
            id (str): The user id
            password (str): The password
        """
        # ensure valid user
        await self.get_user(id)
        kc_admin.set_user_password(id, password, temporary=True)

    async def delete_user(self, id: str):
        """Delete user

        Args:
            id (str): The user id or name

        Returns:
            AppUser: The deleted user
        """
        try:
            user = await self.get_user(id)
            kc_admin.delete_user(user.id)
        except:
            kc_admin.delete_user(id)
        return user

    def _get_role(self, name: str):
        """Get role object by name

        Args:
            name (str): The role name

        Returns:
            dict: The Keycloak role object
        """
        return kc_admin.get_realm_role(name)

    def _as_app_user(self, user: dict) -> AppUser:
        """Make AppUser object from Keycloak user

        Args:
            user (dict): The Keycloak user

        Returns:
            AppUser: The user
        """
        # Get realm roles for the user
        user_id = user["id"]
        realm_roles = kc_admin.get_realm_roles_of_user(user_id)
        realm_role_names = [role["name"] for role in realm_roles]
        return AppUser(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            email_verified=user["emailVerified"],
            totp=user["totp"],
            first_name=user["firstName"],
            last_name=user["lastName"],
            enabled=user["enabled"],
            roles=realm_role_names
        )

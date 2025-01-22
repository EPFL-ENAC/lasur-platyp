from logging import debug
from api.db import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select
from fastapi import HTTPException
from api.models.authz import AppUser, AppResource, AppRole, AppUserRole, ACL


class ACLService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user(self, name: str) -> AppUser:
        """Ensure an app user exists by name

        Args:
            name (str): The unique user name

        Returns:
            AppUser: The app user with roles
        """
        user = await self.session.exec(
            select(AppUser)
            .options(joinedload(AppUser.roles))
            .where(AppUser.name == name)
        ).first()

        if not user:
            user = AppUser(name=name)
            self.session.add(user)
            await self.session.commit()

        return user

    async def get_or_create_role(self, name: str) -> AppRole:
        """Ensure role exists by name

        Args:
            name (str): The unique role name

        Returns:
            AppRole: The role
        """
        role = await self.session.exec(
            select(AppRole)
            .where(AppRole.name == name)
        ).first()

        if not role:
            role = AppRole(name=name)
            self.session.add(role)
            await self.session.commit()

        return role

    async def delete_role(self, name: str):
        """Delete role and associated ACLs nad user relations

        Args:
            name (str): The unique name of the role
        """
        role = await self.session.exec(
            select(AppRole)
            .where(AppRole.name == name)
        ).first()

        if role:
            user_roles = await self.session.exec(
                select(AppUserRole)
                .where(AppUserRole.role_id == role.id)
            )
            if user_roles:
                self.session.delete(user_roles)

            acls = await self.session.exec(
                select(ACL)
                .where(ACL.role_id == role.id)
            )
            if acls:
                self.session.delete(acls)

            self.session.delete(role)
            await self.session.commit()

    async def get_or_create_resource(self, name: str) -> AppResource:
        """Ensure resource exists by name

        Args:
            name (str): The unique resource name

        Returns:
            Resource: The resource with ACLs
        """
        resource = await self.session.exec(
            select(AppResource)
            .options(joinedload(AppResource.acls))
            .where(AppResource.name == name)
        ).first()

        if not resource:
            resource = AppResource(name=name)
            self.session.add(resource)
            await self.session.commit()

        return resource

    async def delete_resource(self, name: str):
        """Delete resource and associated ACLs

        Args:
            name (str): The unique name of the resource
        """
        resource = await self.session.exec(
            select(AppResource)
            .where(AppResource.name == name)
        ).first()

        if resource:
            acls = await self.session.exec(
                select(ACL)
                .where(ACL.resource_id == resource.id)
            )
            if acls:
                self.session.delete(acls)

            self.session.delete(resource)
            await self.session.commit()

    async def apply_user_role(self, user_name: str, role_name: str):
        """Ensure user has role

        Args:
            username (str): The unique user name, add an app user if not found
            role_name (str): The unique role name, add a role if not found
        """
        user = await self.get_or_create_user(user_name)
        role = await self.get_or_create_role(role_name)

        roles = [rl for rl in user.roles if rl.role_id == role.id]
        if len(roles):
            # user has role
            return

        user_role = AppUserRole(user.id, role_id=role.id)
        self.session.add(user_role)
        await self.session.commit()

    async def remove_user_role(self, user_name: str, role_name: str):
        """Remove user role

        Args:
            username (str): The unique user name, add an app user if not found
            role_name (str): The unique role name, add a role if not found
        """
        user = await self.get_or_create_user(user_name)
        role = await self.get_or_create_role(role_name)

        roles = [rl for rl in user.roles if rl.role_id == role.id]
        if len(roles) == 0:
            # user has not role
            return

        user_role = await self.session.exec(
            select(AppUserRole)
            .where(AppUserRole.user_id == user.id and AppUserRole.role_id == role.id)
        ).first()
        self.session.delete(user_role)
        await self.session.commit()

    async def apply_permission(self, role_name: str, resource_name, permission: str):
        """Ensure role has permission on resource

        Args:
            role_name (str): The unique role name, add a role if not found
            resource_name (str): The unique resource name, add a resource if not found
            permission (str): The permission name
        """
        role = await self.get_or_create_role(role_name)
        resource = await self.get_or_create_resource(resource_name)

        role_acls = [acl for acl in resource.acls if acl.role_id ==
                     role.id and acl.permission == permission]
        if len(role_acls):
            # role has resource permission
            return

        acl = ACL(role_id=role.id, resource_id=resource.id,
                  permission=permission)
        self.session.add(acl)
        await self.session.commit()

    async def check_permission(self, user_name: str, resource_name: int, permission: str) -> bool:
        """Check user has permission on a resource

        Args:
            user_name (str): The unique user name
            resource_name (int): The unique resource name
            permission (str): The permission

        Raises:
            HTTPException: 403 when permission is denied

        Returns:
            (bool): True if user has permission on resource
        """
        # Get user with roles
        user = await self.session.exec(
            select(AppUser)
            .options(joinedload(AppUser.roles))
            .where(AppUser.name == user_name)
        ).first()

        if not user:
            raise HTTPException(
                status_code=403, detail="Permission denied: user not found")

        # Get resource ACLs
        resource = await self.session.exec(
            select(AppResource)
            .options(joinedload(AppResource.acls))
            .where(AppResource.name == resource_name)
        ).first()

        if not resource:
            raise HTTPException(
                status_code=403, detail="Permission denied: resource not found")

        # Check if user has required permission through their roles
        role_ids = [ur.role_id for ur in user.roles]
        for acl in resource.acls:
            if acl.role_id in role_ids and acl.permission == permission:
                return True

        raise HTTPException(status_code=403, detail="Permission denied")

from logging import debug
from api.db import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select
from api.models.authz import ACL
import re


class ACLService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def delete_user_permissions(self, resource: str, subject: str = None):
        """Delete ACLs for resource and optionally a specific user

        Args:
            resource (str): The unique resource name
        """
        query = select(ACL).where(
            (ACL.resource == resource) & (ACL.subject_type == "user"))
        if subject:
            query = query.where(ACL.subject == subject)
        res = await self.session.exec(query)
        acls = res.all()

        if len(acls):
            for acl in acls:
                await self.session.delete(acl)
            await self.session.commit()

    async def apply_user_permission(self, resource: str, permission: str, subject: str):
        """Ensure user has permission on resource

        Args:
            resource (str): The resource name
            permission (str): The permission name
            subject (str): The subject name
        """
        res = await self.session.exec(
            select(ACL)
            .where(
                (ACL.resource == resource) &
                (ACL.permission == permission) &
                (ACL.subject_type == "user") &
                (ACL.subject == subject)
            )
        )
        acl = res.one_or_none()

        if acl:
            # user has resource permission
            return

        acl = ACL(resource=resource, permission=permission,
                  subject=subject, subject_type="user")
        self.session.add(acl)
        await self.session.commit()

    async def check_user_permission(self, resource: str, permission: str, subject: str) -> bool:
        """Check user has permission on a resource

        Args:
            resource (str): The unique resource name
            permission (str): The permission
            subject (str): The unique user name

        Returns:
            (bool): True if user has permission on resource, False otherwise
        """
        res = await self.session.exec(
            select(ACL)
            .where(
                (ACL.resource == resource) &
                ((ACL.permission == permission) | (ACL.permission == "*")) &
                (ACL.subject_type == "user") &
                (ACL.subject == subject)
            )
        )
        acl = res.one_or_none()

        if acl:
            # user has resource permission
            return True

        debug("Permission denied: {subject} {permission} {resource}")
        return False

    async def get_permitted_resource_ids(self, resource_type: str, permission: str, subject: str) -> list[int]:
        """Get all resource IDs of a given type that a user has permission on

        This method performs a single database query to fetch all permitted resources,
        avoiding N+1 query problems.

        Args:
            resource_type (str): The resource type prefix (e.g., "company", "campaign")
            permission (str): The permission to check (e.g., "read", "write")
            subject (str): The subject (user email) to check permissions for

        Returns:
            list[int]: List of resource IDs the user has permission on
        """
        # Validate resource_type to prevent SQL injection - only allow alphanumeric and underscore
        if not re.match(r'^[a-zA-Z0-9_]+$', resource_type):
            raise ValueError(f"Invalid resource_type: {resource_type}")
        
        # Query ACL table for all resources matching the pattern "resource_type:*"
        # where the user has the specified permission (or wildcard "*" permission)
        # The LIKE pattern is constructed safely since resource_type is validated above
        res = await self.session.exec(
            select(ACL.resource)
            .where(
                (ACL.resource.like(f"{resource_type}:%")) &
                ((ACL.permission == permission) | (ACL.permission == "*")) &
                (ACL.subject_type == "user") &
                (ACL.subject == subject)
            )
        )
        resources = res.all()

        # Extract the numeric IDs from resource strings like "company:123"
        resource_ids = []
        for resource in resources:
            try:
                # Split on ':' to separate resource type from ID
                # Use rsplit with maxsplit=1 to handle IDs that might contain colons
                parts = resource.rsplit(":", 1)
                if len(parts) == 2 and parts[0] == resource_type:
                    # Verify the prefix matches the requested resource type
                    resource_id = int(parts[1])
                    resource_ids.append(resource_id)
            except (ValueError, IndexError):
                # Skip any malformed resource strings
                continue

        return resource_ids

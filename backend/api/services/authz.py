from logging import debug
from api.db import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select
from api.models.authz import ACL


class ACLService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def delete_user_permissions(self, resource: str, subject: str = None):
        """Delete ACLs for resource and optionally a specific user

        Args:
            resource (str): The unique resource name
        """
        query = select(ACL).where(
            ACL.resource == resource and ACL.subject_type == "user")
        if subject:
            query = query.where(ACL.subject == subject)
        acls = await self.session.exec(query)

        if len(acls):
            for acl in acls:
                self.session.delete(acl)
            self.session.commit()

    async def apply_user_permission(self, resource: str, permission: str, subject: str):
        """Ensure user has permission on resource

        Args:
            resource (str): The resource name
            permission (str): The permission name
            subject (str): The subject name
        """
        acl = await self.session.exec(
            select(ACL)
            .where(ACL.resource == resource and ACL.permission == permission and ACL.subject_type == "user" and ACL.subject == subject)
        ).first()

        if acl:
            # user has resource permission
            return

        acl = ACL(resource=resource, permission=permission,
                  subject=subject, subject_type="user")
        self.session.add(acl)
        await self.session.commit()

    async def check_user_permission(self, resource: int, permission: str, subject: str) -> bool:
        """Check user has permission on a resource

        Args:
            resource (int): The unique resource name
            permission (str): The permission
            user (str): The unique user name

        Returns:
            (bool): True if user has permission on resource, False otherwise
        """
        acl = await self.session.exec(
            select(ACL)
            .where(ACL.resource == resource and ACL.permission == permission and ACL.subject_type == "user" and ACL.subject == subject)
        ).first()

        if acl:
            # user has resource permission
            return True

        debug("Permission denied: {subject} {permission} {resource}")
        return False

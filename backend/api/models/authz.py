from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

# Authorization models


class AppUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    # Other user fields
    roles: List["AppUserRole"] = Relationship(back_populates="user")


class AppResource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    # Other resource fields
    acls: List["ACL"] = Relationship(back_populates="resource")


class AppRole(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    users: List["AppUserRole"] = Relationship(back_populates="role")


class AppUserRole(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="appuser.id")
    role_id: int = Field(foreign_key="approle.id")
    user: AppUser = Relationship(back_populates="roles")
    role: AppRole = Relationship(back_populates="users")


class ACL(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    resource_id: int = Field(foreign_key="appresource.id")
    role_id: int = Field(foreign_key="approle.id")
    permission: str  # e.g., "read", "write", "delete"

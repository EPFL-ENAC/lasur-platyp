from typing import Optional, List
from pydantic import BaseModel
from enacit4r_sql.models.query import ListResult


class AppUser(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    email_verified: bool
    first_name: Optional[str]
    last_name: Optional[str]
    enabled: bool
    totp: Optional[bool] = False
    roles: List[str]


class AppUserDraft(AppUser):
    password: str


class AppUserPassword(BaseModel):
    password: str


class AppUserResult(ListResult):
    data: list[AppUser] = []

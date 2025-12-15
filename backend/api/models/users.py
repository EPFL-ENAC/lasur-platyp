from enacit4r_sql.models.query import ListResult
from enacit4r_auth.models.auth import AppUser, AppUserDraft, AppUserPassword
from pydantic import field_validator
import re


class AppUserDraftValidated(AppUserDraft):
    """AppUserDraft with input validation for registration"""
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip() if v else v
        if not v or len(v) == 0:
            raise ValueError('Username cannot be empty')
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError('Username can only contain letters, numbers, dots, hyphens, and underscores')
        return v
    
    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        v = v.strip() if v else v
        if not v or len(v) == 0:
            raise ValueError('First name cannot be empty')
        if len(v) > 100:
            raise ValueError('First name must be at most 100 characters')
        # Allow letters, spaces, hyphens, and apostrophes (for names like O'Brien or Jean-Paul)
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', v):
            raise ValueError('First name can only contain letters, spaces, hyphens, and apostrophes')
        return v
    
    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        v = v.strip() if v else v
        if not v or len(v) == 0:
            raise ValueError('Last name cannot be empty')
        if len(v) > 100:
            raise ValueError('Last name must be at most 100 characters')
        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', v):
            raise ValueError('Last name can only contain letters, spaces, hyphens, and apostrophes')
        return v


class AppUserResult(ListResult):
    data: list[AppUser] = []

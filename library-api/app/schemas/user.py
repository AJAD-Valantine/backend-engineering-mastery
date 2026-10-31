import re
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from app.models.user import UserRole
from app.schemas.base import AppBaseModel


class UserCreateRequest(AppBaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=25)
    phone: str = Field(pattern=r"^\+?[0-9]{10,15}$")
    address: str = Field(min_length=5, max_length=100)

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserCreateRequestWithRole(UserCreateRequest):
    role: Literal["member", "librarian", "admin"] = "member"


class UserUpdateRequest(AppBaseModel):
    first_name: str | None = Field(default=None, min_length=2, max_length=50)
    last_name: str | None = Field(default=None, min_length=2, max_length=50)
    email: EmailStr | None = Field(default=None)
    phone: str | None = Field(default=None, pattern=r"^\+?[0-9]{10,15}$")
    address: str | None = Field(default=None, min_length=5, max_length=100)
    active: bool | None = Field(default=None)


class UserResponse(AppBaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    phone: str
    address: str
    registered_at: datetime
    active: bool
    is_verified: bool

class ChangeRoleRequest(AppBaseModel):
    role: UserRole

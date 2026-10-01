from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.base import AppBaseModel


class UserCreateRequest(AppBaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=25,
        pattern=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$",
    )
    phone: str = Field(pattern=r"^\+?[0-9]{10,15}$")


class UserCreateRequestWithRole(UserCreateRequest):
    role: Literal["member", "admin", "mod", "librarian"]


class UserUpdateRequest(AppBaseModel):
    first_name: str | None = Field(default=None, min_length=2, max_length=50)
    last_name: str | None = Field(default=None, min_length=2, max_length=50)
    email: EmailStr | None = Field(default=None)
    phone: str | None = Field(default=None, pattern=r"^\+?[0-9]{10,15}$")


class UserResponse(AppBaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    phone: str
    address: str
    created_at: datetime

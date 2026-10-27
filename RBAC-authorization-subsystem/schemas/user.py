from datetime import datetime
from uuid import UUID

from core.enums import UserRole
from pydantic import EmailStr, Field, field_validator
from schemas.base import AppBaseModel


class UserCreateRequest(AppBaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError("Name cannot be empty")

        return value


class UserCreateRequestWithRole(AppBaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError("Name cannot be empty")

        return value

class UserLoginRequest(AppBaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(AppBaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    role: UserRole
    registered_at: datetime

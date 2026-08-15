from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateRequest(BaseModel):
    
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=25)
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    address: str = Field(..., min_length=10, max_length=75)

class AdminCreateUserRequest(UserCreateRequest):
    role: Literal["customer", "mod", "admin"] = Field(...)


class UserUpdateRequest(BaseModel):

    first_name: str | None = Field(None, min_length=2, max_length=50)
    last_name: str | None = Field(None, min_length=2, max_length=50)
    email: EmailStr | None = Field(None)
    phone: str | None = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    address: str | None = Field(None, min_length=10, max_length=75)


class UserResponse(BaseModel):

    user_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    phone: str
    address: str
    image_file: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedUserResponse(BaseModel):
    
    total_items: int
    page: int
    size: int
    data: list[UserResponse]
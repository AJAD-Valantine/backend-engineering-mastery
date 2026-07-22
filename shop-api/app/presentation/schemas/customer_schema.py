from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr = Field(...)
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    address: str = Field(..., min_length=10, max_length=75)


class CustomerUpdateRequest(BaseModel):
    first_name: str | None = Field(None, min_length=2, max_length=50)
    last_name: str | None = Field(None, min_length=2, max_length=50)
    email: EmailStr | None = Field(None)
    phone: str | None = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    address: str | None = Field(None, min_length=10, max_length=75)


class CustomerResponse(BaseModel):
    customer_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    category: str = Field(..., min_length=2, max_length=100)


class ProductUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=50)
    description: str | None = Field(None, min_length=10, max_length=500)
    price: float | None = Field(None, gt=0)
    stock_quantity: int | None = Field(None, ge=0)
    category: str | None = Field(None, min_length=2, max_length=100)


class ProductResponse(BaseModel):
    product_id: UUID
    name: str
    description: str
    price: float
    stock_quantity: int
    category: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

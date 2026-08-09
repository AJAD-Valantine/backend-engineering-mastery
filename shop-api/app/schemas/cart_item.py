from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CartItemCreateRequest(BaseModel):
    product_id: int = Field(...)
    quantity: int = Field(..., gt=0)


class CartItemUpdateRequest(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    cart_id: int
    user_id: UUID
    product_id: int
    quantity: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

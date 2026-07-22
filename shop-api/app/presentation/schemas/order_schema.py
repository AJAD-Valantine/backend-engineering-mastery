from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderUpdateRequest(BaseModel):
    status: (
        Literal["Pending", "Confirmed", "Packed", "Shipped", "Delivered", "Cancelled"]
    ) = Field()


class OrderResponse(BaseModel):
    id: int
    customer_id: UUID
    total_amount: float
    status: Literal[
        "Pending", "Confirmed", "Packed", "Shipped", "Delivered", "Cancelled"
    ]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class PaymentCreateRequest(BaseModel):
    order_id: int
    payment_method: Literal["Cash on Delivery", "Card", "Bank Transfer"]
    paid_amount: float = Field(..., gt=0)

class PaymentUpdateRequest(BaseModel):
    payment_status: Literal["Pending", "Paid", "Failed", "Refunded"]

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_method: Literal["Cash on Delivery", "Card", "Bank Transfer"]
    payment_status: Literal["Pending", "Paid", "Failed", "Refunded"]
    paid_amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
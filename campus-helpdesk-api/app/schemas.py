from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Literal, Optional
from datetime import datetime

class TicketCreate(BaseModel):
    requester_name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=150)
    category: Literal["Technical", "Academic", "Finance", "Facilities", "Other"] = Field(...)
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1)
    priority: Literal["Low", "Medium", "High"] = Field(default="Medium")
    status: Literal["Open", "In Progress", "Resolved"] = Field(default="Open")

class TicketUpdate(BaseModel):
    requester_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(default=None, max_length=150)
    category: Optional[Literal["Technical", "Academic", "Finance", "Facilities", "Other"]] = Field(default=None)
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, min_length=1)
    priority: Optional[Literal["Low", "Medium", "High"]] = Field(default=None)
    status: Optional[Literal["Open", "In Progress", "Resolved"]] = Field(default=None)

class TicketResponse(BaseModel):
    id: int
    requester_name: str 
    email: EmailStr 
    category: Literal["Technical", "Academic", "Finance", "Facilities", "Other"]
    title: str
    description: str
    priority: Literal["Low", "Medium", "High"]
    status: Literal["Open", "In Progress", "Resolved"]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
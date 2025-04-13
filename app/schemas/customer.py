from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Shared properties
class CustomerBase(BaseModel):
    name: str


# Properties to receive on customer creation
class CustomerCreate(CustomerBase):
    api_key: Optional[str] = None  # Auto-generated if not provided


# Properties to receive on customer update
class CustomerUpdate(CustomerBase):
    name: Optional[str] = None


# Properties shared by models stored in DB
class CustomerInDBBase(CustomerBase):
    id: int
    api_key: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Properties to return to client
class Customer(CustomerInDBBase):
    pass

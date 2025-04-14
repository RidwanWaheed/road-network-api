from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CustomerBase(BaseModel):
    name: str


class CustomerCreate(CustomerBase):
    api_key: Optional[str] = None 


class CustomerUpdate(CustomerBase):
    name: Optional[str] = None


class CustomerInDBBase(CustomerBase):
    id: int
    api_key: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Customer(CustomerInDBBase):
    pass

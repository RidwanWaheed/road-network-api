from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NetworkBase(BaseModel):
    name: str
    description: Optional[str] = None


class NetworkCreate(NetworkBase):
    data: Dict[str, Any] 


class NetworkUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None 


class NetworkInDBBase(NetworkBase):
    id: int
    customer_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Network(NetworkInDBBase):
    pass


class NetworkWithVersion(Network):
    version: int
    node_count: int
    edge_count: int

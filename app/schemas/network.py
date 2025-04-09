from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


# Shared properties
class NetworkBase(BaseModel):
    name: str
    description: Optional[str] = None

# Properties to receive on network creation
class NetworkCreate(NetworkBase):
    data: Dict[str, Any]  # GeoJSON data

# Properties to receive on network update
class NetworkUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None  # GeoJSON data

# Properties shared by models stored in DB
class NetworkInDBBase(NetworkBase):
    id: int
    customer_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }

# Properties to return to client
class Network(NetworkInDBBase):
    pass

# Network with version info
class NetworkWithVersion(Network):
    version: int
    node_count: int
    edge_count: int
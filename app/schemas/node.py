from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
from geojson_pydantic import Point as GeoJSONPoint

# Shared properties
class NodeBase(BaseModel):
    external_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

# Properties to receive on node creation
class NodeCreate(NodeBase):
    pass

# Properties to receive on node update
class NodeUpdate(NodeBase):
    properties: Optional[Dict[str, Any]] = None

# Properties shared by models stored in DB
class NodeInDBBase(NodeBase):
    id: int
    network_id: int
    version_id: int
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

# Properties to return to client
class Node(NodeInDBBase):
    coordinates: GeoJSONPoint

from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
from geojson_pydantic import LineString as GeoJSONLineString

# Shared properties
class EdgeBase(BaseModel):
    external_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

# Properties to receive on edge creation
class EdgeCreate(EdgeBase):
    pass

# Properties to receive on edge update
class EdgeUpdate(EdgeBase):
    properties: Optional[Dict[str, Any]] = None

# Properties shared by models stored in DB
class EdgeInDBBase(EdgeBase):
    id: int
    network_id: int
    version_id: int
    source_node_id: int
    target_node_id: int
    is_current: bool
    valid_from: datetime
    valid_to: Optional[datetime] = None
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

# Properties to return to client
class Edge(EdgeInDBBase):
    geometry: GeoJSONLineString
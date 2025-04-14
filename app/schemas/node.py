from datetime import datetime
from typing import Any, Dict, List, Optional

from geojson_pydantic import Point as GeoJSONPoint
from pydantic import BaseModel


class NodeBase(BaseModel):
    external_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class NodeCreate(NodeBase):
    pass


class NodeUpdate(NodeBase):
    properties: Optional[Dict[str, Any]] = None


class NodeInDBBase(NodeBase):
    id: int
    network_id: int
    version_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class Node(NodeInDBBase):
    coordinates: GeoJSONPoint

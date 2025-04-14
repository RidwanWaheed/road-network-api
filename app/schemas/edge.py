from datetime import datetime
from typing import Any, Dict, List, Optional

from geojson_pydantic import LineString as GeoJSONLineString
from pydantic import BaseModel


class EdgeBase(BaseModel):
    external_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class EdgeCreate(EdgeBase):
    pass


class EdgeUpdate(EdgeBase):
    properties: Optional[Dict[str, Any]] = None


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

    model_config = {"from_attributes": True}


class Edge(EdgeInDBBase):
    geometry: GeoJSONLineString

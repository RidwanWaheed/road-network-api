from typing import Dict, List, Optional, Tuple

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.node import Node
from app.repositories.base import BaseRepository
from app.schemas.node import NodeCreate, NodeUpdate


class NodeRepository(BaseRepository[Node, NodeCreate, NodeUpdate]):
    def __init__(self):
        super().__init__(Node)

    def create_from_geojson(
        self,
        db: Session,
        *,
        network_id: int,
        version_id: int,
        feature: Dict,
        external_id: str
    ) -> Node:
        coordinates = feature["geometry"]["coordinates"]
        point = Point(coordinates[0], coordinates[1])

        db_node = Node(
            network_id=network_id,
            version_id=version_id,
            external_id=external_id,
            geometry=from_shape(point, srid=4326),
            properties=feature.get("properties", {}),
        )
        db.add(db_node)
        db.flush()
        return db_node

    def get_by_external_id(
        self, db: Session, *, network_id: int, version_id: int, external_id: str
    ) -> Optional[Node]:
        return (
            db.query(Node)
            .filter(
                Node.network_id == network_id,
                Node.version_id == version_id,
                Node.external_id == external_id,
            )
            .first()
        )

    def get_by_network_version(
        self, db: Session, *, network_id: int, version_id: int
    ) -> List[Node]:
        return (
            db.query(Node)
            .filter(Node.network_id == network_id, Node.version_id == version_id)
            .all()
        )

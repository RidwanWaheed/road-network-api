import base64
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from geoalchemy2.shape import from_shape
from shapely.geometry import LineString
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.edge import Edge
from app.repositories.base import BaseRepository
from app.schemas.edge import EdgeCreate, EdgeUpdate


class EdgeRepository(BaseRepository[Edge, EdgeCreate, EdgeUpdate]):
    def __init__(self):
        super().__init__(Edge)

    def create_from_geojson(
        self,
        db: Session,
        *,
        network_id: int,
        version_id: int,
        source_node_id: int,
        target_node_id: int,
        feature: Dict,
        external_id: str
    ) -> Edge:
        coordinates = feature["geometry"]["coordinates"]
        line = LineString(coordinates)

        db_edge = Edge(
            network_id=network_id,
            version_id=version_id,
            external_id=external_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            geometry=from_shape(line, srid=4326),
            properties=feature.get("properties", {}),
            is_current=True,
            valid_from=datetime.now(timezone.utc),
        )
        db.add(db_edge)
        db.flush() 
        return db_edge

    def get_by_external_id(
        self, db: Session, *, network_id: int, external_id: str
    ) -> Optional[Edge]:
        return (
            db.query(Edge)
            .filter(
                Edge.network_id == network_id,
                Edge.external_id == external_id,
                Edge.is_current == True,
            )
            .first()
        )

    def mark_as_outdated(
        self, db: Session, *, edge_id: int, timestamp: datetime
    ) -> Edge:
        db_edge = db.query(Edge).filter(Edge.id == edge_id).first()
        if db_edge:
            db_edge.is_current = False
            db_edge.valid_to = timestamp
            db.add(db_edge)
            db.flush()
        return db_edge

    def get_current_by_network(self, db: Session, *, network_id: int) -> List[Edge]:
        return (
            db.query(Edge)
            .filter(Edge.network_id == network_id, Edge.is_current == True)
            .all()
        )

    def get_by_network_version(
        self, db: Session, *, network_id: int, version_id: int
    ) -> List[Edge]:
        return (
            db.query(Edge)
            .filter(Edge.network_id == network_id, Edge.version_id == version_id)
            .all()
        )

    def get_by_timestamp(
        self, db: Session, *, network_id: int, timestamp: datetime
    ) -> List[Edge]:
        return (
            db.query(Edge)
            .filter(
                Edge.network_id == network_id,
                Edge.valid_from <= timestamp,
                or_(Edge.valid_to > timestamp, Edge.valid_to.is_(None)),
            )
            .all()
        )

    def get_paginated_edges_by_network_version(
        self,
        db: Session,
        *,
        network_id: int,
        version_id: int,
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> Tuple[List[Edge], Optional[str], int]:
        query = db.query(Edge).filter(
            Edge.network_id == network_id, Edge.version_id == version_id
        )

        total_count = query.count()

        if cursor:
            try:
                edge_id = int(base64.b64decode(cursor.encode()).decode())
                query = query.filter(Edge.id > edge_id)
            except:
                pass

        edges = query.order_by(Edge.id).limit(limit + 1).all()

        has_more = len(edges) > limit
        if has_more:
            edges = edges[:-1]  

        next_cursor = None
        if has_more and edges:
            next_cursor = base64.b64encode(str(edges[-1].id).encode()).decode()

        return edges, next_cursor, total_count

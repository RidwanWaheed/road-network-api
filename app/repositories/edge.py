import base64
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from shapely.geometry import LineString
from datetime import datetime, timezone
from geoalchemy2.shape import from_shape
from typing import Dict, List, Optional, Tuple

from app.models.edge import Edge
from app.repositories.base import BaseRepository
from app.schemas.edge import EdgeCreate, EdgeUpdate


class EdgeRepository(BaseRepository[Edge, EdgeCreate, EdgeUpdate]):
    def __init__(self):
        super().__init__(Edge)

    def create_from_geojson(self, db: Session, *, network_id: int, version_id: int,
                          source_node_id: int, target_node_id: int,
                          feature: Dict, external_id: str) -> Edge:
        """Create an edge from a GeoJSON feature with node IDs"""
        # Extract coordinates from GeoJSON
        coordinates = feature["geometry"]["coordinates"]
        line = LineString(coordinates)
        
        # Create edge
        db_edge = Edge(
            network_id=network_id,
            version_id=version_id,
            external_id=external_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            geometry=from_shape(line, srid=4326),
            properties=feature.get("properties", {}),
            is_current=True,
            valid_from=datetime.now(timezone.utc)
        )
        db.add(db_edge)
        db.flush()  # Get ID without committing transaction
        return db_edge

    def get_by_external_id(self, db: Session, *, network_id: int, 
                         external_id: str) -> Optional[Edge]:
        """Get a current edge by its external ID within a specific network"""
        return db.query(Edge).filter(
            Edge.network_id == network_id,
            Edge.external_id == external_id,
            Edge.is_current == True
        ).first()

    def mark_as_outdated(self, db: Session, *, edge_id: int, timestamp: datetime) -> Edge:
        """Mark an edge as outdated with a valid_to timestamp"""
        db_edge = db.query(Edge).filter(Edge.id == edge_id).first()
        if db_edge:
            db_edge.is_current = False
            db_edge.valid_to = timestamp
            db.add(db_edge)
            db.flush()
        return db_edge

    def get_current_by_network(self, db: Session, *, network_id: int) -> List[Edge]:
        """Get all current edges for a network"""
        return db.query(Edge).filter(
            Edge.network_id == network_id,
            Edge.is_current == True
        ).all()

    def get_by_network_version(self, db: Session, *, network_id: int, 
                             version_id: int) -> List[Edge]:
        """Get all edges for a specific network version"""
        return db.query(Edge).filter(
            Edge.network_id == network_id,
            Edge.version_id == version_id
        ).all()

    def get_by_timestamp(self, db: Session, *, network_id: int, 
                       timestamp: datetime) -> List[Edge]:
        """Get edges valid at a specific timestamp"""
        return db.query(Edge).filter(
            Edge.network_id == network_id,
            Edge.valid_from <= timestamp,
            or_(
                Edge.valid_to > timestamp,
                Edge.valid_to.is_(None)
            )
        ).all()
    
    def get_paginated_edges_by_network_version(
        self, db: Session, *, 
        network_id: int, 
        version_id: int, 
        cursor: Optional[str] = None, 
        limit: int = 100
        ) -> Tuple[List[Edge], Optional[str], int]:
        """Get paginated edges for a specific network version"""
        query = db.query(Edge).filter(
            Edge.network_id == network_id,
            Edge.version_id == version_id
        )
        
        # Get total count
        total_count = query.count()
        
        # Apply cursor if provided
        if cursor:
            try:
                # Decode the cursor (which is a base64 encoded edge ID)
                edge_id = int(base64.b64decode(cursor.encode()).decode())
                query = query.filter(Edge.id > edge_id)
            except:
                # If cursor is invalid, ignore it
                pass
        
        # Apply limit
        edges = query.order_by(Edge.id).limit(limit + 1).all()
        
        # Check if there are more results
        has_more = len(edges) > limit
        if has_more:
            edges = edges[:-1]  # Remove the extra item we fetched
        
        # Create next cursor if there are more results
        next_cursor = None
        if has_more and edges:
            next_cursor = base64.b64encode(str(edges[-1].id).encode()).decode()
        
        return edges, next_cursor, total_count
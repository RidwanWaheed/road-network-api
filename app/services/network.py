# app/services/network.py
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session

from app.models.network_version import NetworkVersion
from app.repositories.edge import EdgeRepository
from app.repositories.network import NetworkRepository
from app.repositories.node import NodeRepository
from app.schemas.network import (
    Network,
    NetworkCreate,
    NetworkUpdate,
    NetworkWithVersion,
)
from app.utils.geojson import extract_nodes_and_edges


class NetworkService:
    def __init__(
        self,
        network_repo: NetworkRepository,
        node_repo: NodeRepository,
        edge_repo: EdgeRepository,
    ):
        self.network_repo = network_repo
        self.node_repo = node_repo
        self.edge_repo = edge_repo

    def get(self, db: Session, id: int) -> Optional[Network]:
        return self.network_repo.get(db=db, id=id)

    def get_multi(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100):
        return self.network_repo.get_by_customer(
            db=db, customer_id=customer_id, skip=skip, limit=limit
        )

    def create(
        self, db: Session, obj_in: NetworkCreate, customer_id: int
    ) -> NetworkWithVersion:
        db_network = self.network_repo.create_with_version(
            db=db, obj_in=obj_in, customer_id=customer_id
        )

        version = self.network_repo.get_latest_version(db=db, network_id=db_network.id)

        geojson_data = obj_in.data
        nodes_data, edges_data = extract_nodes_and_edges(geojson_data)

        node_map = {} 
        for node_id, node_feature in nodes_data.items():
            db_node = self.node_repo.create_from_geojson(
                db=db,
                network_id=db_network.id,
                version_id=version.id,
                feature=node_feature,
                external_id=node_id,
            )
            node_map[node_id] = db_node.id

        for edge_id, edge_data in edges_data.items():
            edge_feature, source_id, target_id = edge_data

            if source_id in node_map and target_id in node_map:
                self.edge_repo.create_from_geojson(
                    db=db,
                    network_id=db_network.id,
                    version_id=version.id,
                    source_node_id=node_map[source_id],
                    target_node_id=node_map[target_id],
                    feature=edge_feature,
                    external_id=edge_id,
                )

        db.commit()

        node_count = len(nodes_data)
        edge_count = len(edges_data)

        return NetworkWithVersion(
            id=db_network.id,
            name=db_network.name,
            description=db_network.description,
            customer_id=db_network.customer_id,
            created_at=db_network.created_at,
            updated_at=db_network.updated_at,
            version=version.version_number,
            node_count=node_count,
            edge_count=edge_count,
        )

    def update(
        self, db: Session, network_id: int, obj_in: NetworkUpdate
    ) -> NetworkWithVersion:
        db_network = self.network_repo.get(db=db, id=network_id)
        if not db_network:
            return None

        if obj_in.name or obj_in.description:
            update_data = obj_in.model_dump(
                exclude={"data"}, exclude_unset=True
            )
            db_network = self.network_repo.update(
                db=db, db_obj=db_network, obj_in=update_data
            )

        if not obj_in.data:
            current_version = self.network_repo.get_latest_version(
                db=db, network_id=network_id
            )
            node_count = len(
                self.node_repo.get_by_network_version(
                    db=db, network_id=network_id, version_id=current_version.id
                )
            )
            edge_count = len(
                self.edge_repo.get_by_network_version(
                    db=db, network_id=network_id, version_id=current_version.id
                )
            )

            return NetworkWithVersion(
                id=db_network.id,
                name=db_network.name,
                description=db_network.description,
                customer_id=db_network.customer_id,
                created_at=db_network.created_at,
                updated_at=db_network.updated_at,
                version=current_version.version_number,
                node_count=node_count,
                edge_count=edge_count,
            )

        previous_version = self.network_repo.get_latest_version(
            db=db, network_id=network_id
        )
        new_version = self.network_repo.create_new_version(db=db, network_id=network_id)

        geojson_data = obj_in.data
        nodes_data, edges_data = extract_nodes_and_edges(geojson_data)

        current_time = datetime.now(timezone.utc)

        existing_edges = self.edge_repo.get_current_by_network(
            db=db, network_id=network_id
        )
        for edge in existing_edges:
            self.edge_repo.mark_as_outdated(
                db=db, edge_id=edge.id, timestamp=current_time
            )

        node_map = {}
        for node_id, node_feature in nodes_data.items():
            db_node = self.node_repo.create_from_geojson(
                db=db,
                network_id=network_id,
                version_id=new_version.id,
                feature=node_feature,
                external_id=node_id,
            )
            node_map[node_id] = db_node.id

        for edge_id, edge_data in edges_data.items():
            edge_feature, source_id, target_id = edge_data

            if source_id in node_map and target_id in node_map:
                self.edge_repo.create_from_geojson(
                    db=db,
                    network_id=network_id,
                    version_id=new_version.id,
                    source_node_id=node_map[source_id],
                    target_node_id=node_map[target_id],
                    feature=edge_feature,
                    external_id=edge_id,
                )

        db.commit()

        node_count = len(nodes_data)
        edge_count = len(edges_data)

        return NetworkWithVersion(
            id=db_network.id,
            name=db_network.name,
            description=db_network.description,
            customer_id=db_network.customer_id,
            created_at=db_network.created_at,
            updated_at=db_network.updated_at,
            version=new_version.version_number,
            node_count=node_count,
            edge_count=edge_count,
        )

    def get_edges_by_version(
        self,
        db: Session,
        network_id: int,
        version_id: Optional[int] = None,
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get network edges by version or timestamp"""
        network = self.network_repo.get(db=db, id=network_id)
        if not network:
            return None

        if version_id:
            version = (
                db.query(NetworkVersion)
                .filter(
                    NetworkVersion.network_id == network_id,
                    NetworkVersion.version_number == version_id,
                )
                .first()
            )

            if not version:
                return None

            edges = self.edge_repo.get_by_network_version(
                db=db, network_id=network_id, version_id=version.id
            )
            timestamp = version.created_at
        elif timestamp:
            edges = self.edge_repo.get_by_timestamp(
                db=db, network_id=network_id, timestamp=timestamp
            )
        else:
            edges = self.edge_repo.get_current_by_network(db=db, network_id=network_id)
            latest_version = self.network_repo.get_latest_version(
                db=db, network_id=network_id
            )
            version_id = latest_version.version_number if latest_version else None
            timestamp = datetime.now(datetime.timezone.utc)()

        features = []
        for edge in edges:
            geom = to_shape(edge.geometry)
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [list(coord) for coord in geom.coords],
                },
                "properties": {
                    "id": edge.id,
                    "external_id": edge.external_id,
                    "source_node_id": edge.source_node_id,
                    "target_node_id": edge.target_node_id,
                    "is_current": edge.is_current,
                    "valid_from": edge.valid_from.isoformat(),
                    "valid_to": edge.valid_to.isoformat() if edge.valid_to else None,
                    **edge.properties,
                },
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "network_id": network_id,
            "version": version_id,
            "timestamp": timestamp.isoformat() if timestamp else None,
            "features": features,
        }

    def get_paginated_edges_by_version(
        self,
        db: Session,
        network_id: int,
        version_id: Optional[int] = None,
        cursor: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get paginated network edges by version"""
        network = self.network_repo.get(db=db, id=network_id)
        if not network:
            return None

        if version_id:
            version = (
                db.query(NetworkVersion)
                .filter(
                    NetworkVersion.network_id == network_id,
                    NetworkVersion.version_number == version_id,
                )
                .first()
            )

            if not version:
                return None
        else:
            version = self.network_repo.get_latest_version(db=db, network_id=network_id)
            version_id = version.version_number if version else None

        (
            edges,
            next_cursor,
            total_count,
        ) = self.edge_repo.get_paginated_edges_by_network_version(
            db=db,
            network_id=network_id,
            version_id=version.id,
            cursor=cursor,
            limit=limit,
        )

        features = []
        for edge in edges:
            geom = to_shape(edge.geometry)
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [list(coord) for coord in geom.coords],
                },
                "properties": {
                    "id": edge.id,
                    "external_id": edge.external_id,
                    "source_node_id": edge.source_node_id,
                    "target_node_id": edge.target_node_id,
                    "is_current": edge.is_current,
                    "valid_from": edge.valid_from.isoformat(),
                    "valid_to": edge.valid_to.isoformat() if edge.valid_to else None,
                    **edge.properties,
                },
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "network_id": network_id,
            "version": version_id,
            "features": features,
            "next_cursor": next_cursor,
            "total_count": total_count,
        }

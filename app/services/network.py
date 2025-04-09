# app/services/network.py
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import uuid
from geoalchemy2.shape import from_shape, to_shape
from app.models.network_version import NetworkVersion
from app.repositories.network import NetworkRepository
from app.repositories.node import NodeRepository
from app.repositories.edge import EdgeRepository
from app.schemas.network import NetworkCreate, NetworkUpdate, Network, NetworkWithVersion
from app.utils.geojson import extract_nodes_and_edges

class NetworkService:
    def __init__(self,
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
        return self.network_repo.get_by_customer(db=db, customer_id=customer_id, skip=skip, limit=limit)

    def create(self, db: Session, obj_in: NetworkCreate, customer_id: int) -> NetworkWithVersion:
        """Create a new network with initial version and process GeoJSON data"""
        # Create network with initial version
        db_network = self.network_repo.create_with_version(db=db, obj_in=obj_in, customer_id=customer_id)
        
        # Get version ID
        version = self.network_repo.get_latest_version(db=db, network_id=db_network.id)
        
        # Process GeoJSON data to extract nodes and edges
        geojson_data = obj_in.data
        nodes_data, edges_data = extract_nodes_and_edges(geojson_data)
        
        # Create nodes first
        node_map = {}  # Map external IDs to DB IDs
        for node_id, node_feature in nodes_data.items():
            db_node = self.node_repo.create_from_geojson(
                db=db,
                network_id=db_network.id,
                version_id=version.id,
                feature=node_feature,
                external_id=node_id
            )
            node_map[node_id] = db_node.id
        
        # Create edges with node references
        for edge_id, edge_data in edges_data.items():
            edge_feature, source_id, target_id = edge_data
            
            # Check if both nodes exist
            if source_id in node_map and target_id in node_map:
                self.edge_repo.create_from_geojson(
                    db=db,
                    network_id=db_network.id,
                    version_id=version.id,
                    source_node_id=node_map[source_id],
                    target_node_id=node_map[target_id],
                    feature=edge_feature,
                    external_id=edge_id
                )
        
        # Commit the transaction
        db.commit()
        
        # Construct response
        node_count = len(nodes_data)
        edge_count = len(edges_data)
        
        return NetworkWithVersion(
            **db_network.__dict__,
            version=version.version_number,
            node_count=node_count,
            edge_count=edge_count
        )

    def update(self, db: Session, network_id: int, obj_in: NetworkUpdate) -> NetworkWithVersion:
        """Update a network by creating a new version and processing GeoJSON data"""
        # Get the network
        db_network = self.network_repo.get(db=db, id=network_id)
        if not db_network:
            return None
        
        # Update network metadata if provided
        if obj_in.name or obj_in.description:
            update_data = obj_in.model_dump(exclude={"data"}, exclude_unset=True) #only fields that are explicitly set in obj_in will be included in the dictionary
            db_network = self.network_repo.update(db=db, db_obj=db_network, obj_in=update_data)
            
        # If no data provided, just return the current network
        if not obj_in.data:
            current_version = self.network_repo.get_latest_version(db=db, network_id=network_id)
            node_count = len(self.node_repo.get_by_network_version(db=db, network_id=network_id, version_id=current_version.id))
            edge_count = len(self.edge_repo.get_by_network_version(db=db, network_id=network_id, version_id=current_version.id))
            
            return NetworkWithVersion(
                **db_network.__dict__,
                version=current_version.version_number,
                node_count=node_count,
                edge_count=edge_count
            )
        
        # Create a new version
        previous_version = self.network_repo.get_latest_version(db=db, network_id=network_id)
        new_version = self.network_repo.create_new_version(db=db, network_id=network_id)
        
        # Process GeoJSON data to extract nodes and edges
        geojson_data = obj_in.data
        nodes_data, edges_data = extract_nodes_and_edges(geojson_data)
        
        # Current timestamp for versioning
        current_time = datetime.now(datetime.timezone.utc)()
        
        # Mark existing edges as outdated
        existing_edges = self.edge_repo.get_current_by_network(db=db, network_id=network_id)
        for edge in existing_edges:
            self.edge_repo.mark_as_outdated(db=db, edge_id=edge.id, timestamp=current_time)
            
        # Process nodes
        # For simplicity, I am creating new nodes for the new version
        node_map = {}  # Map external IDs to DB IDs
        for node_id, node_feature in nodes_data.items():
            db_node = self.node_repo.create_from_geojson(
                db=db,
                network_id=network_id,
                version_id=new_version.id,
                feature=node_feature,
                external_id=node_id
            )
            node_map[node_id] = db_node.id
        
        # Create new edges
        for edge_id, edge_data in edges_data.items():
            edge_feature, source_id, target_id = edge_data
            
            # Check if both nodes exist
            if source_id in node_map and target_id in node_map:
                self.edge_repo.create_from_geojson(
                    db=db,
                    network_id=network_id,
                    version_id=new_version.id,
                    source_node_id=node_map[source_id],
                    target_node_id=node_map[target_id],
                    feature=edge_feature,
                    external_id=edge_id
                )
        
        # Commit the transaction
        db.commit()
        
        # Construct response
        node_count = len(nodes_data)
        edge_count = len(edges_data)
        
        return NetworkWithVersion(
            **db_network.__dict__,
            version=new_version.version_number,
            node_count=node_count,
            edge_count=edge_count
        )

    def get_edges_by_version(self, db: Session, network_id: int, version_id: Optional[int] = None,
                          timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """Get network edges by version or timestamp"""
        network = self.network_repo.get(db=db, id=network_id)
        if not network:
            return None
        
        # Determine which edges to return
        if version_id:
            # Get edges for a specific version
            version = db.query(NetworkVersion).filter(
                NetworkVersion.network_id == network_id,
                NetworkVersion.version_number == version_id
            ).first()
            
            if not version:
                return None
                
            edges = self.edge_repo.get_by_network_version(db=db, network_id=network_id, version_id=version.id)
            timestamp = version.created_at
        elif timestamp:
            # Get edges valid at a specific timestamp
            edges = self.edge_repo.get_by_timestamp(db=db, network_id=network_id, timestamp=timestamp)
        else:
            # Get current edges
            edges = self.edge_repo.get_current_by_network(db=db, network_id=network_id)
            latest_version = self.network_repo.get_latest_version(db=db, network_id=network_id)
            version_id = latest_version.version_number if latest_version else None
            timestamp = datetime.now(datetime.timezone.utc)()
        
        # Convert to GeoJSON
        features = []
        for edge in edges:
            # Convert edge to GeoJSON feature
            geom = to_shape(edge.geometry)
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [list(coord) for coord in geom.coords]
                },
                "properties": {
                    "id": edge.id,
                    "external_id": edge.external_id,
                    "source_node_id": edge.source_node_id,
                    "target_node_id": edge.target_node_id,
                    "is_current": edge.is_current,
                    "valid_from": edge.valid_from.isoformat(),
                    "valid_to": edge.valid_to.isoformat() if edge.valid_to else None,
                    **edge.properties
                }
            }
            features.append(feature)
            
        return {
            "type": "FeatureCollection",
            "network_id": network_id,
            "version": version_id,
            "timestamp": timestamp.isoformat() if timestamp else None,
            "features": features
        }
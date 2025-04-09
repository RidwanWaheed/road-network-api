import uuid
from typing import Dict, Tuple, List, Any

def extract_nodes_and_edges(geojson_data: Dict[str, Any]) -> Tuple[Dict[str, Dict], Dict[str, Tuple]]:
    """
    Extract nodes and edges from a GeoJSON FeatureCollection.
    For LineString features (edges), identify or create nodes at start and end points.
    Returns:
    - Dictionary of nodes: {node_id: node_feature}
    - Dictionary of edges: {edge_id: (edge_feature, source_node_id, target_node_id)}
    """
    if not geojson_data or geojson_data.get("type") != "FeatureCollection":
        raise ValueError("Invalid GeoJSON data: Expected a FeatureCollection")
        
    features = geojson_data.get("features", [])
    
    # First identify all points that could be nodes
    nodes = {}
    node_coordinates = {}  # Map coordinates to node IDs for lookup
    
    # First pass: extract existing Point features as nodes
    for feature in features:
        if feature.get("geometry", {}).get("type") == "Point":
            # This is a node
            node_id = feature.get("properties", {}).get("id") or str(uuid.uuid4())
            nodes[node_id] = feature
            
            # Store coordinates for lookup (as tuple to make hashable)
            coords = tuple(feature["geometry"]["coordinates"])
            node_coordinates[coords] = node_id
    
    # Second pass: extract LineString features as edges and create nodes for endpoints
    edges = {}
    for feature in features:
        if feature.get("geometry", {}).get("type") == "LineString":
            # This is an edge
            edge_id = feature.get("properties", {}).get("id") or str(uuid.uuid4())
            
            # Get the start and end points
            coords = feature["geometry"]["coordinates"]
            if len(coords) < 2:
                continue  # Skip invalid LineStrings
                
            start_coords = tuple(coords[0])
            end_coords = tuple(coords[-1])
            
            # Get or create source node
            if start_coords in node_coordinates:
                source_node_id = node_coordinates[start_coords]
            else:
                source_node_id = str(uuid.uuid4())
                node_feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": list(start_coords)
                    },
                    "properties": {
                        "id": source_node_id,
                        "type": "auto_generated"
                    }
                }
                nodes[source_node_id] = node_feature
                node_coordinates[start_coords] = source_node_id
            
            # Get or create target node
            if end_coords in node_coordinates:
                target_node_id = node_coordinates[end_coords]
            else:
                target_node_id = str(uuid.uuid4())
                node_feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": list(end_coords)
                    },
                    "properties": {
                        "id": target_node_id,
                        "type": "auto_generated"
                    }
                }
                nodes[target_node_id] = node_feature
                node_coordinates[end_coords] = target_node_id
            
            # Store the edge with its source and target nodes
            edges[edge_id] = (feature, source_node_id, target_node_id)
            
    return nodes, edges
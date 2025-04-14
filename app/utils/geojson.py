import uuid
from typing import Any, Dict, List, Tuple


def extract_nodes_and_edges(
    geojson_data: Dict[str, Any]
) -> Tuple[Dict[str, Dict], Dict[str, Tuple]]:
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

    nodes = {}
    node_coordinates = {} 

    for feature in features:
        if feature.get("geometry", {}).get("type") == "Point":
            node_id = feature.get("properties", {}).get("id") or str(uuid.uuid4())
            nodes[node_id] = feature

            coords = tuple(feature["geometry"]["coordinates"])
            node_coordinates[coords] = node_id

    edges = {}
    for feature in features:
        if feature.get("geometry", {}).get("type") == "LineString":
            edge_id = feature.get("properties", {}).get("id") or str(uuid.uuid4())

            coords = feature["geometry"]["coordinates"]
            if len(coords) < 2:
                continue 

            start_coords = tuple(coords[0])
            end_coords = tuple(coords[-1])

            if start_coords in node_coordinates:
                source_node_id = node_coordinates[start_coords]
            else:
                source_node_id = str(uuid.uuid4())
                node_feature = {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": list(start_coords)},
                    "properties": {"id": source_node_id, "type": "auto_generated"},
                }
                nodes[source_node_id] = node_feature
                node_coordinates[start_coords] = source_node_id

            if end_coords in node_coordinates:
                target_node_id = node_coordinates[end_coords]
            else:
                target_node_id = str(uuid.uuid4())
                node_feature = {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": list(end_coords)},
                    "properties": {"id": target_node_id, "type": "auto_generated"},
                }
                nodes[target_node_id] = node_feature
                node_coordinates[end_coords] = target_node_id

            edges[edge_id] = (feature, source_node_id, target_node_id)

    return nodes, edges

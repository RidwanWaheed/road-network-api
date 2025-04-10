import pytest
from geoalchemy2.shape import to_shape
from app.models.network import Network
from app.models.customer import Customer
from app.repositories.node import NodeRepository
from app.models.network_version import NetworkVersion

def test_create_node_from_geojson(db):
    # Arrange
    repo = NodeRepository()
    
    # Create prerequisite data
    customer = Customer(name="Test Customer", api_key="test_key_123")
    db.add(customer)
    db.flush()
    
    network = Network(name="Test Network", customer_id=customer.id)
    db.add(network)
    db.flush()
    
    version = NetworkVersion(network_id=network.id, version_number=1)
    db.add(version)
    db.flush()
    
    # GeoJSON node
    node_feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [10.123, 47.456]
        },
        "properties": {
            "name": "Test Node",
            "type": "junction"
        }
    }
    
    # Act
    node = repo.create_from_geojson(
        db=db,
        network_id=network.id,
        version_id=version.id,
        feature=node_feature,
        external_id="node_123"
    )
    
    # Assert
    assert node.id is not None
    assert node.network_id == network.id
    assert node.version_id == version.id
    assert node.external_id == "node_123"
    
    # Check geometry
    point = to_shape(node.geometry)
    assert round(point.x, 3) == 10.123
    assert round(point.y, 3) == 47.456
    
    # Check properties
    assert node.properties["name"] == "Test Node"
    assert node.properties["type"] == "junction"
import json

import pytest
from fastapi.testclient import TestClient

from app.models.customer import Customer


# Load a real GeoJSON sample from file
@pytest.fixture
def road_network_geojson():
    # You'll need to adjust this path to wherever your sample data is
    with open("tests/data/road_network_aying_1.0.geojson", "r") as f:
        return json.load(f)


@pytest.fixture
def auth_customer(db):
    """Create a customer and return its API key for authentication"""
    customer = Customer(name="Real Data Customer", api_key="real_data_key")
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def test_create_network_with_real_data(client, auth_customer, road_network_geojson):
    # Arrange
    network_data = {
        "name": "Bayrischzell Road Network",
        "description": "Road network for Bayrischzell area",
        "data": road_network_geojson,
    }

    # Act
    response = client.post(
        "/api/networks/",
        json=network_data,
        headers={"X-API-Key": auth_customer.api_key},
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bayrischzell Road Network"
    assert "node_count" in data
    assert "edge_count" in data

    # Verify the network ID for use in subsequent tests
    network_id = data["id"]

    # Get the edges to verify they were processed correctly
    edges_response = client.get(
        f"/api/networks/{network_id}/edges",
        headers={"X-API-Key": auth_customer.api_key},
    )

    assert edges_response.status_code == 200
    edges_data = edges_response.json()
    assert edges_data["type"] == "FeatureCollection"
    assert len(edges_data["features"]) > 0

    # Check content of the first feature
    first_feature = edges_data["features"][0]
    assert first_feature["type"] == "Feature"
    assert first_feature["geometry"]["type"] == "LineString"
    assert "coordinates" in first_feature["geometry"]
    assert "properties" in first_feature

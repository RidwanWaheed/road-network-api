import json

import pytest
from fastapi.testclient import TestClient

from app.models.customer import Customer

# Sample GeoJSON data
SAMPLE_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[10.0, 47.0], [10.1, 47.1], [10.2, 47.2]],
            },
            "properties": {
                "name": "Test Road",
                "highway": "residential",
                "length": 100.5,
            },
        }
    ],
}


@pytest.fixture
def auth_customer(db):
    """Create a customer and return its API key for authentication"""
    customer = Customer(name="Test Customer", api_key="test_network_key")
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def test_create_network(client, auth_customer):
    # Arrange
    network_data = {
        "name": "Test Network",
        "description": "A test road network",
        "data": SAMPLE_GEOJSON,
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
    assert data["name"] == "Test Network"
    assert data["description"] == "A test road network"
    assert data["version"] == 1
    assert data["node_count"] >= 2  # At least start and end nodes
    assert data["edge_count"] >= 1  # At least one road


def test_get_networks(client, auth_customer, db):
    # Arrange - Create a network first
    response = client.post(
        "/api/networks/",
        json={
            "name": "First Network",
            "description": "Test network",
            "data": SAMPLE_GEOJSON,
        },
        headers={"X-API-Key": auth_customer.api_key},
    )

    # Act
    response = client.get(
        "/api/networks/", headers={"X-API-Key": auth_customer.api_key}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(n["name"] == "First Network" for n in data)


def test_get_network_by_id(client, auth_customer):
    # Arrange - Create a network first
    create_response = client.post(
        "/api/networks/",
        json={
            "name": "Test Network",
            "description": "Test network",
            "data": SAMPLE_GEOJSON,
        },
        headers={"X-API-Key": auth_customer.api_key},
    )
    network_id = create_response.json()["id"]

    # Act
    response = client.get(
        f"/api/networks/{network_id}", headers={"X-API-Key": auth_customer.api_key}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == network_id
    assert data["name"] == "Test Network"


def test_update_network(client, auth_customer):
    # Arrange - Create a network first
    create_response = client.post(
        "/api/networks/",
        json={
            "name": "Original Network",
            "description": "Original description",
            "data": SAMPLE_GEOJSON,
        },
        headers={"X-API-Key": auth_customer.api_key},
    )
    network_id = create_response.json()["id"]

    # Act - Update the network
    update_data = {
        "name": "Updated Network",
        "description": "Updated description",
        "data": SAMPLE_GEOJSON,  # Same data for simplicity
    }
    response = client.put(
        f"/api/networks/{network_id}",
        json=update_data,
        headers={"X-API-Key": auth_customer.api_key},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Network"
    assert data["description"] == "Updated description"
    assert data["version"] == 2  # Version should be incremented


def test_get_network_edges(client, auth_customer):
    # Arrange - Create a network first
    create_response = client.post(
        "/api/networks/",
        json={
            "name": "Edge Test Network",
            "description": "Network for testing edges",
            "data": SAMPLE_GEOJSON,
        },
        headers={"X-API-Key": auth_customer.api_key},
    )
    network_id = create_response.json()["id"]

    # Act - Get edges
    response = client.get(
        f"/api/networks/{network_id}/edges",
        headers={"X-API-Key": auth_customer.api_key},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert data["network_id"] == network_id
    assert "features" in data
    assert len(data["features"]) >= 1


def test_get_network_edges_with_pagination(client, auth_customer):
    # Arrange - Create a network first
    create_response = client.post(
        "/api/networks/",
        json={
            "name": "Pagination Test Network",
            "description": "Network for testing pagination",
            "data": SAMPLE_GEOJSON,
        },
        headers={"X-API-Key": auth_customer.api_key},
    )
    network_id = create_response.json()["id"]

    # Act - Get edges with pagination
    response = client.get(
        f"/api/networks/{network_id}/edges?limit=1",
        headers={"X-API-Key": auth_customer.api_key},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "features" in data
    assert len(data["features"]) == 1  # Should only have 1 item due to limit

    # Check if next_cursor is present for pagination
    assert "next_cursor" in data

    # If the next_cursor is not None, we can test fetching the next page
    if data["next_cursor"]:
        next_response = client.get(
            f"/api/networks/{network_id}/edges?cursor={data['next_cursor']}&limit=1",
            headers={"X-API-Key": auth_customer.api_key},
        )
        assert next_response.status_code == 200

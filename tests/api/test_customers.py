import pytest
from fastapi.testclient import TestClient
from app.models.customer import Customer

def test_create_customer(client):
    # Arrange
    customer_data = {
        "name": "Test Customer"
    }
    
    # Act
    response = client.post("/api/customers/", json=customer_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Customer"
    assert "api_key" in data
    assert "id" in data

def test_get_customer_by_id(client, db):
    # Arrange - Create a customer directly in the database
    customer = Customer(name="Existing Customer", api_key="test_key_123")
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    # Act - Get the customer via API with authentication
    response = client.get(
        f"/api/customers/{customer.id}",
        headers={"X-API-Key": "test_key_123"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Existing Customer"
    assert data["id"] == customer.id

def test_get_customer_unauthorized(client, db):
    # Arrange - Create a customer
    customer = Customer(name="Existing Customer", api_key="test_key_123")
    db.add(customer)
    db.commit()
    
    # Act - Try to get the customer with wrong API key
    response = client.get(
        f"/api/customers/{customer.id}",
        headers={"X-API-Key": "wrong_key"}
    )
    
    # Assert
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]

def test_update_customer(client, db):
    # Arrange
    customer = Customer(name="Original Name", api_key="test_key_123")
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    # Act
    update_data = {"name": "Updated Name"}
    response = client.put(
        f"/api/customers/{customer.id}",
        json=update_data,
        headers={"X-API-Key": "test_key_123"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
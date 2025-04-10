import pytest
from app.models.customer import Customer
from app.schemas.network import NetworkCreate
from app.repositories.network import NetworkRepository

def test_create_network_with_version(db):
    # Arrange
    repo = NetworkRepository()
    
    # Create a customer first
    customer = Customer(name="Test Customer", api_key="test_key_789")
    db.add(customer)
    db.commit()
    
    network_data = NetworkCreate(
        name="Test Network",
        description="Test network description",
        data={"type": "FeatureCollection", "features": []}
    )
    
    # Act
    network = repo.create_with_version(db=db, obj_in=network_data, customer_id=customer.id)
    
    # Assert
    assert network.id is not None
    assert network.name == "Test Network"
    assert network.customer_id == customer.id
    
    # Check that version was created
    version = repo.get_latest_version(db=db, network_id=network.id)
    assert version is not None
    assert version.version_number == 1
import pytest
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate

def test_create_customer(db):
    # Arrange
    repo = CustomerRepository()
    customer_data = CustomerCreate(name="Test Customer", api_key="test_key_123")
    
    # Act
    customer = repo.create(db=db, obj_in=customer_data)
    
    # Assert
    assert customer.id is not None
    assert customer.name == "Test Customer"
    assert customer.api_key == "test_key_123"

def test_get_customer_by_api_key(db):
    # Arrange
    repo = CustomerRepository()
    customer_data = CustomerCreate(name="Test Customer", api_key="test_key_456")
    repo.create(db=db, obj_in=customer_data)
    
    # Act
    customer = repo.get_by_api_key(db=db, api_key="test_key_456")
    
    # Assert
    assert customer is not None
    assert customer.name == "Test Customer"
    
    # Act again with wrong key
    customer = repo.get_by_api_key(db=db, api_key="wrong_key")
    
    # Assert
    assert customer is None
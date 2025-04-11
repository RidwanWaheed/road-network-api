import pytest
from unittest.mock import MagicMock
from app.services.customer import CustomerService
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate

def test_create_customer():
    # Arrange
    mock_repo = MagicMock(spec=CustomerRepository)
    service = CustomerService(repository=mock_repo)
    customer_data = CustomerCreate(name="Test Customer")
    
    # Mock the repository create method
    mock_customer = MagicMock()
    mock_customer.id = 1
    mock_customer.name = "Test Customer" 
    mock_customer.api_key = "generated_key"
    mock_repo.create.return_value = mock_customer
    
    # Act
    customer = service.create(db=MagicMock(), obj_in=customer_data)
    
    # Assert
    assert customer is not None
    assert customer.name == "Test Customer"  # This should now pass
    assert customer.api_key == "generated_key"
    
    # Verify repository method was called
    mock_repo.create.assert_called_once()
    
    # Check that api_key was generated
    call_args = mock_repo.create.call_args[1]["obj_in"]
    assert call_args.api_key is not None
    assert len(call_args.api_key) == 32  # Default length

def test_create_customer_with_api_key():
    # Arrange
    mock_repo = MagicMock(spec=CustomerRepository)
    service = CustomerService(repository=mock_repo)
    customer_data = CustomerCreate(name="Test Customer", api_key="provided_key")
    
    # Mock the repository create method
    mock_customer = MagicMock()
    mock_customer.id = 1
    mock_customer.name = "Test Customer"  
    mock_customer.api_key = "provided_key"
    mock_repo.create.return_value = mock_customer
    
    # Act
    customer = service.create(db=MagicMock(), obj_in=customer_data)
    
    # Assert
    assert customer is not None
    assert customer.api_key == "provided_key"
    
    # Verify repository method was called with provided key
    mock_repo.create.assert_called_once()
    assert mock_repo.create.call_args[1]["obj_in"].api_key == "provided_key"
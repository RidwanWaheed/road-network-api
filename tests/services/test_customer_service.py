from unittest.mock import MagicMock

import pytest

from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.customer import CustomerService


def test_create_customer():
    mock_repo = MagicMock(spec=CustomerRepository)
    service = CustomerService(repository=mock_repo)
    customer_data = CustomerCreate(name="Test Customer")

    mock_customer = MagicMock()
    mock_customer.id = 1
    mock_customer.name = "Test Customer"
    mock_customer.api_key = "generated_key"
    mock_repo.create.return_value = mock_customer

    customer = service.create(db=MagicMock(), obj_in=customer_data)

    assert customer is not None
    assert customer.name == "Test Customer"
    assert customer.api_key == "generated_key"

    mock_repo.create.assert_called_once()

    call_args = mock_repo.create.call_args[1]["obj_in"]
    assert call_args.api_key is not None
    assert len(call_args.api_key) == 32


def test_create_customer_with_api_key():
    mock_repo = MagicMock(spec=CustomerRepository)
    service = CustomerService(repository=mock_repo)
    customer_data = CustomerCreate(name="Test Customer", api_key="provided_key")

    mock_customer = MagicMock()
    mock_customer.id = 1
    mock_customer.name = "Test Customer"
    mock_customer.api_key = "provided_key"
    mock_repo.create.return_value = mock_customer

    customer = service.create(db=MagicMock(), obj_in=customer_data)

    assert customer is not None
    assert customer.api_key == "provided_key"

    mock_repo.create.assert_called_once()
    assert mock_repo.create.call_args[1]["obj_in"].api_key == "provided_key"

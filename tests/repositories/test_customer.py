import pytest

from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate


def test_create_customer(db):
    repo = CustomerRepository()
    customer_data = CustomerCreate(name="Test Customer", api_key="test_key_123")

    customer = repo.create(db=db, obj_in=customer_data)

    assert customer.id is not None
    assert customer.name == "Test Customer"
    assert customer.api_key == "test_key_123"


def test_get_customer_by_api_key(db):
    repo = CustomerRepository()
    customer_data = CustomerCreate(name="Test Customer", api_key="test_key_456")
    repo.create(db=db, obj_in=customer_data)

    customer = repo.get_by_api_key(db=db, api_key="test_key_456")

    assert customer is not None
    assert customer.name == "Test Customer"

    customer = repo.get_by_api_key(db=db, api_key="wrong_key")

    assert customer is None

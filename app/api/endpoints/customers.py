from typing import Any, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from app.db.manual_session import get_db
from app.services.customer import CustomerService
from app.models.customer import Customer as CustomerModel
from app.api.dependencies import get_customer_service, get_current_customer
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate

router = APIRouter()

@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED)
def create_customer(
    *,
    db: Session = Depends(get_db),
    customer_in: CustomerCreate,
    service: CustomerService = Depends(get_customer_service)
) -> Any:
    """Create new customer"""
    customer = service.create(db=db, obj_in=customer_in)
    return customer

@router.get("/me", response_model=Customer)
def get_current_customer(
    *,
    current_customer: CustomerModel = Depends(get_current_customer)
) -> Any:
    """Get current customer"""
    return current_customer

@router.get("/{customer_id}", response_model=Customer)
def get_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    service: CustomerService = Depends(get_customer_service),
    current_customer: CustomerModel = Depends(get_current_customer)
) -> Any:
    """Get customer by ID"""
    # Only allow a customer to see their own information
    if current_customer.id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this customer information is forbidden"
        )
    
    customer = service.get(db=db, id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer

@router.put("/{customer_id}", response_model=Customer)
def update_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    customer_in: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service),
    current_customer: CustomerModel = Depends(get_current_customer)
) -> Any:
    """Update customer"""
    # Only allow a customer to update their own information
    if current_customer.id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own customer information"
        )
    
    customer = service.update(db=db, id=customer_id, obj_in=customer_in)
    return customer
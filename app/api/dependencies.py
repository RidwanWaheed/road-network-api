from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Header

from app.db.session import get_db
from app.models.customer import Customer
from app.repositories.edge import EdgeRepository
from app.repositories.node import NodeRepository
from app.services.network import NetworkService
from app.services.customer import CustomerService
from app.repositories.network import NetworkRepository
from app.repositories.customer import CustomerRepository

# Repository dependencies
def get_customer_repository() -> CustomerRepository:
    return CustomerRepository()

def get_network_repository() -> NetworkRepository:
    return NetworkRepository()

def get_node_repository() -> NodeRepository:
    return NodeRepository()

def get_edge_repository() -> EdgeRepository:
    return EdgeRepository()

# Service dependencies
def get_customer_service(
    repository: CustomerRepository = Depends(get_customer_repository),
) -> CustomerService:
    return CustomerService(repository=repository)

def get_network_service(
    network_repo: NetworkRepository = Depends(get_network_repository),
    node_repo: NodeRepository = Depends(get_node_repository),
    edge_repo: EdgeRepository = Depends(get_edge_repository),
) -> NetworkService:
    return NetworkService(
        network_repo=network_repo,
        node_repo=node_repo,
        edge_repo=edge_repo
    )

# Authentication
def get_current_customer(
    db: Session = Depends(get_db),
    x_api_key: str = Header(...),
    customer_service: CustomerService = Depends(get_customer_service),
) -> Customer:
    """Validate API key and return customer"""
    customer = customer_service.get_by_api_key(db=db, api_key=x_api_key)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return customer
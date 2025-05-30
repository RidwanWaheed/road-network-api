from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_customer, get_network_service
from app.db.session import get_session
from app.models.customer import Customer as CustomerModel
from app.schemas.network import (
    Network,
    NetworkCreate,
    NetworkUpdate,
    NetworkWithVersion,
)
from app.services.network import NetworkService

router = APIRouter()


@router.post(
    "/", response_model=NetworkWithVersion, status_code=status.HTTP_201_CREATED
)
def create_network(
    *,
    db: Session = Depends(get_session),
    network_in: NetworkCreate,
    service: NetworkService = Depends(get_network_service),
    current_customer: CustomerModel = Depends(get_current_customer)
) -> Any:
    network = service.create(db=db, obj_in=network_in, customer_id=current_customer.id)
    return network


@router.get("/", response_model=List[Network])
def get_networks(
    *,
    db: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    service: NetworkService = Depends(get_network_service),
    current_customer: CustomerModel = Depends(get_current_customer)
) -> Any:
    networks = service.get_multi(
        db=db, customer_id=current_customer.id, skip=skip, limit=limit
    )
    return networks


@router.get("/{network_id}", response_model=Network)
def get_network(
    *,
    db: Session = Depends(get_session),
    network_id: int,
    service: NetworkService = Depends(get_network_service),
    current_customer: CustomerModel = Depends(get_current_customer)
) -> Any:
    network = service.get(db=db, id=network_id)
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Network not found"
        )

    # Check if network belongs to the current customer
    if network.customer_id != current_customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this network is forbidden",
        )

    return network


@router.put("/{network_id}", response_model=NetworkWithVersion)
def update_network(
    *,
    db: Session = Depends(get_session),
    network_id: int,
    network_in: NetworkUpdate,
    service: NetworkService = Depends(get_network_service),
    current_customer: CustomerModel = Depends(get_current_customer)
) -> Any:
    network = service.get(db=db, id=network_id)
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Network not found"
        )

    if network.customer_id != current_customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this network is forbidden",
        )

    updated_network = service.update(db=db, network_id=network_id, obj_in=network_in)
    return updated_network


@router.get("/{network_id}/edges", response_model=dict)
def get_network_edges(
    *,
    db: Session = Depends(get_session),
    network_id: int,
    version: Optional[int] = Query(None, description="Specific version to retrieve"),
    timestamp: Optional[datetime] = Query(
        None, description="Timestamp for point-in-time retrieval"
    ),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items per page"),
    service: NetworkService = Depends(get_network_service),
    current_customer: CustomerModel = Depends(get_current_customer)
) -> Any:
    network = service.get(db=db, id=network_id)
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Network not found"
        )

    if network.customer_id != current_customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this network is forbidden",
        )

    if limit is not None or cursor is not None:
        edges = service.get_paginated_edges_by_version(
            db=db, network_id=network_id, version_id=version, cursor=cursor, limit=limit
        )
    else:
        print("got here")
        edges = service.get_edges_by_version(
            db=db, network_id=network_id, version_id=version, timestamp=timestamp
        )

    if not edges:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No edges found for the specified criteria",
        )

    return edges

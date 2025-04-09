from typing import Optional
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.repositories.base import BaseRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate

class CustomerRepository(BaseRepository[Customer, CustomerCreate, CustomerUpdate]):
    def __init__(self):
        super().__init__(Customer)

    def get_by_api_key(self, db: Session, *, api_key: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.api_key == api_key).first()
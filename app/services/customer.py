import string
import secrets
from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate, Customer

class CustomerService:
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    def get(self, db: Session, id: int) -> Optional[Customer]:
        return self.repository.get(db=db, id=id)

    def get_by_api_key(self, db: Session, api_key: str) -> Optional[Customer]:
        return self.repository.get_by_api_key(db=db, api_key=api_key)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.repository.get_multi(db=db, skip=skip, limit=limit)

    def create(self, db: Session, obj_in: CustomerCreate) -> Customer:
        # Generate API key if not provided
        if not obj_in.api_key:
            api_key = self._generate_api_key()
            customer_data = obj_in.model_dump()
            customer_data["api_key"] = api_key
            obj_in = CustomerCreate(**customer_data)
        
        return self.repository.create(db=db, obj_in=obj_in)

    def update(self, db: Session, id: int, obj_in: CustomerUpdate) -> Customer:
        db_obj = self.repository.get(db=db, id=id)
        return self.repository.update(db=db, db_obj=db_obj, obj_in=obj_in)

    def _generate_api_key(self, length: int = 32) -> str:
        """Generate a random API key"""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))
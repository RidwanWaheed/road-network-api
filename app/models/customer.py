from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, func

from app.db.base_class import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    api_key = Column(String(64), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    networks = relationship("Network", back_populates="customer")
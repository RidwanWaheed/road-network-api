from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class NetworkVersion(Base):
    __tablename__ = "network_versions"

    id = Column(Integer, primary_key=True, index=True)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("network_id", "version_number", name="uix_network_version"),
    )

    # Relatioships
    network = relationship("Network", back_populates="versions")
    nodes = relationship("Node", back_populates="version")
    edges = relationship("Edge", back_populates="version")

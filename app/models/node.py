from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, UniqueConstraint

from app.db.base import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("network_versions.id"), nullable=False)
    external_id = Column(String(100))
    geometry = Column(Geometry("POINT", srid=4326), nullable=False)
    properties = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('network_id', 'external_id', 'version_id', name='uix_node_network_external_version'),
    )

    # Relationships
    network = relationship("Network", back_populates="nodes")
    version = relationship("NetworkVersion", back_populates="nodes")
    outgoing_edges = relationship("Edge", foreign_keys="[Edge.source_node_id]", back_populates="source_node")
    incoming_edges = relationship("Edge", foreign_keys="[Edge.target_node_id]", back_populates="target_node")
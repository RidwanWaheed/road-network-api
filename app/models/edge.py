from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class Edge(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, index=True)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("network_versions.id"), nullable=False)
    external_id = Column(String(100))
    source_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    target_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    geometry = Column(Geometry("LINESTRING", srid=4326), nullable=False)
    properties = Column(JSONB)
    is_current = Column(Boolean, default=True)
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_to = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    network = relationship("Network", back_populates="edges")
    version = relationship("NetworkVersion", back_populates="edges")
    source_node = relationship(
        "Node", foreign_keys=[source_node_id], back_populates="outgoing_edges"
    )
    target_node = relationship(
        "Node", foreign_keys=[target_node_id], back_populates="incoming_edges"
    )

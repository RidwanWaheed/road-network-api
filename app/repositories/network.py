from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.network import Network
from app.models.network_version import NetworkVersion
from app.repositories.base import BaseRepository
from app.schemas.network import NetworkCreate, NetworkUpdate


class NetworkRepository(BaseRepository[Network, NetworkCreate, NetworkUpdate]):
    def __init__(self):
        super().__init__(Network)

    def get_by_customer(
        self, db: Session, *, customer_id: int, skip: int = 0, limit: int = 100
    ) -> List[Network]:
        return (
            db.query(Network)
            .filter(Network.customer_id == customer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_version(
        self, db: Session, *, obj_in: NetworkCreate, customer_id: int
    ) -> Network:
        """Create a new network with initial version (1)"""
        network_data = obj_in.model_dump(exclude={"data"})
        db_network = Network(**network_data, customer_id=customer_id)
        db.add(db_network)
        db.flush()  # Get network ID

        # Create initial version
        db_version = NetworkVersion(network_id=db_network.id, version_number=1)
        db.add(db_version)
        db.commit()
        db.refresh(db_network)
        return db_network

    def get_latest_version(
        self, db: Session, *, network_id: int
    ) -> Optional[NetworkVersion]:
        """Get the latest version of a network"""
        return (
            db.query(NetworkVersion)
            .filter(NetworkVersion.network_id == network_id)
            .order_by(NetworkVersion.version_number.desc())
            .first()
        )

    def create_new_version(self, db: Session, *, network_id: int) -> NetworkVersion:
        """Create a new version for a network (incremented from latest)"""
        latest_version = self.get_latest_version(db, network_id=network_id)
        new_version_num = latest_version.version_number + 1 if latest_version else 1

        db_version = NetworkVersion(
            network_id=network_id, version_number=new_version_num
        )
        db.add(db_version)
        db.commit()
        db.refresh(db_version)
        return db_version

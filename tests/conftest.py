import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_session
from main import app

TEST_DATABASE_URL = "postgresql://postgres:postgres@db-test:5432/roadnetworkdb"


os.environ["DATABASE_URL"] = TEST_DATABASE_URL


engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    with engine.connect() as connection:
        connection.execute(
            text("DROP EXTENSION IF EXISTS postgis_tiger_geocoder CASCADE")
        )
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        connection.commit()
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

    with engine.connect() as connection:
        connection.execute(
            text("DROP EXTENSION IF EXISTS postgis_tiger_geocoder CASCADE")
        )
        connection.commit()

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

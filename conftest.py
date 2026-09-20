"""
Root pytest configuration.

Provides a TestClient fixture backed by an in-memory SQLite database so the
API integration tests can run without a live PostgreSQL server. The FastAPI
`get_db` dependency is overridden to use the test engine/session factory.
"""

import os

# Must be set before `database` is imported (it reads DATABASE_URL at import
# time to create the module-level engine).
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_worldmine.db")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import models so all mappers are registered on the shared Base before
# any tables are created.
import models
import database

test_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine, autocommit=False, autoflush=False, expire_on_commit=False
)

models.Base.metadata.create_all(bind=test_engine)


def pytest_collection_modifyitems(config, items):
    """Skip live-infrastructure tests unless explicitly enabled.

    Tests marked `staging` require a deployed environment (external API host,
    PostgreSQL, Redis). They are skipped by default so the local/CI suite stays
    hermetic; set RUN_STAGING_TESTS=1 to run them.
    """
    if os.environ.get("RUN_STAGING_TESTS") == "1":
        return

    skip_staging = pytest.mark.skip(
        reason="requires live staging infrastructure (set RUN_STAGING_TESTS=1 to run)"
    )
    for item in items:
        if "staging" in item.keywords:
            item.add_marker(skip_staging)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    """Create test client with an in-memory database override"""
    from app import app

    app.dependency_overrides[database.get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(database.get_db, None)
"""
Test fixtures for Scrounger backend tests.

These fixtures provide a clean test environment with an isolated database
for each test function.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app


# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_category(client):
    """Create a sample category for tests."""
    response = client.post("/api/categories", json={
        "name": "electronics",
        "display_name": "Electronics",
        "description": "Electronic devices and components"
    })
    return response.json()


@pytest.fixture
def sample_tag(client):
    """Create a sample tag for tests."""
    response = client.post("/api/tags", json={
        "name": "urgent",
        "color": "#FF0000"
    })
    return response.json()


@pytest.fixture
def sample_value_factor(client):
    """Create a sample value factor for tests."""
    response = client.post("/api/value-factors", json={
        "name": "Holiday Season",
        "description": "Increased demand during holidays",
        "multiplier": 1.15,
        "active": True
    })
    return response.json()


@pytest.fixture
def sample_item(client, sample_category):
    """Create a sample item for tests."""
    response = client.post("/api/items", json={
        "name": "NVIDIA RTX 3080",
        "description": "Graphics card, used for 6 months",
        "category_id": sample_category["id"],
        "condition": "good",
        "asking_price": 450.00,
        "min_price": 400.00,
        "cost_basis": 699.99,
        "status": "inventory",
        "location": "Office shelf A3"
    })
    return response.json()


@pytest.fixture
def sample_marketplace(client):
    """Create a sample marketplace for tests."""
    response = client.post("/api/marketplaces", json={
        "name": "reddit_hardwareswap",
        "display_name": "r/hardwareswap",
        "platform_type": "reddit",
        "fee_percentage": 0,
        "bump_interval_hours": 72,
        "feedback_timer_days": 3
    })
    return response.json()

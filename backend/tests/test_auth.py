import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.db import get_db
from app.models.base import Base
from app.models.models import User
from app.core.security import get_password_hash

# Define temporary test SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_smartbiz.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Re-create all tables in test database
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the database dependency in FastAPI app
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    """Fixture to ensure the database is clean before each test runs."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def test_register_user_success():
    """Verify standard registration works with valid role."""
    response = client.post(
        "/api/auth/register",
        json={"name": "Alice Smith", "email": "alice@example.com", "password": "alicepassword", "role": "Manager"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice Smith"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "Manager"
    assert "id" in data

def test_register_invalid_role():
    """Verify registration fails for unsupported role."""
    response = client.post(
        "/api/auth/register",
        json={"name": "Alice Smith", "email": "alice@example.com", "password": "alicepassword", "role": "Developer"}
    )
    assert response.status_code == 400
    assert "Invalid role" in response.json()["detail"]

def test_register_duplicate_email():
    """Verify system blocks registering duplicate emails."""
    client.post(
        "/api/auth/register",
        json={"name": "Alice Smith", "email": "alice@example.com", "password": "alicepassword", "role": "Manager"}
    )
    response = client.post(
        "/api/auth/register",
        json={"name": "Alice Two", "email": "alice@example.com", "password": "alicepassword2", "role": "Manager"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_success():
    """Verify that credentials check and token issuance work."""
    # Register first
    client.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "password123", "role": "Admin"}
    )
    
    # Login via JSON
    response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "Admin"

def test_login_invalid_credentials():
    """Verify that wrong password fails."""
    client.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "password123", "role": "Admin"}
    )
    
    response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_get_current_user_profile():
    """Verify that using the JWT allows retrieving /me."""
    client.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "password123", "role": "Admin"}
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Request profile
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "Admin"

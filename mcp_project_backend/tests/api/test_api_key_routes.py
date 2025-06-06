import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from mcp.db.models.api_key import APIKey

def test_create_api_key(test_client: TestClient, db_session: Session):
    """Test creating a new API key."""
    response = test_client.post(
        "/api/v1/api-keys/",
        json={
            "name": "Test API Key",
            "owner_id": "test_user",
            "owner_type": "user",
            "expires_in_days": 30
        },
        headers={"X-User-ID": "test_user"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert data["name"] == "Test API Key"
    assert data["owner_id"] == "test_user"
    assert data["owner_type"] == "user"
    assert data["is_active"] is True
    assert "key" in data  # Raw API key should be included
    
    # Verify the key was saved in the database
    db_key = db_session.query(APIKey).filter_by(id=data["id"]).first()
    assert db_key is not None
    assert db_key.name == "Test API Key"
    assert db_key.owner_id == "test_user"

def test_list_api_keys(test_client: TestClient, db_session: Session):
    """Test listing API keys."""
    # Create some test keys
    key1 = APIKey(name="Key 1", created_by="test_user", owner_id="test_user")
    key2 = APIKey(name="Key 2", created_by="test_user", owner_id="test_user")
    key3 = APIKey(name="Key 3", created_by="other_user", owner_id="other_user")
    db_session.add_all([key1, key2, key3])
    db_session.commit()
    
    # Test listing all keys
    response = test_client.get(
        "/api/v1/api-keys/",
        headers={"X-User-ID": "test_user"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    
    # Test filtering by owner
    response = test_client.get(
        "/api/v1/api-keys/?owner_id=test_user",
        headers={"X-User-ID": "test_user"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(key["owner_id"] == "test_user" for key in data)

def test_get_api_key(test_client: TestClient, db_session: Session):
    """Test getting a specific API key."""
    # Create a test key
    key = APIKey(name="Test Key", created_by="test_user", owner_id="test_user")
    db_session.add(key)
    db_session.commit()
    
    response = test_client.get(
        f"/api/v1/api-keys/{key.id}",
        headers={"X-User-ID": "test_user"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["id"] == key.id
    assert data["name"] == "Test Key"
    assert data["owner_id"] == "test_user"

def test_deactivate_api_key(test_client: TestClient, db_session: Session):
    """Test deactivating an API key."""
    # Create a test key
    key = APIKey(name="Test Key", created_by="test_user", owner_id="test_user")
    db_session.add(key)
    db_session.commit()
    
    response = test_client.delete(
        f"/api/v1/api-keys/{key.id}",
        headers={"X-User-ID": "test_user"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["id"] == key.id
    assert data["is_active"] is False
    
    # Verify the key was deactivated in the database
    db_key = db_session.query(APIKey).filter_by(id=key.id).first()
    assert db_key.is_active is False

def test_api_key_authentication(test_client: TestClient, db_session: Session):
    """Test API key authentication."""
    # Create a test key
    key = APIKey(name="Test Key", created_by="test_user", owner_id="test_user")
    db_session.add(key)
    db_session.commit()
    
    # Test with valid API key
    response = test_client.get(
        "/api/v1/mcp-definitions/",  # Example protected endpoint
        headers={"X-API-Key": key.raw_key}
    )
    assert response.status_code != status.HTTP_401_UNAUTHORIZED
    
    # Test with invalid API key
    response = test_client.get(
        "/api/v1/mcp-definitions/",
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test without API key
    response = test_client.get("/api/v1/mcp-definitions/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 
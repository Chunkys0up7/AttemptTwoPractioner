"""
Tests for External Database Configuration API endpoints.
"""
import pytest
import uuid
import json
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session # For type hinting if needed

from mcp.schemas.external_db_config import ExternalDbConfigCreate, ExternalDbConfigUpdate

# --- Helper to create a config for other tests ---
def create_ext_db_config_util(client: TestClient, name: str = "Test PG Config", db_type: str = "postgresql") -> dict:
    payload = {
        "name": name,
        "db_type": db_type,
        "host": "localhost",
        "port": 5432,
        "username": "testuser",
        "database_name": "testdb",
        "additional_configs": json.dumps({"sslmode": "require"})
    }
    response = client.post("/api/v1/external-db-configs/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

def test_create_external_db_config_ok(test_client: TestClient):
    payload = {
        "name": "My Production PG",
        "description": "Main production PostgreSQL instance",
        "db_type": "postgresql",
        "host": "prod.db.example.com",
        "port": 5432,
        "username": "prod_user",
        "password_secret_key": "prod_pg_pass_key",
        "database_name": "main_app_db",
        "additional_configs": json.dumps({"connect_timeout": 10})
    }
    response = test_client.post("/api/v1/external-db-configs/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["db_type"] == payload["db_type"]
    assert data["host"] == payload["host"]
    assert json.loads(data["additional_configs"]) == {"connect_timeout": 10}
    assert "id" in data

def test_create_external_db_config_duplicate_name(test_client: TestClient):
    create_ext_db_config_util(client=test_client, name="Unique DB Config")
    
    payload_duplicate = {"name": "Unique DB Config", "db_type": "mysql"}
    response = test_client.post("/api/v1/external-db-configs/", json=payload_duplicate)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]

def test_create_external_db_config_invalid_json_additional_configs(test_client: TestClient):
    payload = {
        "name": "Invalid JSON Config",
        "db_type": "other",
        "additional_configs": "not a valid json string: {"
    }
    response = test_client.post("/api/v1/external-db-configs/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY # FastAPI validation error
    # Pydantic v2 error structure might be different, check detail
    # Example: assert "valid JSON string" in response.json()["detail"][0]["msg"]

def test_get_external_db_config_ok(test_client: TestClient):
    created_config = create_ext_db_config_util(test_client, name="Get Me DB")
    config_id = created_config["id"]

    response = test_client.get(f"/api/v1/external-db-configs/{config_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == config_id
    assert data["name"] == "Get Me DB"

def test_get_external_db_config_not_found(test_client: TestClient):
    random_uuid = uuid.uuid4()
    response = test_client.get(f"/api/v1/external-db-configs/{random_uuid}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_external_db_configs(test_client: TestClient):
    create_ext_db_config_util(test_client, name="List DB 1")
    create_ext_db_config_util(test_client, name="List DB 2")

    response = test_client.get("/api/v1/external-db-configs/?limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 2
    names_in_response = [item["name"] for item in data["items"]]
    assert "List DB 1" in names_in_response
    assert "List DB 2" in names_in_response

def test_update_external_db_config_ok(test_client: TestClient):
    created_config = create_ext_db_config_util(test_client, name="Original DB Name")
    config_id = created_config["id"]
    
    update_payload = {"name": "Updated DB Name", "description": "Now with description!"}
    response = test_client.put(f"/api/v1/external-db-configs/{config_id}", json=update_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_payload["name"]
    assert data["description"] == update_payload["description"]
    assert data["id"] == config_id

def test_update_external_db_config_name_conflict(test_client: TestClient):
    config1 = create_ext_db_config_util(test_client, name="DB Conflict 1")
    config2 = create_ext_db_config_util(test_client, name="DB Conflict 2")

    update_payload = {"name": config2["name"]} # Try to update config1's name to config2's
    response = test_client.put(f"/api/v1/external-db-configs/{config1['id']}", json=update_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]

def test_delete_external_db_config_ok(test_client: TestClient):
    created_config = create_ext_db_config_util(test_client, name="Delete Me DB")
    config_id = created_config["id"]

    response_delete = test_client.delete(f"/api/v1/external-db-configs/{config_id}")
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT

    response_get = test_client.get(f"/api/v1/external-db-configs/{config_id}")
    assert response_get.status_code == status.HTTP_404_NOT_FOUND 
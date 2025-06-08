"""
Tests for MCP Definition and Version CRUD API endpoints.
"""
import pytest
import uuid
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from mcp.schemas.mcp import MCPDefinitionCreate, MCPDefinitionUpdate, MCPVersionCreate
from mcp.core.mcp_configs import LLMConfig # For creating version config

# --- Helper to create a definition for version tests ---
def create_definition_util(client: TestClient, name: str = "Test Def for Versions") -> dict:
    response = client.post("/api/v1/mcp/definitions/", json={"name": name, "description": "Test"})
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

# --- MCPDefinition Tests ---

def test_create_mcp_definition_ok(test_client: TestClient):
    payload = {"name": "My First MCP Def", "description": "A great definition."}
    response = test_client.post("/api/v1/mcp/definitions/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "versions" in data and len(data["versions"]) == 0

def test_create_mcp_definition_with_initial_version(test_client: TestClient):
    llm_config_payload = {"model": "test-llm", "temperature": 0.7, "type": "LLM Prompt Agent"}
    initial_version_payload = {
        "version_string": "1.0.0",
        "mcp_type": "LLM Prompt Agent",
        "config": llm_config_payload
    }
    def_payload = {
        "name": "Def With Initial Version",
        "description": "This one has a version from the start.",
        "initial_version": initial_version_payload
    }
    response = test_client.post("/api/v1/mcp/definitions/", json=def_payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == def_payload["name"]
    assert len(data["versions"]) == 1
    version_data = data["versions"][0]
    assert version_data["version_string"] == "1.0.0"
    assert version_data["mcp_type"] == "LLM Prompt Agent"
    assert version_data["config"]["model"] == "test-llm" # Alias 'model' used in LLMConfig

def test_create_mcp_definition_duplicate_name(test_client: TestClient):
    payload = {"name": "Unique Def Name", "description": "First instance."}
    response1 = test_client.post("/api/v1/mcp/definitions/", json=payload)
    assert response1.status_code == status.HTTP_201_CREATED
    
    response2 = test_client.post("/api/v1/mcp/definitions/", json=payload)
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response2.json()["detail"]

def test_get_mcp_definition_ok(test_client: TestClient):
    created_def = create_definition_util(test_client, name="Get Me Def")
    def_id = created_def["id"]

    response = test_client.get(f"/api/v1/mcp/definitions/{def_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == def_id
    assert data["name"] == "Get Me Def"

def test_get_mcp_definition_not_found(test_client: TestClient):
    random_uuid = uuid.uuid4()
    response = test_client.get(f"/api/v1/mcp/definitions/{random_uuid}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_mcp_definitions(test_client: TestClient):
    create_definition_util(test_client, name="List Def 1")
    create_definition_util(test_client, name="List Def 2")

    response = test_client.get("/api/v1/mcp/definitions/?limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 2
    assert len(data["items"]) <= 10
    # Check if the created items are in the list (order might vary)
    names_in_response = [item["name"] for item in data["items"]]
    assert "List Def 1" in names_in_response
    assert "List Def 2" in names_in_response

def test_update_mcp_definition_ok(test_client: TestClient):
    created_def = create_definition_util(test_client, name="Update Original Name")
    def_id = created_def["id"]
    
    update_payload = {"name": "Updated Def Name", "description": "Now updated."}
    response = test_client.put(f"/api/v1/mcp/definitions/{def_id}", json=update_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_payload["name"]
    assert data["description"] == update_payload["description"]
    assert data["id"] == def_id

def test_update_mcp_definition_name_conflict(test_client: TestClient):
    def1 = create_definition_util(test_client, name="Update Conflict Def 1")
    def2 = create_definition_util(test_client, name="Update Conflict Def 2") # Existing name

    update_payload = {"name": def2["name"]} # Try to update def1's name to def2's name
    response = test_client.put(f"/api/v1/mcp/definitions/{def1['id']}", json=update_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]

def test_delete_mcp_definition_ok(test_client: TestClient):
    created_def = create_definition_util(test_client, name="Delete Me Def")
    def_id = created_def["id"]

    response_delete = test_client.delete(f"/api/v1/mcp/definitions/{def_id}")
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT

    response_get = test_client.get(f"/api/v1/mcp/definitions/{def_id}")
    assert response_get.status_code == status.HTTP_404_NOT_FOUND

# --- MCPVersion Tests ---

def test_create_mcp_version_for_definition_ok(test_client: TestClient):
    mcp_def = create_definition_util(test_client, name="Def For Version Test")
    mcp_def_id = mcp_def["id"]

    llm_config_data = {"model": "gpt-3.5-turbo", "type": "LLM Prompt Agent"}
    version_payload = {
        "version_string": "0.1.0",
        "mcp_type": "LLM Prompt Agent",
        "description": "First version of this cool agent.",
        "config": llm_config_data
    }
    response = test_client.post(f"/api/v1/mcp/definitions/{mcp_def_id}/versions/", json=version_payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["version_string"] == version_payload["version_string"]
    assert data["mcp_type"] == version_payload["mcp_type"]
    assert data["config"]["model"] == "gpt-3.5-turbo"
    assert data["mcp_definition_id"] == mcp_def_id

def test_create_mcp_version_duplicate_version_string(test_client: TestClient):
    mcp_def = create_definition_util(test_client, name="Def For Duplicate Version Test")
    mcp_def_id = mcp_def["id"]
    
    version_payload = {"version_string": "1.1.0", "mcp_type": "Python Script", "config": {"codeContent": "pass", "type": "Python Script"}}
    response1 = test_client.post(f"/api/v1/mcp/definitions/{mcp_def_id}/versions/", json=version_payload)
    assert response1.status_code == status.HTTP_201_CREATED

    response2 = test_client.post(f"/api/v1/mcp/definitions/{mcp_def_id}/versions/", json=version_payload)
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response2.json()["detail"]

def test_create_mcp_version_mismatch_type_and_config(test_client: TestClient):
    mcp_def = create_definition_util(test_client, name="Def For Type Mismatch Test")
    mcp_def_id = mcp_def["id"]
    version_payload = {
        "version_string": "1.0.0",
        "mcp_type": "LLM Prompt Agent", # Outer type
        "config": {"codeContent": "print('hi')", "type": "Python Script"} # Inner config type is different
    }
    response = test_client.post(f"/api/v1/mcp/definitions/{mcp_def_id}/versions/", json=version_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "does not match config.type" in response.json()["detail"]

def test_list_mcp_versions_for_definition(test_client: TestClient):
    mcp_def = create_definition_util(test_client, name="Def For Listing Versions")
    mcp_def_id = mcp_def["id"]

    # Create a couple of versions
    v_payload1 = {"version_string": "0.1.0", "mcp_type": "Python Script", "config": {"type": "Python Script", "codeContent": "v1"}}
    test_client.post(f"/api/v1/mcp/definitions/{mcp_def_id}/versions/", json=v_payload1)
    v_payload2 = {"version_string": "0.2.0", "mcp_type": "Python Script", "config": {"type": "Python Script", "codeContent": "v2"}}
    test_client.post(f"/api/v1/mcp/definitions/{mcp_def_id}/versions/", json=v_payload2)

    response = test_client.get(f"/api/v1/mcp/definitions/{mcp_def_id}/versions/?limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    version_strings = [item["version_string"] for item in data["items"]]
    assert "0.1.0" in version_strings
    assert "0.2.0" in version_strings

def test_get_mcp_version_by_id_ok(test_client: TestClient):
    mcp_def = create_definition_util(test_client, name="Def For Get Version By ID")
    mcp_def_id = mcp_def["id"]
    v_payload = {"version_string": "3.0.0", "mcp_type": "LLM Prompt Agent", "config": {"model": "test", "type": "LLM Prompt Agent"}}
    created_version_res = test_client.post(f"/api/v1/mcp/definitions/{mcp_def_id}/versions/", json=v_payload)
    version_id = created_version_res.json()["id"]

    response = test_client.get(f"/api/v1/mcp/versions/{version_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == version_id
    assert data["version_string"] == "3.0.0"

def test_get_mcp_version_not_found(test_client: TestClient):
    random_uuid = uuid.uuid4()
    response = test_client.get(f"/api/v1/mcp/versions/{random_uuid}")
    assert response.status_code == status.HTTP_404_NOT_FOUND 
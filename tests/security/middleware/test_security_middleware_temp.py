import pytest
from fastapi.testclient import TestClient
from tests.conftest import test_client, test_settings, test_headers, test_security_headers, test_request
from tests.utils.test_utils import get_test_data

@pytest.mark.unit
@pytest.mark.security
def test_valid_host_header(test_client: TestClient, test_settings: dict):
    """Test valid host header."""
    headers = {**test_headers, **test_security_headers, "Host": "localhost"}
    response = test_client.get("/test", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Test successful"}

@pytest.mark.unit
@pytest.mark.security
def test_invalid_host_header(test_client: TestClient, test_settings: dict):
    """Test invalid host header."""
    headers = {**test_headers, **test_security_headers, "Host": "malicious.com"}
    response = test_client.get("/test", headers=headers)
    assert response.status_code == 400
    assert "invalid host" in response.text.lower() or "host header" in response.text.lower()

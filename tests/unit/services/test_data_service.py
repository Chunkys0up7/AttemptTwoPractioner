from mcp.api.services.data_service import (
    get_data,
    transform_data,
    validate_data,
    DataServiceError
)
import pytest

def test_get_data_valid():
    result = get_data("valid_id")
    assert result is not None
    assert "data" in result

def test_get_data_invalid():
    with pytest.raises(DataServiceError):
        get_data("invalid_id")

def test_transform_data():
    data = {"value": 1}
    transformed = transform_data(data)
    assert transformed["value"] == 2  # Example transformation

def test_validate_data_valid():
    data = {"field": "value"}
    assert validate_data(data) is True

def test_validate_data_invalid():
    data = {"field": 123}  # Suppose this is invalid
    with pytest.raises(DataServiceError):
        validate_data(data) 
from mcp.api.services.auth_service import authenticate_user

def test_authenticate_user_valid():
    user = authenticate_user("admin", "password")
    assert user is not None
    assert user["username"] == "admin"

def test_authenticate_user_invalid():
    user = authenticate_user("admin", "wrongpass")
    assert user is None 
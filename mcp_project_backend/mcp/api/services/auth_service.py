from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from mcp.core.security.jwt_manager import JWTManager
from mcp.core.config import settings

router = APIRouter()

def authenticate_user(username: str, password: str):
    # Placeholder for authentication logic
    # Replace with real user lookup and password check
    if username == "admin" and password == "password":
        return {"username": username}
    return None

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # Return a fake token for now
    return {"access_token": "fake-token", "token_type": "bearer"}

@router.post("/refresh")
def refresh_token(refresh_token: str = Body(..., embed=True)):
    payload = JWTManager.verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload")
    # Issue new access token
    access_token = JWTManager.create_access_token({"sub": user_id})
    return {"access_token": access_token, "token_type": "bearer"} 
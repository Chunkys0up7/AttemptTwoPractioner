from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

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
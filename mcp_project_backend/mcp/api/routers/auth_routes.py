from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from mcp.api.deps import get_db_session
from mcp.api.schemas.auth_schemas import UserCreate, UserLoginRequest, TokenResponse, UserRead
from mcp.core.security.jwt_manager import JWTManager
from mcp.core.security.password_manager import PasswordManager
from mcp.db.crud.crud_user import crud_user
from mcp.db.models.user import User
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from typing import Optional

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/auth/register", response_model=UserRead)
def register_user(user_in: UserCreate, db: Session = Depends(get_db_session)):
    existing = crud_user.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud_user.create(db, obj_in=user_in)
    return user

@router.post("/auth/login", response_model=TokenResponse)
def login_for_access_token(form_data: UserLoginRequest, db: Session = Depends(get_db_session)):
    user = crud_user.get_by_email(db, email=form_data.email)
    if not user or not PasswordManager.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = JWTManager.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = JWTManager.decode_token(token)
        user_id: Optional[str] = payload.get("sub") if payload else None
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/auth/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

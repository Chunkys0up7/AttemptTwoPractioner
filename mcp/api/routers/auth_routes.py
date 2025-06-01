from mcp.core.security.rbac_service import rbac_service
from fastapi import Security
from mcp.api.schemas.auth_schemas import UserRead
from sqlalchemy.orm import Session
from mcp.api.crud.crud_user import crud_user
from mcp.api.models.user import User
from fastapi import HTTPException, Depends
from mcp.core.security.session_manager import session_manager

def require_role(required_role: str):
    def role_dependency(current_user: User = Depends(get_current_user)):
        if not rbac_service.has_role(current_user.role_name, required_role):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_dependency

@router.get("/auth/admin-only", response_model=UserRead)
def admin_only_endpoint(current_user: User = Depends(require_role("Admin"))):
    return current_user

@router.get("/users", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session), current_user: User = Depends(require_role("Admin"))):
    return crud_user.list(db, skip=skip, limit=limit)

@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_in: dict, db: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Only admin or the user themselves can update
    if current_user.role_name != "Admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    updated = crud_user.update(db, db_obj=user, obj_in=user_in)
    session_manager.audit_action(current_user.id, "update_user", f"target_user_id={user_id}")
    return updated

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db_session), current_user: User = Depends(require_role("Admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud_user.delete(db, db_obj=user)
    session_manager.audit_action(current_user.id, "delete_user", f"target_user_id={user_id}")
    return {"detail": "User deleted"}

@router.post("/auth/login", response_model=TokenResponse)
def login_for_access_token(form_data: UserLoginRequest, db: Session = Depends(get_db_session)):
    user = crud_user.get_by_email(db, email=form_data.email)
    if not user or not PasswordManager.verify_password(form_data.password, user.hashed_password):
        session_manager.audit_action(user_id=None, action="login_failed", details=form_data.email)
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = session_manager.create_session(user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/logout")
def logout(current_user: User = Depends(get_current_user)):
    session_manager.revoke_session(current_user.id)
    return {"detail": "Logged out"} 
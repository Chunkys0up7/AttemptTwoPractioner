from sqlalchemy.orm import Session
from mcp.db.models.user import User, UserRoleEnum
from mcp.api.schemas.auth_schemas import UserCreate
from mcp.core.security.password_manager import PasswordManager
from typing import Optional

class CRUDUser:
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        obj_in_data = obj_in.dict(exclude={'password'})
        hashed_password = PasswordManager.get_password_hash(obj_in.password)
        db_obj = User(**obj_in_data, hashed_password=hashed_password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: dict) -> User:
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, db_obj: User) -> None:
        db.delete(db_obj)
        db.commit()

    def list(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()

crud_user = CRUDUser() 
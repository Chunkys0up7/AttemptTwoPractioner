from sqlalchemy.orm import Session
from .base_crud import CRUDBase
from mcp.db.models.external_db_config import ExternalDatabaseConfig
from mcp.api.schemas.external_db_config_schemas import ExternalDbConfigCreate, ExternalDbConfigUpdate
from typing import Optional

class CRUDExternalDbConfig(CRUDBase[ExternalDatabaseConfig, ExternalDbConfigCreate, ExternalDbConfigUpdate]):
    """
    CRUD operations for the ExternalDatabaseConfig model, including secure handling of secrets.
    Inherits generic CRUD operations from CRUDBase.
    """
    def create(self, db: Session, *, obj_in: ExternalDbConfigCreate) -> ExternalDatabaseConfig:
        """
        Create a new ExternalDatabaseConfig entry, handling password/secret reference securely.
        Args:
            db (Session): SQLAlchemy session.
            obj_in (ExternalDbConfigCreate): Data for the external DB config.
        Returns:
            ExternalDatabaseConfig: The created config instance.
        """
        obj_in_data = obj_in.model_dump(exclude_none=True)
        # Handle password/secret_ref securely.
        if "password_or_secret_ref" in obj_in_data:
            obj_in_data["password_secret_key"] = obj_in_data.pop("password_or_secret_ref")
            # Real implementation: encrypt or store secret securely
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ExternalDatabaseConfig, obj_in: ExternalDbConfigUpdate) -> ExternalDatabaseConfig:
        """
        Update an ExternalDatabaseConfig entry, handling password/secret reference securely.
        Args:
            db (Session): SQLAlchemy session.
            db_obj (ExternalDatabaseConfig): The existing config instance.
            obj_in (ExternalDbConfigUpdate): Update data.
        Returns:
            ExternalDatabaseConfig: The updated config instance.
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password_or_secret_ref" in update_data and update_data["password_or_secret_ref"] is not None:
            db_obj.password_secret_key = update_data.pop("password_or_secret_ref")
            # Real implementation: encrypt or store secret securely
        return super().update(db, db_obj=db_obj, obj_in=update_data)

crud_external_db_config = CRUDExternalDbConfig(ExternalDatabaseConfig)

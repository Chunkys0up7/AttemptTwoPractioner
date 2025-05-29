"""
Service layer for ExternalDatabaseConfig CRUD operations.
"""
import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from mcp.db.models import ExternalDatabaseConfig
from mcp.schemas.external_db_config import ExternalDbConfigCreate, ExternalDbConfigUpdate


class ExternalDbConfigService:
    def __init__(self, db: Session):
        self.db = db

    def create_config(self, config_create: ExternalDbConfigCreate) -> ExternalDatabaseConfig:
        existing_config = self.db.query(ExternalDatabaseConfig).filter(
            ExternalDatabaseConfig.name == config_create.name).first()
        if existing_config:
            raise ValueError(
                f"ExternalDatabaseConfig with name '{config_create.name}' already exists.")

        db_config = ExternalDatabaseConfig(**config_create.model_dump())
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        return db_config

    def get_config(self, config_id: uuid.UUID) -> Optional[ExternalDatabaseConfig]:
        return self.db.query(ExternalDatabaseConfig).filter(ExternalDatabaseConfig.id == config_id).first()

    def get_config_by_name(self, name: str) -> Optional[ExternalDatabaseConfig]:
        return self.db.query(ExternalDatabaseConfig).filter(ExternalDatabaseConfig.name == name).first()

    def list_configs(self, skip: int = 0, limit: int = 100) -> Tuple[List[ExternalDatabaseConfig], int]:
        query = self.db.query(ExternalDatabaseConfig)
        total = query.count()
        configs = query.order_by(ExternalDatabaseConfig.name).offset(
            skip).limit(limit).all()
        return configs, total

    def update_config(self, config_id: uuid.UUID, config_update: ExternalDbConfigUpdate) -> Optional[ExternalDatabaseConfig]:
        db_config = self.get_config(config_id)
        if not db_config:
            return None

        update_data = config_update.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != db_config.name:
            existing_config = self.db.query(ExternalDatabaseConfig).filter(
                ExternalDatabaseConfig.name == update_data["name"]).first()
            if existing_config:
                raise ValueError(
                    f"ExternalDatabaseConfig with name '{update_data['name']}' already exists.")

        for key, value in update_data.items():
            setattr(db_config, key, value)

        self.db.commit()
        self.db.refresh(db_config)
        return db_config

    def delete_config(self, config_id: uuid.UUID) -> bool:
        db_config = self.get_config(config_id)
        if not db_config:
            return False
        self.db.delete(db_config)
        self.db.commit()
        return True

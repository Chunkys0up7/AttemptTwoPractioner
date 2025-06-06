from sqlalchemy.orm import Session
from .base_crud import CRUDBase
from mcp.db.models.action_log import ActionLog
from typing import Optional, Dict, Any, List
from datetime import datetime

class CRUDActionLog(CRUDBase[ActionLog, dict, dict]):
    """
    CRUD operations for the ActionLog model, including log creation and entity-based queries.
    Inherits generic CRUD operations from CRUDBase.
    """
    def create_log(
        self,
        db: Session,
        *,
        actor_id: Optional[str],
        action_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> ActionLog:
        """
        Create a new ActionLog entry.
        Args:
            db (Session): SQLAlchemy session.
            actor_id (Optional[str]): ID of the actor performing the action.
            action_type (str): Type of action performed.
            entity_type (Optional[str]): Type of the entity involved.
            entity_id (Optional[str]): ID of the entity involved.
            details (Optional[Dict[str, Any]]): Additional details/context.
        Returns:
            ActionLog: The created ActionLog instance.
        """
        log_entry = self.model(
            timestamp=datetime.utcnow(),
            actor_id=actor_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            details=details
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    def get_logs_for_entity(
        self, db: Session, *, entity_type: str, entity_id: str, skip: int = 0, limit: int = 100
    ) -> List[ActionLog]:
        """
        Retrieve logs for a specific entity.
        Args:
            db (Session): SQLAlchemy session.
            entity_type (str): Type of the entity.
            entity_id (str): ID of the entity.
            skip (int): Number of records to skip.
            limit (int): Maximum number of records to return.
        Returns:
            List[ActionLog]: List of ActionLog entries for the entity.
        """
        return (
            db.query(self.model)
            .filter(self.model.entity_type == entity_type, self.model.entity_id == str(entity_id))
            .order_by(self.model.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

crud_action_log = CRUDActionLog(ActionLog)

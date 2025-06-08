from typing import Optional, Dict, Any, List, Union
from sqlalchemy.orm import Session
from datetime import datetime
import json
import logging
from mcp.core.settings import settings
from mcp.core.monitoring import monitor

# Set up logging
logger = logging.getLogger(__name__)

class AuditEvent:
    """
    Audit event data structure.
    
    Args:
        actor_id: User ID, system component name, or API key ID.
        action_type: Type of action (e.g., 'MCP_VERSION_CREATED').
        entity_type: Type of entity affected (optional).
        entity_id: ID of the entity affected (optional).
        details: Additional context as a dictionary (optional).
        severity: Event severity level (INFO, WARNING, ERROR).
    """
    def __init__(
        self,
        actor_id: Optional[str],
        action_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "INFO"
    ):
        self.timestamp = datetime.utcnow()
        self.actor_id = actor_id
        self.action_type = action_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.details = details
        self.severity = severity
        self.request_id = settings.REQUEST_ID if hasattr(settings, 'REQUEST_ID') else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'actor_id': self.actor_id,
            'action_type': self.action_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'severity': self.severity,
            'request_id': self.request_id
        }

class AuditingService:
    """
    Service for creating audit log entries.
    
    Responsibilities:
    - Record significant events for auditing and traceability.
    - Support multiple storage backends.
    - Provide query capabilities.
    - Integrate with monitoring system.
    """
    def __init__(self, db_session: Session):
        """
        Initialize the AuditingService.
        
        Args:
            db_session: SQLAlchemy session for DB operations.
        """
        self.db_session = db_session
        self._audit_events: List[AuditEvent] = []
        
    def create_action_log_entry(
        self,
        actor_id: Optional[str],
        action_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "INFO",
        commit: bool = False
    ) -> AuditEvent:
        """
        Create an audit log entry.
        
        Args:
            actor_id: User ID, system component name, or API key ID.
            action_type: Type of action (e.g., 'MCP_VERSION_CREATED').
            entity_type: Type of entity affected (optional).
            entity_id: ID of the entity affected (optional).
            details: Additional context as a dictionary (optional).
            severity: Event severity level (INFO, WARNING, ERROR).
            commit: Whether to commit immediately (default: False).
        
        Returns:
            AuditEvent: The created audit event.
        
        Raises:
            ValueError: If invalid severity level is provided.
        """
        if severity not in ["INFO", "WARNING", "ERROR"]:
            raise ValueError(f"Invalid severity level: {severity}")
            
        event = AuditEvent(
            actor_id=actor_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            severity=severity
        )
        
        # Add to in-memory buffer
        self._audit_events.append(event)
        
        # Store in database
        try:
            # TODO: Implement actual database storage
            # self.db_session.add(event)
            if commit:
                self.db_session.commit()
        except Exception as e:
            logger.error(f"Failed to store audit event: {str(e)}")
            self.db_session.rollback()
            raise
        
        # Update monitoring metrics
        monitor.increment_event('audit_event_created')
        
        return event

    def get_audit_events(
        self,
        actor_id: Optional[str] = None,
        action_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query audit events based on criteria.
        
        Args:
            actor_id: Filter by actor ID.
            action_type: Filter by action type.
            entity_type: Filter by entity type.
            start_time: Filter events after this time.
            end_time: Filter events before this time.
            limit: Maximum number of results.
        
        Returns:
            List of audit events as dictionaries.
        """
        try:
            # TODO: Implement actual database query
            # query = self.db_session.query(AuditEvent)
            # if actor_id:
            #     query = query.filter(AuditEvent.actor_id == actor_id)
            # if action_type:
            #     query = query.filter(AuditEvent.action_type == action_type)
            # if entity_type:
            #     query = query.filter(AuditEvent.entity_type == entity_type)
            # if start_time:
            #     query = query.filter(AuditEvent.timestamp >= start_time)
            # if end_time:
            #     query = query.filter(AuditEvent.timestamp <= end_time)
            # return query.order_by(AuditEvent.timestamp.desc()).limit(limit).all()
            
            # For now, filter in-memory events
            filtered_events = self._audit_events
            if actor_id:
                filtered_events = [e for e in filtered_events if e.actor_id == actor_id]
            if action_type:
                filtered_events = [e for e in filtered_events if e.action_type == action_type]
            if entity_type:
                filtered_events = [e for e in filtered_events if e.entity_type == entity_type]
            if start_time:
                filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
            if end_time:
                filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
            
            return [e.to_dict() for e in filtered_events[-limit:]]
            
        except Exception as e:
            logger.error(f"Failed to query audit events: {str(e)}")
            raise

    def export_audit_logs(self, format: str = "json") -> Union[str, bytes]:
        """
        Export audit logs in specified format.
        
        Args:
            format: Output format (json, csv)
        
        Returns:
            str or bytes: Exported audit logs
        
        Raises:
            ValueError: If invalid format is specified.
        """
        if format == "json":
            return json.dumps([e.to_dict() for e in self._audit_events])
        elif format == "csv":
            # TODO: Implement CSV export
            raise NotImplementedError("CSV export not implemented yet")
        else:
            raise ValueError(f"Unsupported format: {format}")

    def clear_audit_logs(self) -> None:
        """Clear in-memory audit logs."""
        self._audit_events.clear()
        logger.info("Cleared in-memory audit logs")

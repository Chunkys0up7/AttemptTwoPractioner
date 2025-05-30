"""
Tests for the auditing service and action logging functionality.
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from mcp.db.models.action_log import ActionLog, ActionType, EntityType
from mcp.core.services.auditing_service import AuditingService

def test_create_action_log_entry(db_session: Session):
    """Test creating a basic action log entry."""
    service = AuditingService(db_session)
    
    # Create a test action log entry
    log_entry = service.create_action_log_entry(
        actor_id="test_user",
        action_type=ActionType.CREATE,
        entity_type=EntityType.MCP_DEFINITION,
        entity_id=1,
        details={"name": "Test MCP", "description": "Test description"}
    )
    
    # Verify the entry was created
    assert log_entry.id is not None
    assert log_entry.actor_id == "test_user"
    assert log_entry.action_type == ActionType.CREATE
    assert log_entry.entity_type == EntityType.MCP_DEFINITION
    assert log_entry.entity_id == 1
    assert log_entry.details == {"name": "Test MCP", "description": "Test description"}
    assert isinstance(log_entry.timestamp, datetime)

def test_create_action_log_entry_without_details(db_session: Session):
    """Test creating an action log entry without details."""
    service = AuditingService(db_session)
    
    # Create a test action log entry without details
    log_entry = service.create_action_log_entry(
        actor_id="test_user",
        action_type=ActionType.DELETE,
        entity_type=EntityType.WORKFLOW_RUN,
        entity_id=1
    )
    
    # Verify the entry was created
    assert log_entry.id is not None
    assert log_entry.actor_id == "test_user"
    assert log_entry.action_type == ActionType.DELETE
    assert log_entry.entity_type == EntityType.WORKFLOW_RUN
    assert log_entry.entity_id == 1
    assert log_entry.details == {}
    assert isinstance(log_entry.timestamp, datetime)

def test_create_action_log_entry_with_complex_details(db_session: Session):
    """Test creating an action log entry with complex details."""
    service = AuditingService(db_session)
    
    # Create a test action log entry with complex details
    complex_details = {
        "workflow_id": 1,
        "steps": [
            {"id": 1, "name": "Step 1", "status": "completed"},
            {"id": 2, "name": "Step 2", "status": "running"}
        ],
        "parameters": {
            "input_file": "data.csv",
            "output_format": "json"
        }
    }
    
    log_entry = service.create_action_log_entry(
        actor_id="test_user",
        action_type=ActionType.UPDATE,
        entity_type=EntityType.WORKFLOW_RUN,
        entity_id=1,
        details=complex_details
    )
    
    # Verify the entry was created with complex details
    assert log_entry.id is not None
    assert log_entry.details == complex_details

def test_action_log_entry_retrieval(db_session: Session):
    """Test retrieving action log entries."""
    service = AuditingService(db_session)
    
    # Create multiple test entries
    service.create_action_log_entry(
        actor_id="user1",
        action_type=ActionType.CREATE,
        entity_type=EntityType.MCP_DEFINITION,
        entity_id=1,
        details={"name": "MCP 1"}
    )
    
    service.create_action_log_entry(
        actor_id="user2",
        action_type=ActionType.UPDATE,
        entity_type=EntityType.MCP_DEFINITION,
        entity_id=1,
        details={"name": "MCP 1 Updated"}
    )
    
    # Query the entries
    entries = db_session.query(ActionLog).all()
    assert len(entries) == 2
    
    # Verify the entries are ordered by timestamp (newest first)
    assert entries[0].timestamp > entries[1].timestamp

def test_action_log_entry_validation(db_session: Session):
    """Test validation of action log entries."""
    service = AuditingService(db_session)
    
    # Test with invalid action type
    with pytest.raises(ValueError):
        service.create_action_log_entry(
            actor_id="test_user",
            action_type="INVALID_ACTION",
            entity_type=EntityType.MCP_DEFINITION,
            entity_id=1
        )
    
    # Test with invalid entity type
    with pytest.raises(ValueError):
        service.create_action_log_entry(
            actor_id="test_user",
            action_type=ActionType.CREATE,
            entity_type="INVALID_ENTITY",
            entity_id=1
        )
    
    # Test with negative entity ID
    with pytest.raises(ValueError):
        service.create_action_log_entry(
            actor_id="test_user",
            action_type=ActionType.CREATE,
            entity_type=EntityType.MCP_DEFINITION,
            entity_id=-1
        ) 
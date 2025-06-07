"""
Tests for the auditing service and action logging functionality.
"""
import pytest
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from mcp.core.auditing_service import AuditingService, AuditEvent
from mcp.core.config import settings
from mcp.core.monitoring import monitor

@pytest.fixture
def mock_db_session() -> Session:
    """Mock database session for testing."""
    class MockSession:
        def add(self, obj):
            pass
        
        def commit(self):
            pass
        
        def rollback(self):
            pass
    
    return MockSession()

@pytest.fixture
def mock_settings() -> settings:
    """Mock settings for testing."""
    class MockSettings:
        REQUEST_ID = "test-request-id"
    
    return MockSettings()

@pytest.fixture
def mock_monitor() -> monitor:
    """Mock monitoring instance for testing."""
    class MockMonitor:
        def increment_event(self, event: str, labels: Dict[str, Any] = None) -> None:
            pass
    
    return MockMonitor()

@pytest.fixture
def auditing_service(mock_db_session: Session, mock_settings: settings, mock_monitor: monitor) -> AuditingService:
    """Create an instance of AuditingService for testing."""
    return AuditingService(mock_db_session)

def test_create_action_log_entry(auditing_service: AuditingService):
    """Test creating a basic action log entry."""
    # Create a test action log entry
    event = auditing_service.create_action_log_entry(
        actor_id="test_user",
        action_type="CREATE",
        entity_type="MCP_DEFINITION",
        entity_id=1,
        details={"name": "Test MCP", "description": "Test description"},
        severity="INFO"
    )
    
    # Verify the event was created
    assert isinstance(event, AuditEvent)
    assert event.actor_id == "test_user"
    assert event.action_type == "CREATE"
    assert event.entity_type == "MCP_DEFINITION"
    assert event.entity_id == 1
    assert event.details == {"name": "Test MCP", "description": "Test description"}
    assert event.severity == "INFO"
    assert isinstance(event.timestamp, datetime)
    assert event.request_id == "test-request-id"

def test_create_action_log_entry_with_severity(auditing_service: AuditingService):
    """Test creating an action log entry with different severity levels."""
    # Test INFO severity
    event = auditing_service.create_action_log_entry(
        actor_id="test_user",
        action_type="CREATE",
        severity="INFO"
    )
    assert event.severity == "INFO"
    
    # Test WARNING severity
    event = auditing_service.create_action_log_entry(
        actor_id="test_user",
        action_type="WARNING",
        severity="WARNING"
    )
    assert event.severity == "WARNING"
    
    # Test ERROR severity
    event = auditing_service.create_action_log_entry(
        actor_id="test_user",
        action_type="ERROR",
        severity="ERROR"
    )
    assert event.severity == "ERROR"

def test_create_action_log_entry_invalid_severity(auditing_service: AuditingService):
    """Test creating an action log entry with invalid severity."""
    with pytest.raises(ValueError):
        auditing_service.create_action_log_entry(
            actor_id="test_user",
            action_type="CREATE",
            severity="INVALID"
        )

def test_get_audit_events(auditing_service: AuditingService):
    """Test retrieving audit events with various filters."""
    # Create test events
    event1 = auditing_service.create_action_log_entry(
        actor_id="user1",
        action_type="CREATE",
        entity_type="MCP_DEFINITION",
        entity_id=1,
        severity="INFO"
    )
    event2 = auditing_service.create_action_log_entry(
        actor_id="user2",
        action_type="UPDATE",
        entity_type="WORKFLOW_DEFINITION",
        entity_id=2,
        severity="WARNING"
    )
    
    # Test filtering by actor
    events = auditing_service.get_audit_events(actor_id="user1")
    assert len(events) == 1
    assert events[0]["actor_id"] == "user1"
    
    # Test filtering by action type
    events = auditing_service.get_audit_events(action_type="CREATE")
    assert len(events) == 1
    assert events[0]["action_type"] == "CREATE"
    
    # Test filtering by time range
    start_time = datetime.now()
    event3 = auditing_service.create_action_log_entry(
        actor_id="user3",
        action_type="DELETE",
        entity_type="WORKFLOW_RUN",
        entity_id=3,
        severity="ERROR"
    )
    end_time = datetime.now()
    
    events = auditing_service.get_audit_events(
        start_time=start_time,
        end_time=end_time
    )
    assert len(events) == 1
    assert events[0]["action_type"] == "DELETE"

def test_export_audit_logs(auditing_service: AuditingService):
    """Test exporting audit logs in different formats."""
    # Create test events
    auditing_service.create_action_log_entry(
        actor_id="user1",
        action_type="CREATE",
        entity_type="MCP_DEFINITION",
        entity_id=1,
        severity="INFO"
    )
    auditing_service.create_action_log_entry(
        actor_id="user2",
        action_type="UPDATE",
        entity_type="WORKFLOW_DEFINITION",
        entity_id=2,
        severity="WARNING"
    )
    
    # Test JSON export
    json_export = auditing_service.export_audit_logs(format="json")
    assert isinstance(json_export, str)
    events = json.loads(json_export)
    assert len(events) == 2
    
    # Test invalid format
    with pytest.raises(ValueError):
        auditing_service.export_audit_logs(format="invalid")

def test_clear_audit_logs(auditing_service: AuditingService):
    """Test clearing audit logs."""
    # Create test events
    auditing_service.create_action_log_entry(
        actor_id="user1",
        action_type="CREATE",
        entity_type="MCP_DEFINITION",
        entity_id=1,
        severity="INFO"
    )
    
    # Verify events exist
    events = auditing_service.get_audit_events()
    assert len(events) > 0
    
    # Clear logs
    auditing_service.clear_audit_logs()
    
    # Verify logs are cleared
    events = auditing_service.get_audit_events()
    assert len(events) == 0

def test_create_action_log_entry_without_details(auditing_service: AuditingService):
    """Test creating an action log entry without details."""
    service = auditing_service
    
    # Create a test action log entry without details
    log_entry = service.create_action_log_entry(
        actor_id="test_user",
        action_type="DELETE",
        entity_type="WORKFLOW_RUN",
        entity_id=1
    )
    
    # Verify the entry was created
    assert log_entry.id is not None
    assert log_entry.actor_id == "test_user"
    assert log_entry.action_type == "DELETE"
    assert log_entry.entity_type == "WORKFLOW_RUN"
    assert log_entry.entity_id == 1
    assert log_entry.details == {}
    assert isinstance(log_entry.timestamp, datetime)

def test_create_action_log_entry_with_complex_details(auditing_service: AuditingService):
    """Test creating an action log entry with complex details."""
    service = auditing_service
    
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
        action_type="UPDATE",
        entity_type="WORKFLOW_RUN",
        entity_id=1,
        details=complex_details
    )
    
    # Verify the entry was created with complex details
    assert log_entry.id is not None
    assert log_entry.details == complex_details

def test_action_log_entry_retrieval(auditing_service: AuditingService):
    """Test retrieving action log entries."""
    service = auditing_service
    
    # Create multiple test entries
    service.create_action_log_entry(
        actor_id="user1",
        action_type="CREATE",
        entity_type="MCP_DEFINITION",
        entity_id=1,
        details={"name": "MCP 1"}
    )
    
    service.create_action_log_entry(
        actor_id="user2",
        action_type="UPDATE",
        entity_type="MCP_DEFINITION",
        entity_id=1,
        details={"name": "MCP 1 Updated"}
    )
    
    # Query the entries
    entries = service.get_audit_events()
    assert len(entries) == 2
    
    # Verify the entries are ordered by timestamp (newest first)
    assert entries[0].timestamp > entries[1].timestamp

def test_action_log_entry_validation(auditing_service: AuditingService):
    """Test validation of action log entries."""
    service = auditing_service
    
    # Test with invalid action type
    with pytest.raises(ValueError):
        service.create_action_log_entry(
            actor_id="test_user",
            action_type="INVALID_ACTION",
            entity_type="MCP_DEFINITION",
            entity_id=1
        )
    
    # Test with invalid entity type
    with pytest.raises(ValueError):
        service.create_action_log_entry(
            actor_id="test_user",
            action_type="CREATE",
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
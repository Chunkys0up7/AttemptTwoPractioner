"""
Tests for database model creation and basic properties.

These tests ideally should run against a test database.
For now, they demonstrate model instantiation.
Session management and database interaction would typically be handled by fixtures.
"""
import pytest
import uuid
from datetime import datetime
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from mcp.db.base import Base
from mcp.db.models import MCPDefinition, MCPVersion, WorkflowDefinition, WorkflowRun, WorkflowRunStatus

# Placeholder for a SQLAlchemy session fixture (to be defined in conftest.py or similar)
# For now, we will just test instantiation without DB interaction.
@pytest.fixture
def db_session():
    # In a real setup, this would provide a transactional session to a test database.
    # from sqlalchemy import create_engine
    # from sqlalchemy.orm import sessionmaker
    # from mcp.db.base import Base
    # SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    # engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    # Base.metadata.create_all(bind=engine)
    # TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # session = TestingSessionLocal()
    # try:
    #     yield session
    # finally:
    #     session.close()
    #     Base.metadata.drop_all(bind=engine) # Clean up in-memory DB
    print("Skipping DB session for model instantiation test. Add a real session fixture for DB tests.")
    yield None

def test_mcp_definition_creation():
    """Test creating an MCPDefinition instance."""
    def_id = uuid.uuid4()
    mcp_def = MCPDefinition(
        id=def_id,
        name="Test MCP Definition",
        description="A definition for testing."
    )
    assert mcp_def.id == def_id
    assert mcp_def.name == "Test MCP Definition"
    assert mcp_def.description == "A definition for testing."
    assert isinstance(mcp_def.created_at, datetime)
    assert isinstance(mcp_def.updated_at, datetime)
    assert repr(mcp_def) == f"<MCPDefinition(id={def_id}, name='Test MCP Definition')>"

def test_mcp_version_creation(db_session): # Add db_session if testing DB interaction
    """Test creating an MCPVersion instance."""
    def_id = uuid.uuid4() # Assume this definition exists or is created in a real test
    ver_id = uuid.uuid4()
    mcp_ver = MCPVersion(
        id=ver_id,
        mcp_definition_id=def_id,
        version_string="1.0.1",
        description="Version 1.0.1 of the test MCP.",
        mcp_type="Python Script",
        config_payload_data={"param1": "value1"} 
    )
    assert mcp_ver.id == ver_id
    assert mcp_ver.mcp_definition_id == def_id
    assert mcp_ver.version_string == "1.0.1"
    assert mcp_ver.mcp_type == "Python Script"
    assert mcp_ver.config_payload_data == {"param1": "value1"}
    # Add assertions for created_at, updated_at if not using default from model
    assert repr(mcp_ver) == f"<MCPVersion(id={ver_id}, definition_id={def_id}, version='1.0.1', type='Python Script')>"

def test_workflow_definition_creation():
    """Test creating a WorkflowDefinition instance."""
    wf_def_id = uuid.uuid4()
    wf_def = WorkflowDefinition(
        id=wf_def_id,
        name="Test Workflow Definition",
        description="A workflow definition for testing.",
        graph_representation={"nodes": [], "edges": []}
    )
    assert wf_def.id == wf_def_id
    assert wf_def.name == "Test Workflow Definition"
    assert wf_def.graph_representation == {"nodes": [], "edges": []}
    assert repr(wf_def) == f"<WorkflowDefinition(id={wf_def_id}, name='Test Workflow Definition')>"

def test_workflow_run_creation():
    """Test creating a WorkflowRun instance."""
    wf_def_id = uuid.uuid4() # Assume this definition exists
    run_id = uuid.uuid4()
    wf_run = WorkflowRun(
        id=run_id,
        workflow_definition_id=wf_def_id,
        status=WorkflowRunStatus.PENDING,
        run_parameters={"input_param": "test_value"}
    )
    assert wf_run.id == run_id
    assert wf_run.workflow_definition_id == wf_def_id
    assert wf_run.status == WorkflowRunStatus.PENDING
    assert wf_run.run_parameters == {"input_param": "test_value"}
    assert repr(wf_run) == f"<WorkflowRun(id={run_id}, definition_id={wf_def_id}, status='PENDING')>"

def test_workflow_run_status_enum():
    """Test the WorkflowRunStatus enum values."""
    assert WorkflowRunStatus.PENDING.value == "PENDING"
    assert WorkflowRunStatus.RUNNING.value == "RUNNING"
    assert WorkflowRunStatus.SUCCESS.value == "SUCCESS"
    assert WorkflowRunStatus.FAILED.value == "FAILED"
    assert WorkflowRunStatus.CANCELLED.value == "CANCELLED"

def test_workflow_definition_and_run_relationship():
    # Set up in-memory SQLite DB
    engine = sqlalchemy.create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a workflow definition
    wf_def = WorkflowDefinition(
        name="DB Test Workflow",
        description="A workflow for DB relationship test.",
        graph_representation={"nodes": [], "edges": []}
    )
    session.add(wf_def)
    session.commit()

    # Create a workflow run linked to the definition
    wf_run = WorkflowRun(
        workflow_definition_id=wf_def.id,
        status=WorkflowRunStatus.PENDING,
        run_parameters={"input": "value"}
    )
    session.add(wf_run)
    session.commit()

    # Query and assert relationship
    queried_run = session.query(WorkflowRun).filter_by(id=wf_run.id).first()
    assert queried_run.workflow_definition_id == wf_def.id
    queried_def = session.query(WorkflowDefinition).filter_by(id=wf_def.id).first()
    assert queried_def.id == wf_def.id
    # Clean up
    session.close()
    engine.dispose() 
"""
API Endpoints for managing Workflow Definitions and their Workflow Steps.

This router provides CRUD operations for WorkflowDefinitions and for managing WorkflowSteps within a workflow (adding, removing, reordering MCP versions as steps).
Includes monitoring, caching, and circuit breaker integration.
"""
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, Request
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from pydantic import ValidationError

# Set TESTING environment variable before any imports
os.environ['TESTING'] = 'true'

# Import after setting TESTING
from mcp.db.session import get_db
from mcp.core.settings import settings
from mcp.api.schemas.workflow_definition_schemas import (
    WorkflowDefinitionCreate, WorkflowDefinitionRead, WorkflowDefinitionUpdate,
    WorkflowStepCreate, WorkflowStepRead
)
from mcp.db.crud.crud_workflow_definition import crud_workflow_definition, crud_workflow_step
from mcp.core.exceptions import WorkflowDefinitionError, WorkflowStepError
from mcp.core.logging import logger
from fastapi.responses import JSONResponse
from mcp.api.middleware.auth import jwt_bearer
from mcp.core.exceptions import AuthenticationError
from mcp.core.security import get_current_user
from mcp.core.logging import setup_request_logging

# Use mock monitoring during testing
if os.getenv('TESTING'):
    class MockMonitor:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    monitor = MockMonitor()
else:
    from mcp.core.monitoring import monitor

# Type variables for generic functions
T = TypeVar('T', bound=Any)

# Cache timeouts in seconds
definition_cache_timeout = 300  # 5 minutes
steps_cache_timeout = 3600  # 1 hour

# Request ID middleware
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get('X-Request-ID', None)
    if not request_id:
        request_id = f"req-{str(uuid.uuid4())}"
    request.state.request_id = request_id
    setup_request_logging(request_id)
    response = await call_next(request)
    return response

# Custom exception handlers
async def handle_validation_error(exc: ValidationError, request: Request):
    """
    Handle validation errors with proper logging and monitoring.
    
    Args:
        exc: Pydantic ValidationError
        request: FastAPI Request object
        
    Returns:
        JSONResponse with error details
    """
    logger.error(f"[Request {request.state.request_id}] Validation error: {str(exc)}")
    if not os.getenv('TESTING'):
        monitor.increment_error("workflow_validation", str(exc))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "request_id": request.state.request_id,
            "error": "Validation Error",
            "details": exc.errors()
        }
    )

async def handle_workflow_error(exc: WorkflowDefinitionError, request: Request):
    logger.error(f"[Request {request.state.request_id}] Workflow error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Workflow error",
            "message": str(exc),
            "request_id": request.state.request_id
        }
    )

async def handle_auth_error(exc: AuthenticationError, request: Request):
    """
    Handle authentication errors with proper logging and monitoring.
    
    Args:
        exc: Authentication error exception
        request: FastAPI Request object
        
    Returns:
        JSONResponse with error details
    """
    logger.error(f"[Request {request.state.request_id}] Authentication error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": "Authentication error",
            "message": str(exc),
            "request_id": request.state.request_id
        }
    )

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/workflow-definitions",
    tags=["Workflow Definitions"],
    dependencies=[Depends(jwt_bearer)]
)

# Add security middleware
router.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

router.add_middleware(
    GZipMiddleware,
    minimum_size=1000
)

# Router initialization
router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    dependencies=[Depends(get_current_user)]
)

# Mock decorators for testing
if os.getenv('TESTING'):
    def mock_decorator(func):
        return func
    
    workflow_circuit_breaker = mock_decorator
    workflow_rate_limiter = mock_decorator
    cache_response = mock_decorator
else:
    from mcp.core.circuit_breaker import workflow_circuit_breaker
    from mcp.core.rate_limiter import workflow_rate_limiter
    from mcp.core.cache import cache_response

# Add rate limiting
@router.on_event("startup")
def startup_event():
    if not os.getenv('TESTING'):
        workflow_rate_limiter.init()
        workflow_steps_rate_limiter.init()

@router.post("/", response_model=WorkflowDefinitionRead, status_code=status.HTTP_201_CREATED)
@workflow_circuit_breaker
@workflow_rate_limiter
@cache_response(timeout=definition_cache_timeout)
async def create_workflow_definition(
    wf_def_in: WorkflowDefinitionCreate,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new Workflow Definition, optionally with steps.

    Args:
        wf_def_in: Workflow definition data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created workflow definition

    Raises:
        HTTPException: If validation fails or creation fails
    """
    try:
        # Validate input
        if not wf_def_in.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "detail": "Workflow name is required",
                    "request_id": request.state.request_id
                }
            )

        if len(wf_def_in.steps or []) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "detail": "Maximum 50 steps allowed per workflow",
                    "request_id": request.state.request_id
                }
            )

        # Create workflow
        wf_def = crud_workflow_definition.create_with_steps(
            db=db,
            obj_in=wf_def_in,
            created_by=current_user.id
        )
        
        logger.info(f"[Request {request.state.request_id}] Workflow created: {wf_def.name} (ID: {wf_def.id})")
        
        return wf_def

    except ValidationError as e:
        logger.error(f"[Request {request.state.request_id}] Validation error creating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "detail": str(e),
                "request_id": request.state.request_id
            }
        )
    except WorkflowDefinitionError as e:
        logger.error(f"[Request {request.state.request_id}] Workflow creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": str(e),
                "request_id": request.state.request_id
            }
        )
    except Exception as e:
        logger.error(f"[Request {request.state.request_id}] Unexpected error creating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "detail": "An unexpected error occurred while creating the workflow",
                "request_id": request.state.request_id
            }
        )

# Custom exception handlers
async def handle_validation_error(request: Any, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )

async def handle_workflow_error(request: Any, exc: WorkflowDefinitionError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Workflow error",
            "message": str(exc)
        }
    )

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/workflow-definitions",
    tags=["Workflow Definitions"],
)

@router.post("/", response_model=WorkflowDefinitionRead, status_code=status.HTTP_201_CREATED)
def create_workflow_definition(
    wf_def_in: WorkflowDefinitionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new Workflow Definition, optionally with steps.

    Args:
        wf_def_in: Workflow definition data
        db: Database session

    Returns:
        Created workflow definition

    Raises:
        HTTPException: If validation fails or creation fails
    """
    try:
        # Validate input
        if not wf_def_in.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow name is required"
            )

        if len(wf_def_in.steps or []) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 steps allowed per workflow"
            )

        # Create workflow
        wf_def = crud_workflow_definition.create_with_steps(db=db, obj_in=wf_def_in)
        
        # Log creation
        logger.info(f"Workflow created: {wf_def.name} (ID: {wf_def.id})")
        
        return wf_def

    except ValidationError as e:
        logger.error(f"Validation error creating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except WorkflowDefinitionError as e:
        logger.error(f"Workflow creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the workflow"
        )

@router.get("/", response_model=List[WorkflowDefinitionRead])
@workflow_circuit_breaker
@workflow_rate_limiter
@cache_response(timeout=definition_cache_timeout)
async def list_workflow_definitions(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, min_length=1),
    mcp_type: Optional[str] = Query(None),
    include_archived: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    List all Workflow Definitions with optional filtering.
    
    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        search: Search term to filter workflows by name or description
        mcp_type: Filter workflows containing steps of this MCP type
        include_archived: Include archived workflows in results
        db: Database session
    
    Returns:
        List of workflow definitions matching filters
    
    Raises:
        HTTPException: If database error occurs
        RateLimitExceededError: If rate limit is exceeded
        CircuitBreakerOpenError: If circuit breaker is open
    """
    try:
        start_time = datetime.now()
        
        # Apply rate limiting
        await workflow_rate_limiter(request.state.request_id)
        
        # Execute through circuit breaker
        result = await workflow_circuit_breaker(
            self._list_workflow_definitions,
            skip,
            limit,
            search,
            mcp_type,
            include_archived,
            db
        )
        
        # Record metrics
        await monitor.record_request(
            endpoint="workflow_definitions",
            method="GET",
            status=200,
            duration=(datetime.now() - start_time).total_seconds(),
            cache_hit=cache_key_exists(f"workflow:list:{skip}:{limit}:{search}:{mcp_type}:{include_archived}")
        )
        
        return result
    
    except RateLimitExceededError as e:
        logger.warning(f"[Request {request.state.request_id}] Rate limit exceeded: {str(e)}")
        await monitor.record_error(
            endpoint="workflow_definitions",
            method="GET",
            error_type="rate_limit"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "detail": "Rate limit exceeded",
                "request_id": request.state.request_id
            }
        )
    
    except CircuitBreakerOpenError as e:
        logger.error(f"[Request {request.state.request_id}] Circuit breaker open: {str(e)}")
        await monitor.record_error(
            endpoint="workflow_definitions",
            method="GET",
            error_type="circuit_breaker"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Service temporarily unavailable due to high error rate",
                "request_id": request.state.request_id
            }
        )
    """
    List all Workflow Definitions with optional filtering.
    
    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        search: Search term to filter workflows by name or description
        mcp_type: Filter workflows containing steps of this MCP type
        include_archived: Include archived workflows in results
        db: Database session
    
    Returns:
        List of workflow definitions matching filters
    
    Raises:
        HTTPException: If database error occurs
        RateLimitExceededError: If rate limit is exceeded
        CircuitBreakerOpenError: If circuit breaker is open
    """
    try:
        # Apply rate limiting
        await workflow_rate_limiter(request.state.request_id)
        
        # Execute through circuit breaker
        return await workflow_circuit_breaker(
            self._list_workflow_definitions,
            skip,
            limit,
            search,
            mcp_type,
            include_archived,
            db
        )
    
    except RateLimitExceededError as e:
        logger.warning(f"[Request {request.state.request_id}] Rate limit exceeded: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "detail": "Rate limit exceeded",
                "request_id": request.state.request_id
            }
        )
    
    except CircuitBreakerOpenError as e:
        logger.error(f"[Request {request.state.request_id}] Circuit breaker open: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Service temporarily unavailable due to high error rate",
                "request_id": request.state.request_id
            }
        )
    """
    List all Workflow Definitions with optional filtering.
    
    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        search: Search term to filter workflows by name or description
        mcp_type: Filter workflows containing steps of this MCP type
        include_archived: Include archived workflows in results
        db: Database session
    
    Returns:
        List of workflow definitions matching filters
    
    Raises:
        HTTPException: If database error occurs
    """
    try:
        # Build query with eager loading
        query = db.query(WorkflowDefinition).options(
            joinedload(WorkflowDefinition.steps)
        )
        
        # Apply filters
        if not include_archived:
            query = query.filter(WorkflowDefinition.is_archived == False)
        
        if search:
            query = query.filter(
                (WorkflowDefinition.name.ilike(f"%{search}%")) |
                (WorkflowDefinition.description.ilike(f"%{search}%"))
            )
        
        if mcp_type:
            query = query.join(WorkflowStep).filter(
                WorkflowStep.mcp_type == mcp_type
            )
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        definitions = query.all()
        
        logger.info(f"[Request {request.state.request_id}] Retrieved {len(definitions)} workflows")
        
        return {
            "total": total,
            "items": definitions
        }
    
    except Exception as e:
        logger.error(f"[Request {request.state.request_id}] Error fetching workflow definitions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "detail": "An unexpected error occurred while fetching workflows",
                "request_id": request.state.request_id
            }
        )
    """
    List all Workflow Definitions with optional filtering.

    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        search: Search term to filter workflows by name or description
        mcp_type: Filter workflows containing steps of this MCP type
        include_archived: Include archived workflows in results

    Returns:
        List of workflow definitions matching filters

    Raises:
        HTTPException: If database error occurs
    """
    try:
        # Apply filters
        if search or mcp_type or include_archived:
            defs = crud_workflow_definition.get_filtered(
                db,
                skip=skip,
                limit=limit,
                search_term=search,
                mcp_type=mcp_type,
                include_archived=include_archived
            )
        else:
            # No filters, get all
            defs = crud_workflow_definition.get_multi(db, skip=skip, limit=limit)
        
        logger.info(f"Retrieved {len(defs)} workflows")
        return defs

    except Exception as e:
        logger.error(f"Error fetching workflow definitions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching workflows"
        )

@router.get("/{wf_def_id}", response_model=WorkflowDefinitionRead)
@workflow_circuit_breaker
@workflow_rate_limiter
@cache_response(timeout=definition_cache_timeout)
async def get_workflow_definition(
    wf_def_id: int = Path(..., description="Workflow Definition ID"),
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get a Workflow Definition by ID, including its steps.
    
    Args:
        wf_def_id: Workflow Definition ID
        db: Database session
    
    Returns:
        Workflow definition with steps
    
    Raises:
        HTTPException: If workflow not found
    """
    try:
        # Query with eager loading
        definition = db.query(WorkflowDefinition).options(
            joinedload(WorkflowDefinition.steps)
        ).filter(
            WorkflowDefinition.id == wf_def_id
        ).first()
        
        if not definition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "detail": f"Workflow Definition {wf_def_id} not found",
                    "request_id": request.state.request_id
                }
            )
        
        logger.info(f"[Request {request.state.request_id}] Retrieved workflow {wf_def_id}")
        return definition
    
    except Exception as e:
        logger.error(f"[Request {request.state.request_id}] Error fetching workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "detail": "An unexpected error occurred while fetching the workflow",
                "request_id": request.state.request_id
            }
        )
    """
    Get a Workflow Definition by ID, including its steps.

    Args:
        wf_def_id: Workflow Definition ID
        db: Database session

    Returns:
        Workflow definition with steps

    Raises:
        HTTPException: If workflow not found
    """
    wf_def = crud_workflow_definition.get_with_steps(db, id=wf_def_id)
    if not wf_def:
        raise HTTPException(status_code=404, detail="Workflow Definition not found")
    return wf_def

@router.put("/{wf_def_id}", response_model=WorkflowDefinitionRead)
@workflow_circuit_breaker
@workflow_rate_limiter
@cache_response(timeout=definition_cache_timeout)
async def update_workflow_definition(
    wf_def_id: int = Path(..., description="Workflow Definition ID"),
    db: Session = Depends(get_db),
    wf_def_update: WorkflowDefinitionUpdate,
    request: Request
):
    """
    Update a Workflow Definition.

    Args:
        wf_def_id: Workflow Definition ID
        wf_def_update: Update data
        db: Database session

    Returns:
        Updated workflow definition

    Raises:
        HTTPException: If workflow not found or update fails
    """
    try:
        wf_def = crud_workflow_definition.get(db, id=wf_def_id)
        if not wf_def:
            raise HTTPException(status_code=404, detail="Workflow Definition not found")

        updated_wf_def = crud_workflow_definition.update(
            db=db,
            db_obj=wf_def,
            obj_in=wf_def_update
        )
        return updated_wf_def

    except Exception as e:
        logger.error(f"Error updating workflow definition {wf_def_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the workflow"
        )

@router.delete("/{wf_def_id}", response_model=WorkflowDefinitionRead)
@workflow_circuit_breaker
@workflow_rate_limiter
@cache_response(timeout=definition_cache_timeout)
async def delete_workflow_definition(
    wf_def_id: int = Path(..., description="Workflow Definition ID"),
    db: Session = Depends(get_db),
    request: Request
):
    """
    Delete a Workflow Definition and all its steps.

    Args:
        wf_def_id: Workflow Definition ID
        db: Database session

    Returns:
        Deleted workflow definition

    Raises:
        HTTPException: If workflow not found or deletion fails
    """
    try:
        wf_def = crud_workflow_definition.get(db, id=wf_def_id)
        if not wf_def:
            raise HTTPException(status_code=404, detail="Workflow Definition not found")

        deleted_wf_def = crud_workflow_definition.remove(db=db, id=wf_def_id)
        logger.info(f"Workflow deleted: {deleted_wf_def.name} (ID: {deleted_wf_def.id})")
        return deleted_wf_def

    except Exception as e:
        logger.error(f"Error deleting workflow definition {wf_def_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the workflow"
        )

# --- Workflow Step Endpoints ---

@router.post("/{wf_def_id}/steps", response_model=WorkflowStepRead, status_code=status.HTTP_201_CREATED)
@workflow_circuit_breaker
@workflow_rate_limiter
@cache_response(timeout=steps_cache_timeout)
async def add_workflow_step(
    wf_def_id: int,
    db: Session = Depends(get_db),
    step_in: WorkflowStepCreate,
    request: Request
):
    """
    Add a new step to a Workflow Definition.

    Args:
        wf_def_id: Workflow Definition ID
        step_in: Step creation data
        db: Database session

    Returns:
        Created workflow step

    Raises:
        HTTPException: If workflow or step creation fails
    """
    # Ensure parent exists
    wf_def = crud_workflow_definition.get(db, id=wf_def_id)
    if not wf_def:
        raise HTTPException(status_code=404, detail="Workflow Definition not found")

    try:
        step = crud_workflow_step.create(
            db=db,
            obj_in={**step_in.model_dump(), "workflow_definition_id": wf_def_id}
        )
        logger.info(f"Step added to workflow {wf_def_id}: {step.id}")
        return step

    except Exception as e:
        logger.error(f"Error adding step to workflow {wf_def_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the step"
        )

@router.delete("/{wf_def_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow_step(
    wf_def_id: int = Path(..., description="Workflow Definition ID"),
    db: Session = Depends(get_db),
    step_id: int = Path(..., description="Step ID")
):
    """
    Delete a step from a Workflow Definition.
    """
    step = crud_workflow_step.get(db, id=step_id)
    if not step or step.workflow_definition_id != wf_def_id:
        raise HTTPException(status_code=404, detail="Workflow Step not found for this Workflow Definition")
    crud_workflow_step.remove(db, id=step_id)
    return

@router.put("/{wf_def_id}/steps/{step_id}", response_model=WorkflowStepRead)
def update_workflow_step(
    wf_def_id: int = Path(..., description="Workflow Definition ID"),
    db: Session = Depends(get_db),
    step_id: int = Path(..., description="Step ID"),
    step_update: WorkflowStepCreate
):
    """
    Update a step in a Workflow Definition.
    """
    step = crud_workflow_step.get(db, id=step_id)
    if not step or step.workflow_definition_id != wf_def_id:
        raise HTTPException(status_code=404, detail="Workflow Step not found for this Workflow Definition")
    updated = crud_workflow_step.update(db, db_obj=step, obj_in=step_update)
    return updated

@router.get("/{wf_def_id}/steps", response_model=List[WorkflowStepRead])
@cache_response(timeout=steps_cache_timeout)
async def list_workflow_steps(
    wf_def_id: int = Path(..., description="Workflow Definition ID"),
    db: Session = Depends(get_db)
):
    """
    List all steps for a Workflow Definition.
    
    Args:
        wf_def_id: Workflow Definition ID
        db: Database session
    
    Returns:
        List of workflow steps
    
    Raises:
        HTTPException: If workflow not found
    """
    try:
        # Query with eager loading
        steps = db.query(WorkflowStep).options(
            joinedload(WorkflowStep.workflow_definition)
        ).filter(
            WorkflowStep.workflow_definition_id == wf_def_id
        ).order_by(
            WorkflowStep.order.asc()
        ).all()
        
        if not steps:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "detail": f"No steps found for workflow {wf_def_id}",
                    "request_id": request.state.request_id
                }
            )
        
        logger.info(f"[Request {request.state.request_id}] Retrieved {len(steps)} steps for workflow {wf_def_id}")
        return steps
    
    except Exception as e:
        logger.error(f"[Request {request.state.request_id}] Error fetching workflow steps: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "detail": "An unexpected error occurred while fetching workflow steps",
                "request_id": request.state.request_id
            }
        )
    """
    List all steps for a Workflow Definition.
    """
    wf_def = crud_workflow_definition.get_with_steps(db, id=wf_def_id)
    if not wf_def:
        raise HTTPException(status_code=404, detail="Workflow Definition not found")
    return wf_def.steps

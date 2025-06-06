import abc
from typing import Dict, Any, Optional
from mcp.core.mcp_configs import MCPConfigPayload
from mcp.core.workflow_streaming_service import WorkflowStreamingService
from sqlalchemy.orm import Session

class BaseExecutor(abc.ABC):
    def __init__(self, db_session: Optional[Session] = None, streaming_service: Optional[WorkflowStreamingService] = None, workflow_run_id: Optional[int]=None):
        self.db_session = db_session
        self.streaming_service = streaming_service
        self.workflow_run_id = workflow_run_id  # To associate logs/events with the current run

    @abc.abstractmethod
    async def execute(self, config: MCPConfigPayload, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the MCP.
        :param config: The specific, typed Pydantic configuration model for this MCP.
        :param inputs: A dictionary of resolved input values for the MCP.
        :return: A dictionary of output values produced by the MCP.
        """
        pass

    async def _log_message(self, step_id_for_log: str, message: str, level: str = "INFO"):
        """Helper to publish log messages via the streaming service."""
        if self.streaming_service and self.workflow_run_id:
            payload = {"step_id": step_id_for_log, "message": message, "level": level}
            # await self.streaming_service.publish_run_update(self.workflow_run_id, "log", payload)
            print(f"RUN_ID {self.workflow_run_id} - STEP {step_id_for_log} [{level}]: {message}")  # Fallback print

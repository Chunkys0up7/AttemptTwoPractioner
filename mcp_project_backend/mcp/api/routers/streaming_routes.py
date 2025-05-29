"""
API Endpoints for streaming real-time updates, e.g., for workflow monitoring.
"""
import asyncio
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import EventSourceResponse
# Alternative if needed, but FastAPI's is fine
# from sse_starlette.sse import EventSourceResponse as SSEEventSourceResponse # Unused

from mcp.api.main import redis_pubsub_manager  # Import the global instance
from mcp.core.config import settings
# In a larger app, you might have a dependency injection system for services like RedisPubSubManager
# For now, importing the global instance from main.py is straightforward if it's initialized there.

router = APIRouter(
    # Consistent prefix with API_V1_STR
    prefix=f"{settings.API_V1_STR}/streaming",
    tags=["Streaming"],
)


@router.get("/workflow-runs/{run_id}/stream")
async def stream_workflow_run_updates(run_id: str, request: Request):
    """
    Streams real-time updates for a specific workflow run using Server-Sent Events (SSE).

    Clients can connect to this endpoint to receive live updates such as:
    - Log messages
    - Step status changes
    - Partial results or previews
    - Final run status and results

    Events are published by the WorkflowEngineService to a Redis Pub/Sub channel
    specific to the `run_id` (e.g., `workflow_run_events:{run_id}`).
    """
    if not settings.REDIS_URL:
        # If Redis is not configured, SSE streaming cannot work.
        # Option 1: Return an error immediately.
        raise HTTPException(
            status_code=503,
            detail="Real-time streaming is disabled as Redis is not configured."
        )
        # Option 2: Return an EventSourceResponse that immediately closes or sends a single error event.
        # async def error_event_generator():
        #     yield {"event": "error", "data": json.dumps({"message": "Streaming unavailable"})}
        # return EventSourceResponse(error_event_generator(), media_type="text/event-stream")

    async def event_generator():
        try:
            # The subscribe_to_channel method in RedisPubSubManager should handle
            # creating a new Redis connection for this subscription.
            async for event_data in redis_pubsub_manager.subscribe_to_channel(f"workflow_run_events:{run_id}"):
                if await request.is_disconnected():
                    print(
                        f"SSE stream: Client for run '{run_id}' disconnected. Closing stream.")
                    break  # Exit the generator loop

                # SSE format:
                # event: <event_type> (optional, defaults to 'message')
                # data: <json_string_payload>
                # id: <unique_event_id> (optional)
                # retry: <milliseconds> (optional)
                # \n\n (double newline to end event)

                event_type = event_data.get("event_type", "message")
                payload = event_data.get("payload", {})

                yield {
                    "event": event_type,
                    "data": json.dumps(payload)  # Data must be a string
                    # "id": str(uuid.uuid4()) # Optional: if you need unique event IDs
                }
                # print(f"SSE stream: Sent event '{event_type}' for run '{run_id}'") # For debugging

        except asyncio.CancelledError:
            # This occurs if the client disconnects and the request is cancelled by FastAPI/Uvicorn
            print(
                f"SSE stream: Task for run '{run_id}' was cancelled (client likely disconnected).")
        except ConnectionError as e:
            # Handle Redis connection errors during subscription
            print(
                f"SSE stream: Redis connection error for run '{run_id}': {e}")
            yield {
                "event": "error",
                "data": json.dumps({"message": "Streaming service connection error.", "detail": str(e)})
            }
        except Exception as e:
            # Catch any other unexpected errors during event generation
            print(f"SSE stream: Unexpected error for run '{run_id}': {e}")
            yield {
                "event": "error",
                "data": json.dumps({"message": "An unexpected error occurred during streaming.", "detail": str(e)})
            }
        finally:
            # Cleanup logic here is mostly handled by RedisPubSubManager's subscribe_to_channel method
            # (closing its specific Redis connection for the subscription).
            print(f"SSE stream: Event generator for run '{run_id}' finished.")

    return EventSourceResponse(event_generator(), media_type="text/event-stream")

# Example of how other modules would publish events (e.g., WorkflowEngineService):
# from mcp.api.main import redis_pubsub_manager
# async def some_workflow_step_execution(run_id: str, step_id: str):
#     # ... do work ...
#     log_message = f"Step {step_id} started."
#     await redis_pubsub_manager.publish(
#         channel=f"workflow_run_events:{run_id}",
#         message={"event_type": "log", "payload": {"step_id": step_id, "message": log_message}}
#     )
#     # ... more work ...
#     await redis_pubsub_manager.publish(
#         channel=f"workflow_run_events:{run_id}",
#         message={"event_type": "status_change", "payload": {"step_id": step_id, "status": "completed"}}
#     )

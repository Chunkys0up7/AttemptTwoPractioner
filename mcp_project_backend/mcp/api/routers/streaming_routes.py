"""
API Router for Server-Sent Events (SSE) for real-time updates.

This router provides endpoints for clients to subscribe to real-time event streams.
Currently, it includes an endpoint for monitoring workflow run progress.

Workflow Run Streaming:
- Endpoint: `/workflow-runs/{run_id}/stream`
- Method: GET
- Produces: `text/event-stream`
- Functionality: Subscribes to a Redis Pub/Sub channel specific to the `run_id`
  (e.g., `workflow_run_events:{run_id}`). Events published to this channel by the
  Workflow Engine (e.g., log messages, status changes, result previews) are
  formatted as SSE and sent to the client.
- Handles client disconnects gracefully by stopping the event stream for that client.
"""
import asyncio
import json
import os
from fastapi import APIRouter, Request, HTTPException, Path, Depends
try:
    from sse_starlette.sse import EventSourceResponse
except ImportError:
    if os.getenv('TESTING'):
        # Mock EventSourceResponse for tests
        class EventSourceResponse:
            def __init__(self, generator):
                self.generator = generator
            async def __call__(self, scope, receive, send):
                async for item in self.generator:
                    await send({"type": "http.response.body", "body": item})
    else:
        raise
from typing import AsyncGenerator

from mcp.core.pubsub.redis_pubsub_manager import redis_pubsub_manager
from mcp.core.settings import settings
from mcp.core.pubsub.redis_pubsub import RedisPubSubManager

router = APIRouter()

async def get_redis_pubsub_manager():
    # This dependency injector allows for easier mocking in tests if needed
    # and ensures the manager is available.
    if not redis_pubsub_manager or not redis_pubsub_manager._publisher_client:
        # This check is a bit of a safeguard; normally lifespan should handle connection.
        # If running tests where lifespan isn't fully executed, this might be an issue.
        # For production, REDIS_URL check in main.py lifespan is more critical.
        if settings.REDIS_URL:
            try:
                await redis_pubsub_manager.connect_publisher() # Ensure publisher is connected
            except ConnectionError as e:
                raise HTTPException(status_code=503, detail=f"Redis connection not available: {e}")
        else:
            raise HTTPException(status_code=503, detail="Redis not configured, streaming is unavailable.")
    return redis_pubsub_manager


async def workflow_event_generator(run_id: str, request: Request, pubsub_manager: RedisPubSubManager) -> AsyncGenerator[str, None]:
    """
    Subscribes to Redis for a specific workflow run and yields events as SSE.
    Handles client disconnects gracefully.
    """
    channel_name = f"workflow_run_events:{run_id}"
    try:
        # Yield a connection confirmation event (optional)
        # yield json.dumps({"event": "connection_established", "data": {"run_id": run_id}})

        async for message in pubsub_manager.subscribe_to_channel(channel_name):
            if await request.is_disconnected():
                print(f"SSE Client for run_id {run_id} disconnected.")
                break # Exit the generator if client disconnects

            # Format as SSE event:
            # event: <event_type from message>
            # data: <payload from message>
            # id: <optional_event_id>
            event_type = message.get("event_type", "message") # Default to "message" if no specific type
            payload = message.get("payload", {})

            sse_event = f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"
            yield sse_event
            await asyncio.sleep(0.01) # Small sleep to allow other tasks to run

    except asyncio.CancelledError:
        print(f"SSE subscription for run_id {run_id} cancelled (client likely disconnected).")
        # This is an expected way for the stream to end when the client disconnects
    except Exception as e:
        print(f"Error in SSE event generator for run_id {run_id} on channel {channel_name}: {e}")
        # Optionally, yield an error event to the client if the connection is still alive
        # error_event = {"event": "error", "data": {"detail": str(e)}}
        # yield f"event: error\ndata: {json.dumps(error_event)}\n\n"
    finally:
        print(f"Stopped SSE event generator for run_id {run_id} on channel {channel_name}.")
        # Unsubscription and client closing is handled within subscribe_to_channel

@router.get(
    "/workflow-runs/{run_id}/stream",
    summary="Stream Workflow Run Events (SSE)",
    response_description="A stream of Server-Sent Events for a specific workflow run.",
    tags=["Streaming", "Workflow Execution"],
)
async def stream_workflow_run_events(
    request: Request,
    run_id: str = Path(..., title="Workflow Run ID", description="The ID of the workflow run to stream events for."),
    pubsub_manager: RedisPubSubManager = Depends(get_redis_pubsub_manager)
):
    """
    Provides a Server-Sent Events (SSE) stream for real-time updates on a specific workflow run.

    Events are published by the Workflow Engine to a Redis channel associated with the `run_id`.
    This endpoint subscribes to that channel and forwards messages to the connected client.

    Possible event types (sent in the `event:` field of SSE):
    - `status_change`: Indicates a change in the overall workflow run status or a step's status.
    - `log`: Provides a log message related to the workflow run.
    - `result_preview`: Provides a preview of intermediate or final results.
    - `error`: Indicates an error occurred during the stream or workflow processing.
    - `message`: Generic message type if `event_type` is not specified in the Redis message.

    The `data:` field of SSE will contain a JSON payload specific to the event type.
    """
    # Validate run_id format if necessary (e.g., if it should be a UUID)
    # For now, assume it's a string.

    # Check if the workflow run_id exists in the database (optional, but good practice)
    # This might involve a quick DB lookup. If not found, return 404.
    # e.g., if not await some_service.get_workflow_run(run_id):
    #     raise HTTPException(status_code=404, detail=f"Workflow run with ID '{run_id}' not found.")

    event_gen = workflow_event_generator(run_id, request, pubsub_manager)
    return EventSourceResponse(event_gen)

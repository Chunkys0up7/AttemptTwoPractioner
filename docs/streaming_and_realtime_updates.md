# Streaming & Real-time Updates

This document describes the real-time streaming and Server-Sent Events (SSE) system in the MCP backend, which enables live workflow monitoring and UI updates.

## Overview

The backend uses FastAPI SSE endpoints and Redis pubsub to provide real-time updates for workflow runs and other events. This allows the frontend to receive live status, logs, and results without polling.

## Architecture

- **RedisPubSubManager**: Manages pub/sub channels for publishing and subscribing to events.
- **SSE Endpoints**: FastAPI endpoints stream events to clients using `EventSourceResponse`.
- **Workflow Engine**: Publishes events (status, logs, results) to Redis channels.
- **Frontend**: Connects to SSE endpoints using the browser's `EventSource` API.

## Key Components

### RedisPubSubManager

```python
class RedisPubSubManager:
    def __init__(self, redis_url: str): ...
    async def publish(self, channel: str, message: dict): ...
    async def subscribe_to_channel(self, channel: str): ...
```

### SSE Endpoint Example

```python
@router.get("/workflow-runs/{run_id}/stream")
async def stream_workflow_run_updates(run_id: str, request: Request):
    async def event_generator():
        async for event_data in pubsub_manager.subscribe_to_channel(f"workflow_run_events:{run_id}"):
            if await request.is_disconnected():
                break
            yield f"event: {event_data.get('event_type', 'message')}\ndata: {json.dumps(event_data.get('payload', {}))}\n\n"
    return EventSourceResponse(event_generator(), media_type="text/event-stream")
```

### Event Types

- `status_change`: Workflow status updates
- `log`: Log messages
- `result_preview`: Partial results

## Frontend Integration

- The frontend uses the `EventSource` API to connect to `/api/v1/workflow-runs/{run_id}/stream`.
- UI components (e.g., `RunDetailView`) update in real time as events are received.

## Usage Example (Frontend)

```javascript
const eventSource = new EventSource(`/api/v1/workflow-runs/${runId}/stream`);
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Update UI with new data
};
eventSource.addEventListener('status_change', (event) => { ... });
eventSource.addEventListener('log', (event) => { ... });
```

## Security & Scalability

- SSE endpoints are protected by authentication.
- Redis pubsub decouples event producers and consumers for scalability.

## See Also

- `streaming_routes.py` for endpoint code
- `RedisPubSubManager` in `core/pubsub/`
- Frontend `ExecutionMonitorPage.tsx` for UI integration

import asyncio
import json
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from sse_starlette.sse import EventSourceResponse

from mcp.api.routers.streaming_routes import router as streaming_router
from mcp.core.pubsub.redis_pubsub import RedisPubSubManager
from mcp.api.main import lifespan # To ensure lifespan events like Redis connection mock if needed

# Minimal app setup for testing the router
@pytest_asyncio.fixture
async def test_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(streaming_router, prefix="/api/v1") # Match main.py prefix
    return app

@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
def mock_redis_pubsub_manager() -> AsyncMock:
    mock_manager = AsyncMock(spec=RedisPubSubManager)
    mock_manager._publisher_client = AsyncMock() # Simulate a connected publisher
    mock_manager._publisher_client.closed = False
    return mock_manager

# Override the dependency for the router
@pytest_asyncio.fixture(autouse=True)
async def override_redis_dependency(test_app: FastAPI, mock_redis_pubsub_manager: AsyncMock):
    from mcp.api.routers.streaming_routes import get_redis_pubsub_manager
    test_app.dependency_overrides[get_redis_pubsub_manager] = lambda: mock_redis_pubsub_manager
    yield
    test_app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_stream_workflow_run_events_success(client: AsyncClient, mock_redis_pubsub_manager: AsyncMock):
    run_id = "test_run_123"
    channel_name = f"workflow_run_events:{run_id}"

    # Simulate messages that the subscribe_to_channel would yield
    mock_messages = [
        {"event_type": "log", "payload": {"message": "Log 1"}},
        {"event_type": "status_change", "payload": {"status": "running"}},
    ]

    async def mock_subscribe_generator():
        for msg in mock_messages:
            yield msg
            await asyncio.sleep(0.01) # Simulate some delay
        # Keep the generator alive briefly to allow client to disconnect gracefully
        # Or simulate it ending naturally after all messages
        await asyncio.sleep(0.1)

    mock_redis_pubsub_manager.subscribe_to_channel.return_value = mock_subscribe_generator()

    response_events = []
    try:
        async with client.stream("GET", f"/api/v1/workflow-runs/{run_id}/stream") as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]

            buffer = ""
            async for line in response.aiter_lines():
                buffer += line + "\n"
                if buffer.endswith("\n\n"):
                    # We have a complete event
                    parts = buffer.strip().split("\n")
                    event_data = {}
                    for part in parts:
                        if part.startswith("event:"):
                            event_data["event"] = part.split("event: ", 1)[1]
                        elif part.startswith("data:"):
                            event_data["data"] = json.loads(part.split("data: ", 1)[1])
                    if event_data: # Ensure we parsed something
                        response_events.append(event_data)
                    buffer = ""
                    if len(response_events) == len(mock_messages):
                        break # Stop after receiving expected number of messages

    except asyncio.TimeoutError:
        pytest.fail("Stream timed out")
    except Exception as e:
        pytest.fail(f"Stream failed with exception: {e}")

    mock_redis_pubsub_manager.subscribe_to_channel.assert_called_once_with(channel_name)
    assert len(response_events) == len(mock_messages)
    for i, expected_msg_content in enumerate(mock_messages):
        assert response_events[i]["event"] == expected_msg_content["event_type"]
        assert response_events[i]["data"] == expected_msg_content["payload"]

@pytest.mark.asyncio
async def test_stream_workflow_run_client_disconnect(client: AsyncClient, mock_redis_pubsub_manager: AsyncMock):
    run_id = "disconnect_test_run"
    channel_name = f"workflow_run_events:{run_id}"

    # Simulate a long-running or infinite generator
    # Use an event to signal the generator to stop when the test is done
    stop_event = asyncio.Event()

    async def mock_infinite_subscribe_generator():
        try:
            count = 0
            while not stop_event.is_set():
                yield {"event_type": "ping", "payload": {"count": count}}
                count += 1
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            print(f"mock_infinite_subscribe_generator for {channel_name} cancelled")
            raise
        finally:
            print(f"mock_infinite_subscribe_generator for {channel_name} finished")

    mock_redis_pubsub_manager.subscribe_to_channel.return_value = mock_infinite_subscribe_generator()

    response_received = False
    try:
        async with client.stream("GET", f"/api/v1/workflow-runs/{run_id}/stream", timeout=1.0) as response:
            assert response.status_code == 200
            async for line in response.aiter_lines():
                # We expect the client to disconnect before reading many messages
                # so we just check if we get at least one line and then break
                response_received = True
                print(f"Client received: {line}")
                break # Simulate client disconnecting after first event part
    except asyncio.TimeoutError:
        # This can happen if the client doesn't disconnect quickly enough and the server keeps sending.
        # For this test, a timeout implies the disconnect wasn't handled as expected by the stream task.
        # However, httpx client might not raise error on early close from server side.
        print("Client stream processing timed out or completed.")
    except Exception as e:
        pytest.fail(f"Stream failed with exception: {e}")
    finally:
        stop_event.set() # Signal generator to stop

    # Give a moment for the server-side generator to process cancellation
    await asyncio.sleep(0.2)

    mock_redis_pubsub_manager.subscribe_to_channel.assert_called_once_with(channel_name)
    # Difficult to assert graceful shutdown from client side alone without more server introspection
    # The main check is that subscribe_to_channel was called and the test doesn't hang indefinitely.
    assert response_received, "Client did not receive any data before simulated disconnect."

@pytest.mark.asyncio
async def test_stream_redis_connection_error(test_app: FastAPI, client: AsyncClient):
    from mcp.api.routers.streaming_routes import get_redis_pubsub_manager
    run_id = "redis_error_run"

    # Create a new mock that will raise an error on connect_publisher or is misconfigured
    error_mock_manager = AsyncMock(spec=RedisPubSubManager)
    # Simulate publisher not connected and connection attempt fails
    error_mock_manager._publisher_client = None
    error_mock_manager.connect_publisher.side_effect = ConnectionError("Simulated Redis down")

    # Temporarily override with the error-throwing mock
    original_override = test_app.dependency_overrides.get(get_redis_pubsub_manager)
    test_app.dependency_overrides[get_redis_pubsub_manager] = lambda: error_mock_manager

    response = await client.get(f"/api/v1/workflow-runs/{run_id}/stream")
    assert response.status_code == 503
    assert "Redis connection not available" in response.text or "Redis not configured" in response.text

    # Restore original override
    if original_override:
        test_app.dependency_overrides[get_redis_pubsub_manager] = original_override
    else:
        del test_app.dependency_overrides[get_redis_pubsub_manager]

# TODO: Add test for when subscribe_to_channel itself raises an unhandled exception
# (not asyncio.CancelledError) 
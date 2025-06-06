import asyncio
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock
from contextlib import suppress

from mcp.core.pubsub.redis_pubsub import RedisPubSubManager
from mcp.core.config import settings


@pytest_asyncio.fixture
async def redis_manager():
    # Use a test-specific Redis URL if possible, or ensure your test environment Redis is isolated
    # For this example, we'll use the general settings.REDIS_URL
    # but ideally, you'd use a separate test database or mock Redis entirely.
    manager = RedisPubSubManager(redis_url=settings.REDIS_URL)
    await manager.connect_publisher()
    yield manager
    await manager.disconnect_publisher()

@pytest.mark.asyncio
async def test_publish_subscribe(redis_manager: RedisPubSubManager):
    """
    Test basic publish and subscribe functionality.
    """
    test_channel = "test_channel_pubsub"
    test_message = {"data": "test_message_content", "type": "test"}

    # Use a list to capture messages from the subscriber
    received_messages = []
    subscription_task_started = asyncio.Event()

    async def subscriber_task():
        try:
            async for message in redis_manager.subscribe_to_channel(test_channel):
                received_messages.append(message)
                # We only expect one message in this test
                if len(received_messages) >= 1:
                    break
        except asyncio.CancelledError:
            print("Subscriber task cancelled.")
            raise
        except Exception as e:
            pytest.fail(f"Subscriber task failed: {e}")
        finally:
            print(f"Subscriber task for {test_channel} finished.")


    # Start the subscriber task
    # Wrap subscriber_task in a future that can be awaited or cancelled
    subscriber_future = asyncio.create_task(subscriber_task())

    # Ensure subscriber is ready (or at least give it a moment to start)
    # A more robust way would be for subscribe_to_channel to signal readiness.
    await asyncio.sleep(0.5) # Allow time for subscription to establish

    # Publish a message
    await redis_manager.publish(test_channel, test_message)

    # Wait for the subscriber to receive the message or timeout
    try:
        await asyncio.wait_for(subscriber_future, timeout=5.0)
    except asyncio.TimeoutError:
        pytest.fail("Test timed out waiting for message.")
    finally:
        if not subscriber_future.done():
            subscriber_future.cancel()
            # Ensure cancellation is processed
            with suppress(asyncio.CancelledError):
                await subscriber_future


    assert len(received_messages) == 1
    assert received_messages[0] == test_message

@pytest.mark.asyncio
async def test_publish_without_connection(redis_manager: RedisPubSubManager):
    """
    Test that publishing without a connection raises an error.
    """
    # Ensure publisher is disconnected first
    await redis_manager.disconnect_publisher()

    test_channel = "test_channel_no_connection"
    test_message = {"data": "test_data"}

    with pytest.raises(ConnectionError, match="Publisher not connected. Cannot publish."):
        await redis_manager.publish(test_channel, test_message)

    # Reconnect for fixture cleanup
    await redis_manager.connect_publisher()


@pytest.mark.asyncio
async def test_subscribe_cancellation(redis_manager: RedisPubSubManager):
    """
    Test that the subscribe_to_channel task can be cancelled gracefully.
    """
    test_channel = "test_cancellation_channel"
    subscriber_task_instance = None

    async def cancellable_subscriber():
        nonlocal subscriber_task_instance
        subscriber_task_instance = asyncio.current_task()
        try:
            async for _ in redis_manager.subscribe_to_channel(test_channel):
                pass # Should not receive anything in this test path
        except asyncio.CancelledError:
            print(f"Cancellable subscriber for {test_channel} was cancelled as expected.")
            raise # Propagate cancellation

    task = asyncio.create_task(cancellable_subscriber())

    # Give the task a moment to start and subscribe
    await asyncio.sleep(0.2)

    assert subscriber_task_instance is not None, "Subscriber task did not set current_task reference"

    # Cancel the task
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task # Wait for cancellation to complete

    # Add a small delay to allow Redis client in subscribe_to_channel to close
    await asyncio.sleep(0.1)


@pytest.mark.asyncio
@patch('aioredis.from_url')
async def test_connect_publisher_failure(mock_from_url):
    """
    Test publisher connection failure.
    """
    mock_redis_instance = AsyncMock()
    mock_redis_instance.ping.side_effect = Exception("Redis connection failed")
    mock_from_url.return_value = mock_redis_instance

    manager = RedisPubSubManager(redis_url="redis://fake_url:1234")

    with pytest.raises(ConnectionError, match="Failed to connect Redis publisher: Redis connection failed"):
        await manager.connect_publisher()

    assert manager._publisher_client is None # Ensure client is reset

@pytest.mark.asyncio
async def test_publish_error_handling(redis_manager: RedisPubSubManager):
    """
    Test that errors during the publish call itself are raised.
    """
    test_channel = "test_publish_error_channel"
    test_message = {"data": "some_data"}

    # Mock the actual publish method on the connected client to simulate an error
    with patch.object(redis_manager._publisher_client, 'publish', new_callable=AsyncMock) as mock_publish:
        mock_publish.side_effect = Exception("Simulated Redis publish error")

        with pytest.raises(Exception, match="Simulated Redis publish error"):
            await redis_manager.publish(test_channel, test_message) 
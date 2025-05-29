"""
Redis Pub/Sub Manager for handling real-time event streaming.
"""
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional

import aioredis
from aioredis import Redis  # For type hinting

# from mcp.core.config import settings  # Assuming REDIS_URL is in settings - Unused if global instance is commented out


class RedisPubSubManager:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._publisher_client: Optional[Redis] = None
        # Subscriber clients are created per subscription typically

    async def connect_publisher(self) -> None:
        """Connects the publisher client to Redis."""
        if not self._publisher_client or self._publisher_client.closed:
            try:
                self._publisher_client = await aioredis.from_url(self.redis_url)
                # Test connection with a PING
                await self._publisher_client.ping()
                print(
                    f"Redis Pub/Sub Manager: Publisher connected to {self.redis_url}")
            except Exception as e:
                self._publisher_client = None  # Ensure client is None on failure
                # Log this error appropriately
                print(
                    f"Redis Pub/Sub Manager: Failed to connect publisher to Redis: {e}")
                # Depending on application requirements, this might be a critical error.
                raise ConnectionError(
                    f"Failed to connect Redis publisher: {e}") from e

    async def disconnect_publisher(self) -> None:
        """Closes the publisher client connection."""
        if self._publisher_client and not self._publisher_client.closed:
            await self._publisher_client.close()
            self._publisher_client = None
            print("Redis Pub/Sub Manager: Publisher disconnected.")

    async def publish(self, channel: str, message: Dict[str, Any]) -> None:
        """Publishes a message to a specific Redis channel."""
        if not self._publisher_client or self._publisher_client.closed:
            # Option 1: Try to reconnect automatically
            # print("Redis Pub/Sub Manager: Publisher not connected. Attempting to reconnect...")
            # await self.connect_publisher()
            # Option 2: Raise an error
            raise ConnectionError(
                "Redis Pub/Sub Manager: Publisher not connected. Cannot publish.")

        try:
            await self._publisher_client.publish(channel, json.dumps(message))
        except Exception as e:
            # Log this error
            print(
                f"Redis Pub/Sub Manager: Error publishing message to channel '{channel}': {e}")
            # Optionally re-raise or handle
            raise

    async def subscribe_to_channel(self, channel: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Subscribes to a Redis channel and yields messages as they are received.
        This method creates its own Redis connection for the subscription.
        """
        subscriber_client: Optional[Redis] = None
        pubsub: Optional[aioredis.client.PubSub] = None
        try:
            subscriber_client = await aioredis.from_url(self.redis_url)
            pubsub = subscriber_client.pubsub()
            await pubsub.subscribe(channel)
            print(f"Redis Pub/Sub Manager: Subscribed to channel '{channel}'")

            while True:
                # Listen for messages with a timeout to allow graceful shutdown/disconnection checks
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message.get("type") == "message":
                    try:
                        data = json.loads(message["data"])
                        yield data
                    except json.JSONDecodeError as e:
                        print(
                            f"Redis Pub/Sub Manager: Error decoding JSON message from channel '{channel}': {e} - Data: {message['data']}")
                    except Exception as e:
                        print(
                            f"Redis Pub/Sub Manager: Error processing message from '{channel}': {e}")

                # A mechanism to break the loop if the client/caller disconnects would be ideal here,
                # e.g., checking an external flag or asyncio.CancelledError propagation.
                # For FastAPI EventSourceResponse, request.is_disconnected() check is done in the route.
                # Small sleep to prevent tight loop and allow task switching
                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            print(
                f"Redis Pub/Sub Manager: Subscription to channel '{channel}' cancelled.")
            # This is expected when the client disconnects
            raise  # Re-raise to allow FastAPI/caller to handle it
        except Exception as e:
            print(
                f"Redis Pub/Sub Manager: Error in subscription to channel '{channel}': {e}")
            # Log error and potentially re-raise or handle based on policy
            # For a persistent subscriber, you might implement retry logic here.
        finally:
            if pubsub:
                try:
                    await pubsub.unsubscribe(channel)
                    # pubsub.close() or await pubsub.close() - aioredis pubsub object itself might not have close
                except Exception as e:
                    print(
                        f"Redis Pub/Sub Manager: Error during unsubscribe for channel '{channel}': {e}")
            if subscriber_client:
                await subscriber_client.close()
            print(
                f"Redis Pub/Sub Manager: Unsubscribed and connection closed for channel '{channel}'.")

# Global instance (optional, can be managed by FastAPI dependency injection)
# Ensure settings.REDIS_URL is available when this module is imported if using global instance this way.
# redis_pubsub_manager = RedisPubSubManager(settings.REDIS_URL)

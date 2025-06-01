import abc
from typing import Dict, Any, AsyncGenerator

class BasePubSubManager(abc.ABC):
    """
    Abstract base class for Pub/Sub implementations, allowing for different backends (e.g., Redis, Kafka, in-memory).
    """
    @abc.abstractmethod
    async def connect_publisher(self):
        """
        Connects the publisher client.
        """
        pass

    @abc.abstractmethod
    async def disconnect_publisher(self):
        """
        Disconnects the publisher client.
        """
        pass

    @abc.abstractmethod
    async def publish(self, channel: str, message: Dict[str, Any]):
        """
        Publishes a message to a channel.
        Args:
            channel (str): The channel to publish to.
            message (Dict[str, Any]): The message to publish.
        """
        pass

    @abc.abstractmethod
    async def subscribe_to_channel(self, channel: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Subscribes to a channel and yields incoming messages.
        Args:
            channel (str): The channel to subscribe to.
        Yields:
            Dict[str, Any]: Incoming messages from the channel.
        """
        if False:  # Never actually runs, just to satisfy linter
            yield {}

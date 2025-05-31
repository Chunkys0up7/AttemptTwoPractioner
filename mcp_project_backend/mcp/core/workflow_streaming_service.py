from typing import Dict, Any

class WorkflowStreamingService:
    """
    Service responsible for publishing workflow execution updates to a Pub/Sub system (e.g., Redis Pub/Sub).
    These updates are picked up by the SSE streaming endpoint to send to clients.

    Responsibilities:
    - Publishes workflow run updates (status changes, logs, step events) to Pub/Sub channels.
    - May handle logic for constructing event payloads before publishing.
    """
    def __init__(self, pubsub_manager):
        """
        Initialize the WorkflowStreamingService with a Pub/Sub manager.
        Args:
            pubsub_manager: An instance of a Pub/Sub manager (e.g., RedisPubSubManager).
        """
        self.pubsub_manager = pubsub_manager

    async def publish_run_update(
        self,
        run_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """
        Publishes an update for a specific workflow run to the Pub/Sub system.
        Args:
            run_id (str): The workflow run ID (can be int or UUID, converted to string for channel name).
            event_type (str): The type of event (e.g., 'status_change', 'log', 'step_started', 'step_completed').
            payload (dict): The event payload to publish.
        """
        channel = f"workflow_run_events:{run_id}"
        message = {
            "event_type": event_type,
            "payload": payload,
            # Optionally add a timestamp here
        }
        # TODO: Ensure pubsub_manager is initialized and connected in main.py lifespan
        # await self.pubsub_manager.publish(channel, message)
        print(f"STREAMING (Simulated Publish to {channel}): Event: {event_type}, Payload: {payload}")

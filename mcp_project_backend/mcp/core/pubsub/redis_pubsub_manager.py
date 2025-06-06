from mcp.core.config import settings
from mcp.core.pubsub.redis_pubsub import RedisPubSubManager

redis_pubsub_manager = RedisPubSubManager(settings.REDIS_URL) 
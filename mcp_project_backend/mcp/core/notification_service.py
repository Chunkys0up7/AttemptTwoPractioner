"""
Notification service for sending and managing user notifications.
"""

from typing import List, Dict, Any
import uuid
from datetime import datetime, timezone

class NotificationService:
    def __init__(self):
        # In-memory store: {user_id: [notification, ...]}
        self.notifications = {}

    def send_notification(self, user_id: str, message: str, type_: str = "info") -> Dict[str, Any]:
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "message": message,
            "type": type_,
            "read": False,
            "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        }
        self.notifications.setdefault(user_id, []).append(notification)
        return notification

    def get_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        notifs = self.notifications.get(user_id, [])
        if unread_only:
            return [n for n in notifs if not n["read"]]
        return notifs

    def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        for n in self.notifications.get(user_id, []):
            if n["id"] == notification_id:
                n["read"] = True
                return True
        return False 
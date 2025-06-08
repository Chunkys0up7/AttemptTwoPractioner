from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from mcp.core.notification_service import NotificationService

router = APIRouter()
service = NotificationService()

@router.post('/notifications', tags=["Notifications"])
def send_notification(
    user_id: str = Body(...),
    message: str = Body(...),
    type_: str = Body("info")
) -> Dict[str, Any]:
    """
    Send a notification to a user.
    """
    return service.send_notification(user_id, message, type_)

@router.get('/notifications', tags=["Notifications"])
def get_notifications(
    user_id: str = Query(...),
    unread_only: bool = Query(False)
) -> List[Dict[str, Any]]:
    """
    Fetch notifications for a user.
    """
    return service.get_notifications(user_id, unread_only)

@router.post('/notifications/read', tags=["Notifications"])
def mark_as_read(
    user_id: str = Body(...),
    notification_id: str = Body(...)
) -> Dict[str, Any]:
    """
    Mark a notification as read.
    """
    success = service.mark_as_read(user_id, notification_id)
    return {"success": success} 
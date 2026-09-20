"""
Notification System API
Event-driven notifications for all alerts
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


class NotificationType(str, Enum):
    """Notification types"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ALERT = "alert"


class NotificationChannel(str, Enum):
    """Notification channels"""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(BaseModel):
    """Notification model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: NotificationType
    channel: NotificationChannel
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM)
    title: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None


class NotificationPreference(BaseModel):
    """User notification preferences"""
    user_id: str
    channels_enabled: List[NotificationChannel] = Field(default_factory=list)
    types_enabled: List[NotificationType] = Field(default_factory=list)
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class NotificationCreate(BaseModel):
    """Create notification request"""
    user_id: str
    type: NotificationType
    channel: NotificationChannel
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM)
    title: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)


# In-memory storage
notifications: Dict[str, Notification] = {}
notification_preferences: Dict[str, NotificationPreference] = {}


@router.post("/notifications")
async def create_notification(notification: NotificationCreate):
    """Create a new notification"""
    # Check user preferences
    preference = notification_preferences.get(notification.user_id)
    
    if preference:
        # Check if channel is enabled
        if notification.channel not in preference.channels_enabled:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Notification channel not enabled for user")
        
        # Check if notification type is enabled
        if notification.type not in preference.types_enabled:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Notification type not enabled for user")
    
    new_notification = Notification(
        user_id=notification.user_id,
        type=notification.type,
        channel=notification.channel,
        priority=notification.priority,
        title=notification.title,
        message=notification.message,
        data=notification.data
    )
    
    notifications[new_notification.id] = new_notification
    
    return {"data": jsonable_encoder(new_notification)}


@router.get("/notifications", response_model=List[Notification])
async def list_notifications(
    user_id: str,
    unread_only: bool = False,
    type: Optional[NotificationType] = None,
    skip: int = 0,
    limit: int = 100
):
    """List notifications for a user"""
    notification_list = [
        n for n in notifications.values()
        if n.user_id == user_id
    ]
    
    if unread_only:
        notification_list = [n for n in notification_list if not n.read]
    
    if type:
        notification_list = [n for n in notification_list if n.type == type]
    
    notification_list.sort(key=lambda x: x.created_at, reverse=True)
    
    return notification_list[skip:skip + limit]


@router.get("/notifications/{notification_id}", response_model=Notification)
async def get_notification(notification_id: str):
    """Get notification by ID"""
    if notification_id not in notifications:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
    return notifications[notification_id]


@router.put("/notifications/{notification_id}/read")
async def mark_as_read(notification_id: str):
    """Mark notification as read"""
    if notification_id not in notifications:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
    
    notifications[notification_id].read = True
    notifications[notification_id].read_at = datetime.utcnow()
    
    return {"message": "Notification marked as read"}


@router.put("/notifications/{notification_id}/unread")
async def mark_as_unread(notification_id: str):
    """Mark notification as unread"""
    if notification_id not in notifications:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
    
    notifications[notification_id].read = False
    notifications[notification_id].read_at = None
    
    return {"message": "Notification marked as unread"}


@router.put("/notifications/mark-all-read")
async def mark_all_as_read(user_id: str):
    """Mark all notifications for a user as read"""
    count = 0
    for notification in notifications.values():
        if notification.user_id == user_id and not notification.read:
            notification.read = True
            notification.read_at = datetime.utcnow()
            count += 1
    
    return {"message": f"Marked {count} notifications as read"}


@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str):
    """Delete a notification"""
    if notification_id not in notifications:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
    
    del notifications[notification_id]
    
    return {"message": "Notification deleted"}


@router.post("/preferences", response_model=NotificationPreference, status_code=status.HTTP_201_CREATED)
async def set_notification_preferences(preference: NotificationPreference):
    """Set notification preferences for a user"""
    notification_preferences[preference.user_id] = preference
    return preference


@router.get("/preferences/{user_id}", response_model=NotificationPreference)
async def get_notification_preferences(user_id: str):
    """Get notification preferences for a user"""
    if user_id not in notification_preferences:
        # Return default preferences
        return NotificationPreference(
            user_id=user_id,
            channels_enabled=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
            types_enabled=[NotificationType.INFO, NotificationType.SUCCESS, NotificationType.WARNING, NotificationType.ERROR, NotificationType.ALERT]
        )
    
    return notification_preferences[user_id]


@router.get("/notifications/{user_id}/unread-count")
async def get_unread_count(user_id: str):
    """Get unread notification count for a user"""
    count = len([
        n for n in notifications.values()
        if n.user_id == user_id and not n.read
    ])
    
    return {"user_id": user_id, "unread_count": count}


@router.post("/broadcast")
async def broadcast_notification(notification: NotificationCreate, user_ids: List[str]):
    """Broadcast notification to multiple users"""
    created_notifications = []
    
    for user_id in user_ids:
        try:
            new_notification = Notification(
                user_id=user_id,
                type=notification.type,
                channel=notification.channel,
                priority=notification.priority,
                title=notification.title,
                message=notification.message,
                data=notification.data
            )
            
            notifications[new_notification.id] = new_notification
            created_notifications.append(new_notification.id)
        except Exception:
            continue
    
    return {
        "message": f"Broadcast to {len(created_notifications)} users",
        "notification_ids": created_notifications
    }

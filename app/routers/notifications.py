from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.notification_service import NotificationService
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationResponse(BaseModel):
    id: int
    type: str
    message: str
    sender: dict
    painting_id: int = None
    comment_id: int = None
    rating_id: int = None
    is_read: bool
    created_at: str

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    limit: int = Query(20, le=100, ge=1),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for the current user."""
    notifications = NotificationService.get_user_notifications(
        db, current_user.id, limit, offset, unread_only
    )
    
    result = []
    for notif in notifications:
        result.append(NotificationResponse(
            id=notif.id,
            type=notif.type.value,
            message=notif.message,
            sender={
                "id": notif.sender.id,
                "username": notif.sender.username,
                "full_name": notif.sender.full_name,
                "profile_picture": notif.sender.profile_picture
            },
            painting_id=notif.painting_id,
            comment_id=notif.comment_id,
            rating_id=notif.rating_id,
            is_read=notif.is_read,
            created_at=notif.created_at.isoformat()
        ))
    
    return result

@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications for the current user."""
    count = NotificationService.get_unread_count(db, current_user.id)
    return {"count": count}

@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read."""
    success = NotificationService.mark_notification_as_read(
        db, notification_id, current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}

@router.put("/mark-all-read")
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the current user."""
    NotificationService.mark_all_notifications_as_read(db, current_user.id)
    return {"message": "All notifications marked as read"}

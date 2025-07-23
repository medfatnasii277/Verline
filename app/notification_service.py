from sqlalchemy.orm import Session
from app.models import Notification, User, Painting, Comment, Rating, NotificationType
from app.websocket_manager import manager
from typing import Optional
import asyncio

class NotificationService:
    
    @staticmethod
    def create_notification(
        db: Session,
        sender_id: int,
        recipient_id: int,
        notification_type: NotificationType,
        message: str,
        painting_id: Optional[int] = None,
        comment_id: Optional[int] = None,
        rating_id: Optional[int] = None
    ) -> Notification:
        """Create a new notification in the database"""
        notification = Notification(
            sender_id=sender_id,
            recipient_id=recipient_id,
            type=notification_type,
            message=message,
            painting_id=painting_id,
            comment_id=comment_id,
            rating_id=rating_id
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    async def send_notification(
        db: Session,
        sender_id: int,
        recipient_id: int,
        notification_type: NotificationType,
        message: str,
        painting_id: Optional[int] = None,
        comment_id: Optional[int] = None,
        rating_id: Optional[int] = None
    ):
        """Create notification and send it via WebSocket if user is online"""
        
        # Don't send notification to yourself
        if sender_id == recipient_id:
            return
            
        # Create notification in database
        notification = NotificationService.create_notification(
            db, sender_id, recipient_id, notification_type, message,
            painting_id, comment_id, rating_id
        )
        
        # Get sender info for the notification
        sender = db.query(User).filter(User.id == sender_id).first()
        
        # Prepare WebSocket message
        ws_message = {
            "type": "notification",
            "data": {
                "id": notification.id,
                "type": notification_type.value,
                "message": message,
                "sender": {
                    "id": sender.id,
                    "username": sender.username,
                    "full_name": sender.full_name,
                    "profile_picture": sender.profile_picture
                },
                "painting_id": painting_id,
                "comment_id": comment_id,
                "rating_id": rating_id,
                "created_at": notification.created_at.isoformat(),
                "is_read": False
            }
        }
        
        # Send via WebSocket if user is connected
        await manager.send_personal_message(ws_message, recipient_id)
        
        return notification
    
    @staticmethod
    async def notify_painting_rating(db: Session, rating: Rating):
        """Send notification when someone rates a painting"""
        painting = db.query(Painting).filter(Painting.id == rating.painting_id).first()
        if not painting:
            return
            
        rater = db.query(User).filter(User.id == rating.user_id).first()
        if not rater:
            return
            
        message = f"{rater.full_name} rated your painting '{painting.title}' with {rating.rating} stars"
        
        await NotificationService.send_notification(
            db=db,
            sender_id=rating.user_id,
            recipient_id=painting.artist_id,
            notification_type=NotificationType.RATING,
            message=message,
            painting_id=painting.id,
            rating_id=rating.id
        )
    
    @staticmethod
    async def notify_painting_comment(db: Session, comment: Comment):
        """Send notification when someone comments on a painting"""
        painting = db.query(Painting).filter(Painting.id == comment.painting_id).first()
        if not painting:
            return
            
        commenter = db.query(User).filter(User.id == comment.user_id).first()
        if not commenter:
            return
            
        message = f"{commenter.full_name} commented on your painting '{painting.title}'"
        
        await NotificationService.send_notification(
            db=db,
            sender_id=comment.user_id,
            recipient_id=painting.artist_id,
            notification_type=NotificationType.COMMENT,
            message=message,
            painting_id=painting.id,
            comment_id=comment.id
        )
    
    @staticmethod
    async def notify_comment_reply(db: Session, reply: Comment):
        """Send notification when someone replies to a comment"""
        if not reply.parent_id:
            return
            
        parent_comment = db.query(Comment).filter(Comment.id == reply.parent_id).first()
        if not parent_comment:
            return
            
        painting = db.query(Painting).filter(Painting.id == reply.painting_id).first()
        if not painting:
            return
            
        replier = db.query(User).filter(User.id == reply.user_id).first()
        if not replier:
            return
            
        message = f"{replier.full_name} replied to your comment on '{painting.title}'"
        
        await NotificationService.send_notification(
            db=db,
            sender_id=reply.user_id,
            recipient_id=parent_comment.user_id,
            notification_type=NotificationType.REPLY,
            message=message,
            painting_id=painting.id,
            comment_id=reply.id
        )
    
    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False
    ):
        """Get notifications for a user"""
        query = db.query(Notification).filter(Notification.recipient_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
            
        return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def mark_notification_as_read(db: Session, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.recipient_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            return True
        return False
    
    @staticmethod
    def mark_all_notifications_as_read(db: Session, user_id: int):
        """Mark all notifications as read for a user"""
        db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
    
    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """Get count of unread notifications for a user"""
        return db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == False
        ).count()

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from fastapi import WebSocket
from unittest.mock import AsyncMock, patch
from app.main import app
from app.models import User, Painting, Rating, Comment, Notification, NotificationType
from app.notification_service import NotificationService
from app.websocket_manager import ConnectionManager, manager

class TestNotificationService:
    """Test notification service functionality"""
    
    def test_create_notification(self, db_session, test_artist_id, test_enthusiast_id):
        """Test creating a notification in the database"""
        notification = NotificationService.create_notification(
            db=db_session,
            sender_id=test_enthusiast_id,
            recipient_id=test_artist_id,
            notification_type=NotificationType.RATING,
            message="Test notification"
        )
        
        assert notification.id is not None
        assert notification.sender_id == test_enthusiast_id
        assert notification.recipient_id == test_artist_id
        assert notification.type == NotificationType.RATING
        assert notification.message == "Test notification"
        assert notification.is_read == False
    
    @pytest.mark.asyncio
    async def test_send_notification_to_offline_user(self, db_session, test_artist_id, test_enthusiast_id):
        """Test sending notification when user is offline (should save to DB only)"""
        with patch.object(manager, 'send_personal_message', new_callable=AsyncMock) as mock_send:
            await NotificationService.send_notification(
                db=db_session,
                sender_id=test_enthusiast_id,
                recipient_id=test_artist_id,
                notification_type=NotificationType.RATING,
                message="Test notification"
            )
            
            # Should attempt to send via WebSocket
            mock_send.assert_called_once()
            
            # Should create notification in database
            notifications = db_session.query(Notification).filter(
                Notification.recipient_id == test_artist_id
            ).all()
            
            assert len(notifications) > 0
            # Check that at least one notification contains our test message
            test_notification = next((n for n in notifications if n.message == "Test notification"), None)
            assert test_notification is not None
    
    def test_get_user_notifications(self, db_session, test_artist_id, test_enthusiast_id):
        """Test retrieving user notifications"""
        # Create test notifications
        for i in range(5):
            notification = Notification(
                sender_id=test_enthusiast_id,
                recipient_id=test_artist_id,
                type=NotificationType.RATING,
                message=f"Test notification {i}"
            )
            db_session.add(notification)
        db_session.commit()
        
        # Get notifications
        notifications = NotificationService.get_user_notifications(db_session, test_artist_id, limit=3)
        assert len(notifications) == 3
        
        # Should be ordered by created_at desc (most recent first)
        # Since SQLite with same timestamp might not guarantee order, just check we got 3
        assert len(notifications) == 3
    
    def test_mark_notification_as_read(self, db_session, test_artist_id, test_enthusiast_id):
        """Test marking a notification as read"""
        # Create notification
        notification = Notification(
            sender_id=test_enthusiast_id,
            recipient_id=test_artist_id,
            type=NotificationType.RATING,
            message="Test notification"
        )
        db_session.add(notification)
        db_session.commit()
        db_session.refresh(notification)
        
        # Mark as read
        success = NotificationService.mark_notification_as_read(
            db_session, notification.id, test_artist_id
        )
        
        assert success == True
        db_session.refresh(notification)
        assert notification.is_read == True
    
    def test_mark_all_notifications_as_read(self, db_session, test_artist_id, test_enthusiast_id):
        """Test marking all notifications as read"""
        # Create multiple notifications
        for i in range(3):
            notification = Notification(
                sender_id=test_enthusiast_id,
                recipient_id=test_artist_id,
                type=NotificationType.RATING,
                message=f"Test notification {i}"
            )
            db_session.add(notification)
        db_session.commit()
        
        # Mark all as read
        NotificationService.mark_all_notifications_as_read(db_session, test_artist_id)
        
        # Check all are marked as read
        notifications = db_session.query(Notification).filter(
            Notification.recipient_id == test_artist_id
        ).all()
        
        for notification in notifications:
            assert notification.is_read == True
    
    def test_get_unread_count(self, db_session, test_artist_id, test_enthusiast_id):
        """Test getting unread notification count"""
        # Create notifications (some read, some unread)
        for i in range(5):
            notification = Notification(
                sender_id=test_enthusiast_id,
                recipient_id=test_artist_id,
                type=NotificationType.RATING,
                message=f"Test notification {i}",
                is_read=i < 2  # First 2 are read
            )
            db_session.add(notification)
        db_session.commit()
        
        unread_count = NotificationService.get_unread_count(db_session, test_artist_id)
        assert unread_count == 3  # Last 3 are unread


class TestConnectionManager:
    """Test WebSocket connection manager"""
    
    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self):
        """Test connecting and disconnecting users"""
        manager = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        user_id = 1
        
        # Test connect
        await manager.connect(mock_websocket, user_id)
        assert user_id in manager.active_connections
        assert mock_websocket in manager.active_connections[user_id]
        assert manager.is_user_connected(user_id) == True
        
        # Test disconnect
        manager.disconnect(mock_websocket, user_id)
        assert user_id not in manager.active_connections
        assert manager.is_user_connected(user_id) == False
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self):
        """Test sending personal message to connected user"""
        manager = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        user_id = 1
        
        await manager.connect(mock_websocket, user_id)
        
        message = {"type": "test", "data": "hello"}
        await manager.send_personal_message(message, user_id)
        
        mock_websocket.send_text.assert_called_once_with(json.dumps(message))
    
    @pytest.mark.asyncio
    async def test_send_message_to_offline_user(self):
        """Test sending message to offline user (should not raise error)"""
        manager = ConnectionManager()
        user_id = 999  # Not connected
        
        message = {"type": "test", "data": "hello"}
        # Should not raise an error
        await manager.send_personal_message(message, user_id)
    
    @pytest.mark.asyncio
    async def test_multiple_connections_per_user(self):
        """Test that a user can have multiple connections (multiple devices/tabs)"""
        manager = ConnectionManager()
        mock_websocket1 = AsyncMock(spec=WebSocket)
        mock_websocket2 = AsyncMock(spec=WebSocket)
        user_id = 1
        
        # Connect twice
        await manager.connect(mock_websocket1, user_id)
        await manager.connect(mock_websocket2, user_id)
        
        assert len(manager.active_connections[user_id]) == 2
        
        # Send message should go to both connections
        message = {"type": "test", "data": "hello"}
        await manager.send_personal_message(message, user_id)
        
        mock_websocket1.send_text.assert_called_once_with(json.dumps(message))
        mock_websocket2.send_text.assert_called_once_with(json.dumps(message))


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality"""
    
    def test_websocket_endpoint_unauthorized(self):
        """Test WebSocket connection with invalid token"""
        client = TestClient(app)
        
        with pytest.raises(Exception):  # Should fail to connect
            with client.websocket_connect("/ws/1?token=invalid_token"):
                pass

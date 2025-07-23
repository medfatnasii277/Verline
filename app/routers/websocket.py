from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from app.websocket_manager import manager
from app.auth import get_current_user_ws
from app.database import get_db
from app.notification_service import NotificationService
from sqlalchemy.orm import Session
import json

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time notifications"""
    try:
        # Verify the user's authentication
        current_user = await get_current_user_ws(token, db)
        
        # Ensure user can only connect to their own WebSocket
        if current_user.id != user_id:
            await websocket.close(code=1008, reason="Unauthorized")
            return
            
        # Connect the user
        await manager.connect(websocket, user_id)
        
        # Send initial data - unread notifications count
        unread_count = NotificationService.get_unread_count(db, user_id)
        await manager.send_personal_message({
            "type": "unread_count",
            "data": {"count": unread_count}
        }, user_id)
        
        try:
            while True:
                # Listen for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "mark_read":
                    notification_id = message.get("notification_id")
                    if notification_id:
                        NotificationService.mark_notification_as_read(db, notification_id, user_id)
                        
                elif message.get("type") == "mark_all_read":
                    NotificationService.mark_all_notifications_as_read(db, user_id)
                    
                elif message.get("type") == "get_notifications":
                    # Send recent notifications
                    notifications = NotificationService.get_user_notifications(db, user_id, limit=10)
                    notification_data = []
                    
                    for notif in notifications:
                        notification_data.append({
                            "id": notif.id,
                            "type": notif.type.value,
                            "message": notif.message,
                            "sender": {
                                "id": notif.sender.id,
                                "username": notif.sender.username,
                                "full_name": notif.sender.full_name,
                                "profile_picture": notif.sender.profile_picture
                            },
                            "painting_id": notif.painting_id,
                            "comment_id": notif.comment_id,
                            "rating_id": notif.rating_id,
                            "is_read": notif.is_read,
                            "created_at": notif.created_at.isoformat()
                        })
                    
                    await manager.send_personal_message({
                        "type": "notifications_list",
                        "data": notification_data
                    }, user_id)
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass

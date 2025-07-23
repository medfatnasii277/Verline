from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.schemas import CommentCreate, CommentUpdate, CommentResponse
from app.crud import CommentService, PaintingService
from app.notification_service import NotificationService
import asyncio

router = APIRouter(prefix="/comments", tags=["Comments"])

class CommentCreateRequest(BaseModel):
    painting_id: int
    user_id: int
    content: str
    parent_id: Optional[int] = None

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_request: CommentCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new comment on a painting."""
    # Validate content is not empty
    if not comment_request.content or not comment_request.content.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Comment content cannot be empty"
        )
    
    # Check if painting exists
    painting = PaintingService.get_painting(db, comment_request.painting_id)
    if not painting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Painting not found"
        )
    
    # Create CommentCreate object for the service
    comment_data = CommentCreate(
        painting_id=comment_request.painting_id,
        content=comment_request.content,
        parent_id=comment_request.parent_id
    )
    
    # Create the comment
    comment = CommentService.create_comment(db, comment_data, comment_request.user_id)
    
    # Send notifications
    try:
        if comment.parent_id:
            # This is a reply - notify the parent comment author
            await NotificationService.notify_comment_reply(db, comment)
        else:
            # This is a new comment - notify the painting owner
            await NotificationService.notify_painting_comment(db, comment)
    except Exception as e:
        print(f"Failed to send comment notification: {e}")
    
    return comment

@router.get("/painting/{painting_id}", response_model=List[CommentResponse])
def get_painting_comments(
    painting_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get comments for a painting."""
    # Check if painting exists
    painting = PaintingService.get_painting(db, painting_id)
    if not painting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Painting not found"
        )
    
    return CommentService.get_painting_comments(db, painting_id, skip, limit)

@router.get("/user/{user_id}", response_model=List[CommentResponse])
def get_user_comments(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get comments by a user."""
    return CommentService.get_user_comments(db, user_id, skip, limit)

@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific comment by ID."""
    comment = CommentService.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment

@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    user_id: int = Query(..., description="User ID updating the comment"),
    db: Session = Depends(get_db)
):
    """Update a comment (owner only)."""
    updated_comment = CommentService.update_comment(
        db, comment_id, comment_update, user_id
    )
    if not updated_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to update it"
        )
    return updated_comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    user_id: int = Query(..., description="User ID deleting the comment"),
    db: Session = Depends(get_db)
):
    """Delete a comment (owner only)."""
    success = CommentService.delete_comment(db, comment_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete it"
        )

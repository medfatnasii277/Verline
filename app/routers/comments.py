from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import CommentCreate, CommentUpdate, CommentResponse
from app.crud import CommentService, PaintingService
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new comment on a painting."""
    # Check if painting exists
    painting = PaintingService.get_painting(db, comment.painting_id)
    if not painting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Painting not found"
        )
    
    return CommentService.create_comment(db, comment, current_user.id)

@router.get("/painting/{painting_id}", response_model=List[CommentResponse])
def get_painting_comments(
    painting_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
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

@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a comment (owner only)."""
    updated_comment = CommentService.update_comment(
        db, comment_id, comment_update, current_user.id
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment (owner only)."""
    success = CommentService.delete_comment(db, comment_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete it"
        )

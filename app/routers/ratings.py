from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from app.database import get_db
from app.schemas import RatingCreate, RatingResponse
from app.crud import RatingService, PaintingService
from app.auth import get_current_user
from app.models import User
from app.notification_service import NotificationService
import asyncio

router = APIRouter(prefix="/ratings", tags=["Ratings"])

@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_rating(
    rating_request: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update a rating for a painting."""
    # Check if painting exists
    painting = PaintingService.get_painting(db, rating_request.painting_id)
    if not painting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Painting not found"
        )
    
    # Prevent artists from rating their own paintings
    if painting.artist_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot rate your own painting"
        )
    
    # Create or update the rating
    rating = RatingService.create_or_update_rating(db, rating_request, current_user.id)
    
    # Send notification to painting owner
    try:
        await NotificationService.notify_painting_rating(db, rating)
    except Exception as e:
        print(f"Failed to send rating notification: {e}")
    
    return rating

@router.get("/{painting_id}/rating/{user_id}", response_model=RatingResponse)
def get_user_rating(
    painting_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user's rating for a painting."""
    rating = RatingService.get_user_rating(db, user_id, painting_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    return rating

@router.get("/painting/{painting_id}", response_model=List[RatingResponse])
def get_painting_ratings(
    painting_id: int,
    db: Session = Depends(get_db)
):
    """Get all ratings for a specific painting."""
    painting = PaintingService.get_painting(db, painting_id)
    if not painting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Painting not found"
        )
    
    return RatingService.get_painting_ratings(db, painting_id)

@router.get("/my-ratings", response_model=List[RatingResponse])
def get_user_ratings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all ratings by the current user."""
    return RatingService.get_user_ratings(db, current_user.id)

@router.get("/my-paintings-ratings", response_model=List[RatingResponse])
def get_my_paintings_ratings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all ratings received on paintings by the current artist."""
    return RatingService.get_artist_paintings_ratings(db, current_user.id)

class RatingUpdate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating value between 1 and 5")

@router.put("/{rating_id}", response_model=RatingResponse)  
def update_rating(
    rating_id: int,
    rating_update: RatingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a rating."""
    updated_rating = RatingService.update_rating(db, rating_id, rating_update.rating, current_user.id)
    if not updated_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    return updated_rating

@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    rating_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a rating."""
    success = RatingService.delete_rating(db, rating_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

@router.get("/painting/{painting_id}/average")
def get_painting_average_rating(
    painting_id: int,
    db: Session = Depends(get_db)
):
    """Get average rating for a painting."""
    painting = PaintingService.get_painting(db, painting_id)
    if not painting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Painting not found"
        )
    
    avg_data = RatingService.get_painting_average_rating(db, painting_id)
    return avg_data

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import RatingCreate, RatingResponse
from app.crud import RatingService, PaintingService

router = APIRouter(prefix="/ratings", tags=["Ratings"])

@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_rating(
    rating: RatingCreate,
    user_id: int,  # Now passed as parameter
    db: Session = Depends(get_db)
):
    """Create or update a rating for a painting."""
    # Check if painting exists
    painting = PaintingService.get_painting(db, rating.painting_id)
    if not painting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Painting not found"
        )
    
    # Prevent artists from rating their own paintings
    if painting.artist_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot rate your own painting"
        )
    
    return RatingService.create_or_update_rating(db, rating, user_id)

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

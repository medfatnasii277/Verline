from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import UserResponse, UserUpdate, PaginationParams, PaginatedResponse
from app.crud import UserService, PaintingService
from app.models import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user's profile by ID."""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/me/{user_id}", response_model=UserResponse)
def update_user_profile(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user's profile."""
    updated_user = UserService.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID."""
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/{user_id}/paintings")
def get_user_paintings(
    user_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paintings by a specific user."""
    # Check if user exists
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    skip = (page - 1) * limit
    paintings, total = PaintingService.get_user_paintings(db, user_id, skip, limit)
    
    return PaginatedResponse(
        items=paintings,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )



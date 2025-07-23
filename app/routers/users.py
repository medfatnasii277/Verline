from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from PIL import Image
from app.database import get_db
from app.schemas import UserResponse, UserUpdate, PaginationParams, PaginatedResponse, PaintingResponse
from app.crud import UserService, PaintingService
from app.models import User
from app.auth import get_current_user
from app.utils import allowed_file, secure_filename

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
def get_all_users(
    role: Optional[str] = Query(None, description="Filter by user role (artist, enthusiast)"),
    db: Session = Depends(get_db)
):
    """Get all users, optionally filtered by role."""
    return UserService.get_all_users(db, role=role)

@router.get("/artists", response_model=List[UserResponse])
def get_artists(db: Session = Depends(get_db)):
    """Get all users with artist role."""
    return UserService.get_all_users(db, role="artist")

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

@router.post("/me/{user_id}/profile-picture", response_model=UserResponse)
async def upload_profile_picture(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload profile picture for user."""
    # Check if user exists and if current user can update this profile
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only allow users to update their own profile picture
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile picture"
        )
    
    # Validate file type
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and GIF files are allowed."
        )
    
    # Validate file size (5MB limit)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum size is 5MB."
        )
    
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"profile_{user_id}_{uuid.uuid4().hex}{file_extension}"
        
        # Create upload path
        upload_dir = "uploads/profiles"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Read and validate image
        contents = await file.read()
        image = Image.open(file.file)
        
        # Resize image to max 400x400 while maintaining aspect ratio
        image.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed (for JPEG)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Save optimized image
        image.save(file_path, format='JPEG', quality=85, optimize=True)
        
        # Delete old profile picture if exists
        if user.profile_picture:
            old_path = user.profile_picture.replace('/uploads/', 'uploads/')
            if os.path.exists(old_path):
                os.remove(old_path)
        
        # Update user profile picture
        profile_picture_url = f"/uploads/profiles/{unique_filename}"
        user_update = UserUpdate(profile_picture=profile_picture_url)
        updated_user = UserService.update_user(db, user_id, user_update)
        
        return updated_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

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

@router.get("/{user_id}/paintings", response_model=PaginatedResponse[PaintingResponse])
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
    
    return PaginatedResponse[PaintingResponse](
        items=[PaintingResponse.model_validate(p) for p in paintings],
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )



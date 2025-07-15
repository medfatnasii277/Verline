from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import (
    PaintingCreate, PaintingUpdate, PaintingResponse, PaintingListResponse,
    PaginatedResponse, PaintingFilters, SortOptions
)
from app.crud import PaintingService
from app.models import User
from app.utils import save_image, delete_image_files

router = APIRouter(prefix="/paintings", tags=["Paintings"])

@router.post("/", response_model=PaintingResponse, status_code=status.HTTP_201_CREATED)
async def create_painting(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    price: Optional[float] = Form(None),
    year_created: Optional[int] = Form(None),
    dimensions: Optional[str] = Form(None),
    medium: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    artist_id: int = Form(...),  # Now require artist_id as form parameter
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Create a new painting with image upload."""
    # Save uploaded image
    image_url, thumbnail_url = await save_image(image, "paintings", "http://localhost:8000")
    
    try:
        # Create painting data
        painting_data = PaintingCreate(
            title=title,
            description=description,
            category_id=category_id,
            price=price,
            year_created=year_created,
            dimensions=dimensions,
            medium=medium,
            tags=tags
        )
        
        # Create painting in database
        painting = PaintingService.create_painting(
            db, painting_data, artist_id, image_url, thumbnail_url
        )
        
        return painting
    except Exception as e:
        # Clean up uploaded files if database operation fails
        delete_image_files(image_url, thumbnail_url)
        raise e

@router.get("/", response_model=PaginatedResponse[PaintingResponse])
def get_paintings(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    year_created: Optional[int] = Query(None),
    artist_id: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None),
    tags: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[SortOptions] = Query(None),
    db: Session = Depends(get_db)
):
    """Get paintings with filtering and pagination."""
    filters = PaintingFilters(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        year_created=year_created,
        artist_id=artist_id,
        min_rating=min_rating,
        tags=tags,
        search=search
    )
    
    skip = (page - 1) * limit
    paintings, total = PaintingService.get_paintings(db, skip, limit, filters, sort_by)
    
    # Convert paintings to response objects
    painting_responses = [PaintingResponse.model_validate(painting) for painting in paintings]
    
    return PaginatedResponse[PaintingResponse](
        items=painting_responses,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/my-paintings/{artist_id}", response_model=PaginatedResponse[PaintingResponse])
def get_artist_paintings(
    artist_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get paintings by specific artist."""
    skip = (page - 1) * limit
    filters = PaintingFilters(artist_id=artist_id)
    paintings, total = PaintingService.get_paintings(db, skip, limit, filters)
    
    # Convert paintings to response objects
    painting_responses = [PaintingResponse.model_validate(painting) for painting in paintings]
    
    return PaginatedResponse[PaintingResponse](
        items=painting_responses,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{painting_id}", response_model=PaintingResponse)
def get_painting(painting_id: int, db: Session = Depends(get_db)):
    """Get painting by ID and increment view count."""
    painting = PaintingService.get_painting(db, painting_id)
    if not painting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Painting not found"
        )
    
    # Increment view count
    PaintingService.increment_view_count(db, painting_id)
    
    return painting

@router.put("/{painting_id}", response_model=PaintingResponse)
def update_painting(
    painting_id: int,
    painting_update: PaintingUpdate,
    artist_id: int,  # Pass as parameter
    db: Session = Depends(get_db)
):
    """Update a painting (owner only)."""
    updated_painting = PaintingService.update_painting(
        db, painting_id, painting_update, artist_id
    )
    if not updated_painting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Painting not found or you don't have permission to update it"
        )
    return updated_painting

@router.delete("/{painting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_painting(
    painting_id: int,
    artist_id: int,  # Pass as parameter
    db: Session = Depends(get_db)
):
    """Delete a painting (owner only)."""
    # Get painting to retrieve image URLs for cleanup
    painting = PaintingService.get_painting(db, painting_id)
    if not painting or painting.artist_id != artist_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Painting not found or you don't have permission to delete it"
        )
    
    # Delete from database
    success = PaintingService.delete_painting(db, painting_id, artist_id)
    if success:
        # Clean up image files
        delete_image_files(painting.image_url, painting.thumbnail_url)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Painting not found or you don't have permission to delete it"
        )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import CategoryCreate, CategoryResponse
from app.crud import CategoryService
from app.auth import get_current_artist
from app.models import User

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_artist)
):
    """Create a new category (Artist only)."""
    return CategoryService.create_category(db, category)

@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories."""
    return CategoryService.get_categories(db)

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get category by ID."""
    category = CategoryService.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

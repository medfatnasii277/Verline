from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    ENTHUSIAST = "enthusiast"
    ARTIST = "artist"

class PaintingStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: UserRole = UserRole.ENTHUSIAST
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    profile_picture: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Painting Schemas
class PaintingBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    year_created: Optional[int] = None
    dimensions: Optional[str] = None
    medium: Optional[str] = None
    tags: Optional[str] = None

class PaintingCreate(PaintingBase):
    pass

class PaintingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    year_created: Optional[int] = None
    dimensions: Optional[str] = None
    medium: Optional[str] = None
    status: Optional[PaintingStatus] = None
    tags: Optional[str] = None

class PaintingResponse(PaintingBase):
    id: int
    artist_id: int
    image_url: str
    thumbnail_url: Optional[str] = None
    status: PaintingStatus
    view_count: int = 0
    average_rating: float = 0.0
    rating_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested objects
    artist: UserResponse
    category: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True

class PaintingListResponse(BaseModel):
    id: int
    title: str
    artist_id: int
    image_url: str
    thumbnail_url: Optional[str] = None
    average_rating: float = 0.0
    rating_count: int = 0
    price: Optional[float] = None
    artist: UserResponse
    category: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True

# Rating Schemas
class RatingBase(BaseModel):
    rating: int
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class RatingCreate(RatingBase):
    painting_id: int

class RatingResponse(RatingBase):
    id: int
    user_id: int
    painting_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: UserResponse
    
    class Config:
        from_attributes = True

# Comment Schemas
class CommentBase(BaseModel):
    content: str
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    painting_id: int

class CommentUpdate(BaseModel):
    content: str

class CommentResponse(CommentBase):
    id: int
    user_id: int
    painting_id: int
    is_approved: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: UserResponse
    replies: Optional[List['CommentResponse']] = []
    
    class Config:
        from_attributes = True

# Update forward reference
CommentResponse.model_rebuild()

# Pagination Schema
class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 10
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be at least 1')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v

class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    limit: int
    pages: int

# Search and Filter Schemas
class PaintingFilters(BaseModel):
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    year_created: Optional[int] = None
    artist_id: Optional[int] = None
    min_rating: Optional[float] = None
    tags: Optional[str] = None
    search: Optional[str] = None  # Search in title and description

class SortOptions(str, Enum):
    NEWEST = "newest"
    OLDEST = "oldest"
    PRICE_LOW = "price_low"
    PRICE_HIGH = "price_high"
    RATING_HIGH = "rating_high"
    RATING_LOW = "rating_low"
    MOST_VIEWED = "most_viewed"
    TITLE_AZ = "title_az"
    TITLE_ZA = "title_za"

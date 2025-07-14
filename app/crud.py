from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from app.models import User, Painting, Category, Rating, Comment
from app.schemas import (
    UserCreate, UserUpdate, PaintingCreate, PaintingUpdate, 
    CategoryCreate, RatingCreate, CommentCreate, CommentUpdate,
    PaintingFilters, SortOptions
)
from app.auth import get_password_hash

# User CRUD operations
class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        # Check if email or username already exists
        existing_user = db.query(User).filter(
            or_(User.email == user.email, User.username == user.username)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )
        
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=user.role,
            bio=user.bio
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_users(db: Session, role: Optional[str] = None) -> List[User]:
        """Get all users, optionally filtered by role."""
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        return query.all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        # Check for duplicate email/username if being changed
        if user_update.email and user_update.email != db_user.email:
            existing = db.query(User).filter(User.email == user_update.email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        if user_update.username and user_update.username != db_user.username:
            existing = db.query(User).filter(User.username == user_update.username).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Update fields
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user

# Category CRUD operations
class CategoryService:
    @staticmethod
    def create_category(db: Session, category: CategoryCreate) -> Category:
        # Check if category name already exists
        existing = db.query(Category).filter(Category.name == category.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )
        
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def get_categories(db: Session) -> List[Category]:
        return db.query(Category).all()
    
    @staticmethod
    def get_category(db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

# Painting CRUD operations
class PaintingService:
    @staticmethod
    def create_painting(
        db: Session, 
        painting: PaintingCreate, 
        artist_id: int, 
        image_url: str, 
        thumbnail_url: str
    ) -> Painting:
        db_painting = Painting(
            **painting.dict(),
            artist_id=artist_id,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            status="published"  # Set status to published by default
        )
        db.add(db_painting)
        db.commit()
        db.refresh(db_painting)
        return db_painting
    
    @staticmethod
    def get_painting(db: Session, painting_id: int) -> Optional[Painting]:
        return db.query(Painting).filter(Painting.id == painting_id).first()
    
    @staticmethod
    def get_paintings(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[PaintingFilters] = None,
        sort_by: Optional[SortOptions] = None
    ) -> Tuple[List[Painting], int]:
        query = db.query(Painting)
        
        # Only filter by published status if explicitly requested
        # For now, show all paintings regardless of status
        
        # Apply filters
        if filters:
            if filters.category_id:
                query = query.filter(Painting.category_id == filters.category_id)
            if filters.artist_id:
                query = query.filter(Painting.artist_id == filters.artist_id)
            if filters.min_price is not None:
                query = query.filter(Painting.price >= filters.min_price)
            if filters.max_price is not None:
                query = query.filter(Painting.price <= filters.max_price)
            if filters.year_created:
                query = query.filter(Painting.year_created == filters.year_created)
            if filters.min_rating is not None:
                query = query.filter(Painting.average_rating >= filters.min_rating)
            if filters.tags:
                query = query.filter(Painting.tags.contains(filters.tags))
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Painting.title.ilike(search_term),
                        Painting.description.ilike(search_term)
                    )
                )
        
        # Apply sorting
        if sort_by:
            if sort_by == SortOptions.NEWEST:
                query = query.order_by(desc(Painting.created_at))
            elif sort_by == SortOptions.OLDEST:
                query = query.order_by(asc(Painting.created_at))
            elif sort_by == SortOptions.PRICE_LOW:
                query = query.order_by(asc(Painting.price))
            elif sort_by == SortOptions.PRICE_HIGH:
                query = query.order_by(desc(Painting.price))
            elif sort_by == SortOptions.RATING_HIGH:
                query = query.order_by(desc(Painting.average_rating))
            elif sort_by == SortOptions.RATING_LOW:
                query = query.order_by(asc(Painting.average_rating))
            elif sort_by == SortOptions.MOST_VIEWED:
                query = query.order_by(desc(Painting.view_count))
            elif sort_by == SortOptions.TITLE_AZ:
                query = query.order_by(asc(Painting.title))
            elif sort_by == SortOptions.TITLE_ZA:
                query = query.order_by(desc(Painting.title))
        else:
            query = query.order_by(desc(Painting.created_at))
        
        total = query.count()
        paintings = query.offset(skip).limit(limit).all()
        
        return paintings, total
    
    @staticmethod
    def get_user_paintings(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[Painting], int]:
        query = db.query(Painting).filter(Painting.artist_id == user_id)
        total = query.count()
        paintings = query.offset(skip).limit(limit).all()
        return paintings, total
    
    @staticmethod
    def update_painting(
        db: Session, 
        painting_id: int, 
        painting_update: PaintingUpdate,
        user_id: int
    ) -> Optional[Painting]:
        db_painting = db.query(Painting).filter(
            and_(Painting.id == painting_id, Painting.artist_id == user_id)
        ).first()
        
        if not db_painting:
            return None
        
        for field, value in painting_update.dict(exclude_unset=True).items():
            setattr(db_painting, field, value)
        
        db.commit()
        db.refresh(db_painting)
        return db_painting
    
    @staticmethod
    def delete_painting(db: Session, painting_id: int, user_id: int) -> bool:
        db_painting = db.query(Painting).filter(
            and_(Painting.id == painting_id, Painting.artist_id == user_id)
        ).first()
        
        if not db_painting:
            return False
        
        db.delete(db_painting)
        db.commit()
        return True
    
    @staticmethod
    def increment_view_count(db: Session, painting_id: int) -> None:
        db.query(Painting).filter(Painting.id == painting_id).update(
            {Painting.view_count: Painting.view_count + 1}
        )
        db.commit()

# Rating CRUD operations
class RatingService:
    @staticmethod
    def create_or_update_rating(
        db: Session, 
        rating_data: RatingCreate, 
        user_id: int
    ) -> Rating:
        # Check if user has already rated this painting
        existing_rating = db.query(Rating).filter(
            and_(Rating.user_id == user_id, Rating.painting_id == rating_data.painting_id)
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_data.rating
            db.commit()
            db.refresh(existing_rating)
            rating_obj = existing_rating
        else:
            # Create new rating
            rating_obj = Rating(
                user_id=user_id,
                painting_id=rating_data.painting_id,
                rating=rating_data.rating
            )
            db.add(rating_obj)
            db.commit()
            db.refresh(rating_obj)
        
        # Update painting's average rating
        RatingService._update_painting_rating_stats(db, rating_data.painting_id)
        return rating_obj
    
    @staticmethod
    def get_user_rating(db: Session, user_id: int, painting_id: int) -> Optional[Rating]:
        return db.query(Rating).filter(
            and_(Rating.user_id == user_id, Rating.painting_id == painting_id)
        ).first()
    
    @staticmethod
    def _update_painting_rating_stats(db: Session, painting_id: int) -> None:
        # Calculate new average rating and count
        result = db.query(
            func.avg(Rating.rating).label('avg_rating'),
            func.count(Rating.id).label('rating_count')
        ).filter(Rating.painting_id == painting_id).first()
        
        avg_rating = float(result.avg_rating) if result.avg_rating else 0.0
        rating_count = result.rating_count or 0
        
        # Update painting
        db.query(Painting).filter(Painting.id == painting_id).update({
            Painting.average_rating: round(avg_rating, 2),
            Painting.rating_count: rating_count
        })
        db.commit()

# Comment CRUD operations
class CommentService:
    @staticmethod
    def create_comment(
        db: Session, 
        comment: CommentCreate, 
        user_id: int
    ) -> Comment:
        db_comment = Comment(
            user_id=user_id,
            painting_id=comment.painting_id,
            content=comment.content,
            parent_id=comment.parent_id
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    
    @staticmethod
    def get_painting_comments(
        db: Session, 
        painting_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Comment]:
        return db.query(Comment).filter(
            and_(
                Comment.painting_id == painting_id,
                Comment.parent_id.is_(None),  # Only top-level comments
                Comment.is_approved == True
            )
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_comment(
        db: Session, 
        comment_id: int, 
        comment_update: CommentUpdate,
        user_id: int
    ) -> Optional[Comment]:
        db_comment = db.query(Comment).filter(
            and_(Comment.id == comment_id, Comment.user_id == user_id)
        ).first()
        
        if not db_comment:
            return None
        
        db_comment.content = comment_update.content
        db.commit()
        db.refresh(db_comment)
        return db_comment
    
    @staticmethod
    def delete_comment(db: Session, comment_id: int, user_id: int) -> bool:
        db_comment = db.query(Comment).filter(
            and_(Comment.id == comment_id, Comment.user_id == user_id)
        ).first()
        
        if not db_comment:
            return False
        
        db.delete(db_comment)
        db.commit()
        return True

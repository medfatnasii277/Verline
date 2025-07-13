from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(enum.Enum):
    ENTHUSIAST = "enthusiast"
    ARTIST = "artist"

class PaintingStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ENTHUSIAST, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    paintings = relationship("Painting", back_populates="artist", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    paintings = relationship("Painting", back_populates="category")

class Painting(Base):
    __tablename__ = "paintings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    artist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    price = Column(Float, nullable=True)  # Optional for selling
    year_created = Column(Integer, nullable=True)
    dimensions = Column(String(100), nullable=True)  # e.g., "24x36 inches"
    medium = Column(String(100), nullable=True)  # e.g., "Oil on canvas"
    status = Column(Enum(PaintingStatus), default=PaintingStatus.DRAFT, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    average_rating = Column(Float, default=0.0, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    artist = relationship("User", back_populates="paintings")
    category = relationship("Category", back_populates="paintings")
    ratings = relationship("Rating", back_populates="painting", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="painting", cascade="all, delete-orphan")

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    painting_id = Column(Integer, ForeignKey("paintings.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    painting = relationship("Painting", back_populates="ratings")
    
    # Ensure one rating per user per painting
    __table_args__ = (
        UniqueConstraint('user_id', 'painting_id', name='unique_user_painting_rating'),
    )

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    painting_id = Column(Integer, ForeignKey("paintings.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # For replies
    is_approved = Column(Boolean, default=True, nullable=False)  # For moderation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="comments")
    painting = relationship("Painting", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

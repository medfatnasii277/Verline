import os
import uuid
from typing import Optional
from PIL import Image
from fastapi import UploadFile, HTTPException, status
from app.config import settings

def validate_image(file: UploadFile) -> None:
    """Validate uploaded image file."""
    # Check file size
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size too large. Maximum size: {settings.max_file_size / 1024 / 1024:.1f}MB"
        )
    
    # Check file extension
    allowed_extensions = settings.allowed_image_extensions.split(",")
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed formats: {', '.join(allowed_extensions)}"
        )

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename while preserving extension."""
    file_extension = original_filename.split(".")[-1].lower()
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{file_extension}"

async def save_image(file: UploadFile, subfolder: str = "paintings", base_url: str = "http://localhost:8000") -> tuple[str, str]:
    """
    Save uploaded image and create thumbnail.
    Returns tuple of (image_path, thumbnail_path) as absolute URLs.
    """
    # Validate the image
    validate_image(file)
    
    # Create upload directory if it doesn't exist
    upload_path = os.path.join(settings.upload_dir, subfolder)
    thumbnail_path = os.path.join(settings.upload_dir, subfolder, "thumbnails")
    
    os.makedirs(upload_path, exist_ok=True)
    os.makedirs(thumbnail_path, exist_ok=True)
    
    # Generate unique filename
    filename = generate_unique_filename(file.filename)
    image_file_path = os.path.join(upload_path, filename)
    thumbnail_file_path = os.path.join(thumbnail_path, f"thumb_{filename}")
    
    # Save original image
    content = await file.read()
    with open(image_file_path, "wb") as f:
        f.write(content)
    
    # Create and save thumbnail
    try:
        with Image.open(image_file_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Create thumbnail (300x300 max, maintaining aspect ratio)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            img.save(thumbnail_file_path, "JPEG", quality=85)
    except Exception as e:
        # Clean up original file if thumbnail creation fails
        if os.path.exists(image_file_path):
            os.remove(image_file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file"
        )
    
    # Return absolute URLs for frontend consumption
    image_url = f"{base_url}/uploads/{subfolder}/{filename}"
    thumbnail_url = f"{base_url}/uploads/{subfolder}/thumbnails/thumb_{filename}"
    
    return image_url, thumbnail_url

def delete_image_files(image_url: Optional[str], thumbnail_url: Optional[str]) -> None:
    """Delete image files from disk."""
    if image_url:
        image_path = os.path.join(".", image_url.lstrip("/"))
        if os.path.exists(image_path):
            os.remove(image_path)
    
    if thumbnail_url:
        thumbnail_path = os.path.join(".", thumbnail_url.lstrip("/"))
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

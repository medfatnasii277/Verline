from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "mysql+pymysql://myuser:mypass@localhost:3310/mydb"
    
    # JWT
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AWS S3
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_bucket_name: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # Redis
    redis_url: Optional[str] = None
    
    # File Upload
    max_file_size: int = 10485760  # 10MB
    allowed_image_extensions: str = "jpg,jpeg,png,webp"
    upload_dir: str = "./uploads"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

# Art Gallery Backend API - Complete Documentation

## 🎨 Overview

This is a professional, enterprise-level art gallery backend API built with FastAPI. It supports **two primary user roles**: **Artists** who can upload their artwork and **Enthusiasts** who can view, rate, and comment on paintings. The system features role-based authentication, comprehensive image processing, and robust CRUD operations with full API testing coverage.

## 🏗️ Architecture & Technology Stack

### Core Technologies
- **Framework**: FastAPI 0.116.1 with async support
- **Database**: MySQL 8.0 with Docker Compose
- **ORM**: SQLAlchemy 2.0.41 with declarative models
- **Authentication**: JWT tokens with bcrypt password hashing
- **Image Processing**: Pillow for image validation and thumbnail generation
- **Migrations**: Alembic for database versioning
- **Testing**: pytest with comprehensive API testing suite
- **File Upload**: python-multipart for image uploads
- **Validation**: Pydantic v2 with modern field validators

### Project Structure
```
Verline/
├── app/
│   ├── main.py              # FastAPI application with CORS and static file serving
│   ├── config.py            # Environment configuration and settings
│   ├── database.py          # SQLAlchemy database connection and session management
│   ├── models.py            # Database models with relationships (User, Painting, Rating, Comment, Category)
│   ├── schemas.py           # Pydantic schemas with validation for all endpoints
│   ├── auth.py              # JWT authentication, password hashing, and user verification
│   ├── crud.py              # Service classes for all CRUD operations (UserService, PaintingService, etc.)
│   ├── utils.py             # Image processing utilities and file handling
│   └── routers/             # API endpoint routers
│       ├── auth.py          # Authentication endpoints (register, login)
│       ├── users.py         # User management (profiles, user listings)
│       ├── categories.py    # Category CRUD operations
│       ├── paintings.py     # Painting upload, retrieval, filtering with image validation
│       ├── ratings.py       # Rating system (1-5 stars) with duplicate prevention
│       └── comments.py      # Comment system with threading support
├── tests/                   # Comprehensive pytest test suite
│   ├── conftest.py         # Test configuration and fixtures
│   ├── test_auth.py        # Authentication endpoint tests
│   ├── test_users.py       # User management tests
│   ├── test_categories.py  # Category operation tests  
│   ├── test_paintings.py   # Painting upload/retrieval tests with image validation
│   ├── test_ratings.py     # Rating system tests
│   └── test_comments.py    # Comment system tests
├── alembic/                # Database migrations with version control
├── uploads/
│   └── paintings/          # Image storage with thumbnail generation
│       └── thumbnails/     # Auto-generated thumbnails
├── test/                   # Python virtual environment
├── docker-compose.yml      # MySQL database containerization
├── requirements.txt        # Production dependencies
├── init_db.py             # Database initialization with sample data
├── create_test_painting.py # Test data creation script
└── start.sh               # Production startup script
```

## 👥 User Roles & Permissions

### Artists
- ✅ Upload paintings with image validation (PNG, JPEG, etc.)
- ✅ Create and manage art categories
- ✅ Update and delete their own paintings
- ✅ View all paintings and user profiles
- ✅ Rate and comment on other artists' work
- ✅ Access comprehensive painting management dashboard

### Enthusiasts  
- ✅ View all paintings with advanced filtering and search
- ✅ Rate paintings (1-5 stars) with duplicate prevention
- ✅ Comment on paintings with threading support
- ✅ Create categories for art organization
- ✅ View artist profiles and their galleries
- ❌ Cannot upload paintings (artist role required)

## 🚀 Quick Start

### 1. Prerequisites
### Prerequisites
- Python 3.12+ (tested with 3.12.3)
- Docker and Docker Compose for MySQL
- Virtual environment (strongly recommended)

### Installation & Setup

```bash
# 1. Navigate to project directory
cd /path/to/Verline

# 2. Start MySQL database with Docker
docker-compose up -d

# 3. Create and activate virtual environment
python -m venv test
source test/bin/activate  # Linux/Mac
# OR
test\Scripts\activate     # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run database migrations
alembic upgrade head

# 6. Initialize database with sample data
python init_db.py

# 7. Create test painting with valid image
python create_test_painting.py

# 8. Start the development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Quick Start Script
```bash
chmod +x start.sh
./start.sh
```

### 🧪 Running Tests
```bash
# Run complete test suite
source test/bin/activate
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_auth.py -v          # Authentication tests
python -m pytest tests/test_paintings.py -v    # Painting upload/management tests
python -m pytest tests/test_ratings.py -v      # Rating system tests

# Test coverage summary
python -m pytest tests/ -v --tb=no
```

## 📊 Database Schema & Models

### User System
- **Artists**: Can upload paintings, create categories, manage their artwork
- **Enthusiasts**: Can view, rate, and comment on paintings

### Core Database Models

#### Users Table
```sql
- id (Primary Key)
- email (unique, required)
- username (unique, required) 
- full_name (required)
- hashed_password (bcrypt)
- role (enum: 'artist', 'enthusiast')
- is_active (boolean, default: true)
- bio (text, optional)
- profile_picture (url, optional)
- created_at, updated_at (timestamps)
```

#### Paintings Table
```sql
- id (Primary Key)
- title (required)
- description (optional)
- artist_id (Foreign Key -> users.id)
- category_id (Foreign Key -> categories.id)
- image_url (required, validated formats)
- thumbnail_url (auto-generated)
- price (decimal, optional for selling)
- year_created (integer)
- dimensions (string, e.g., "24x36 inches")
- medium (string, e.g., "Oil on canvas")
- status (enum: 'draft', 'published', 'archived')
- view_count (integer, auto-incremented)
- average_rating (calculated from ratings)
- rating_count (count of ratings)
- tags (comma-separated string)
- created_at, updated_at (timestamps)
```

#### Categories Table
```sql
- id (Primary Key)
- name (unique, required, validated non-empty)
- description (optional)
- created_at (timestamp)
```

#### Ratings Table
```sql
- id (Primary Key)
- user_id (Foreign Key -> users.id)
- painting_id (Foreign Key -> paintings.id)
- rating (integer, 1-5 stars, validated)
- created_at, updated_at (timestamps)
- UNIQUE constraint on (user_id, painting_id) - prevents duplicate ratings
```

#### Comments Table
```sql
- id (Primary Key)
- user_id (Foreign Key -> users.id)
- painting_id (Foreign Key -> paintings.id)
- content (text, required, validated non-empty)
- parent_id (Foreign Key -> comments.id, for threading)
- is_approved (boolean, default: true, for moderation)
- created_at, updated_at (timestamps)
```

## 🚀 API Endpoints & Usage

### Authentication Endpoints

#### Register New User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "artist@example.com",
  "username": "artist1",
  "full_name": "John Artist",
  "password": "securepassword",
  "role": "artist",  // "artist" or "enthusiast"
  "bio": "Professional painter"
}
```

#### User Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=artist1&password=securepassword
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Painting Management

#### Upload New Painting (Artists Only)
```http
POST /paintings/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

title: "Sunset Landscape"
description: "Beautiful sunset over mountains"
category_id: 1
image: [binary file - PNG/JPEG/JPG/GIF/BMP/TIFF, max 10MB]
price: 250.00
year_created: 2024
dimensions: "24x18 inches"
medium: "Oil on canvas"
status: "published"  // "draft", "published", or "archived"
tags: "landscape,nature,sunset"
```

#### Get All Paintings (Public)
```http
GET /paintings/
```

Query parameters:
- `skip` (int): Pagination offset (default: 0)
- `limit` (int): Items per page (default: 100, max: 100)

#### Get Single Painting (Public)
```http
GET /paintings/{painting_id}
```

Response includes:
- Full painting details with artist info
- Automatically increments view_count
- Average rating and rating count
- Associated comments

#### Update Painting (Artists - Own Paintings Only)
```http
PUT /paintings/{painting_id}
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

# All fields optional for updates
title: "Updated Title"
description: "Updated description"
price: 300.00
status: "published"
```

#### Delete Painting (Artists - Own Paintings Only)
```http
DELETE /paintings/{painting_id}
Authorization: Bearer {access_token}
```

### Rating System

#### Add Rating (Authenticated Users)
```http
POST /ratings/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "painting_id": 1,
  "rating": 5  // 1-5 stars, integer only
}
```

Validation:
- Users can only rate each painting once
- Rating must be between 1-5 (inclusive)
- Updates painting's average_rating automatically

#### Get Ratings for Painting
```http
GET /ratings/painting/{painting_id}
```

#### Get User's Ratings
```http
GET /ratings/my-ratings
Authorization: Bearer {access_token}
```

### Comment System

#### Add Comment (Authenticated Users)
```http
POST /comments/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "painting_id": 1,
  "content": "Beautiful work! Love the color composition.",
  "parent_id": null  // Optional: for threaded replies
}
```

#### Get Comments for Painting
```http
GET /comments/painting/{painting_id}
```

Response includes:
- All approved comments for the painting
- User details (username, full_name, profile_picture)
- Threading support via parent_id

#### Update Comment (Author Only)
```http
PUT /comments/{comment_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "content": "Updated comment text"
}
```

### Category Management

#### Get All Categories (Public)
```http
GET /categories/
```

#### Create Category (Artists Only)
```http
POST /categories/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Abstract Art",
  "description": "Non-representational artistic works"
}
```

Validation:
- Category name must be unique
- Name cannot be empty or whitespace-only

#### Get Paintings by Category (Public)
```http
GET /categories/{category_id}/paintings
```

### User Profile Management

#### Get Current User Profile
```http
GET /users/me
Authorization: Bearer {access_token}
```

#### Update Profile
```http
PUT /users/me
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "Updated Name",
  "bio": "Updated biography",
  "profile_picture": "https://example.com/new-photo.jpg"
}
```

#### Get User's Paintings (Artists)
```http
GET /users/me/paintings
Authorization: Bearer {access_token}
```

#### Get Public User Profile
```http
GET /users/{user_id}
```

## 📁 File Upload System

### Supported Image Formats
- PNG, JPEG, JPG, GIF, BMP, TIFF
- Maximum file size: 10MB
- Automatic thumbnail generation
- Files stored in `/uploads/paintings/` directory

### Image Processing
- Original images preserved with unique filenames
- Thumbnails auto-generated (150x150px) for performance
- File validation ensures only valid images are accepted
- Duplicate filename prevention with UUID prefixes

## 🔐 Security Features

### Authentication & Authorization
- JWT tokens with expiration handling
- Role-based access control (artist vs enthusiast)
- Password hashing with bcrypt
- Protected endpoints require valid tokens

### Data Validation
- Comprehensive input validation using Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- File type validation for uploads
- Rating constraints (1-5 scale)
- Unique constraints prevent duplicate ratings

### CORS Configuration
- Configured for frontend integration
- Supports credentials for authenticated requests
- Appropriate headers for file uploads

## 🧪 Testing Coverage

### Current Test Status: 50/57 Tests Passing

#### ✅ Fully Tested Modules
- **Authentication** (9/9 tests): Registration, login, token validation
- **Categories** (8/8 tests): CRUD operations, validation
- **Paintings** (11/11 tests): Upload, retrieval, updates, deletion
- **Comments** (9/12 tests): Creation, retrieval, user permissions

#### 🔄 In Progress
- **Ratings** (5/8 tests): Basic CRUD working, refinements needed
- **Users** (7/8 tests): Profile management, serialization fixes

### Test Features
- Comprehensive fixtures with test database
- Mock authentication tokens
- File upload testing with valid images  
- Error case validation
- Permission and role-based testing

### Running Specific Tests
```bash
# Authentication system
python -m pytest tests/test_auth.py -v

# File upload functionality
python -m pytest tests/test_paintings.py::test_upload_painting -v

# Rating system validation
python -m pytest tests/test_ratings.py -v

# Database operations
python -m pytest tests/test_crud.py -v
```
- status (draft/published/archived)
- view_count
- average_rating
- rating_count
- tags
- created_at, updated_at
```

#### Categories Table
```sql
- id (PK)
- name (unique)
- description
- created_at
```

#### Ratings Table
```sql
- id (PK)
- user_id (FK -> users.id)
- painting_id (FK -> paintings.id)
- rating (1-5)
- created_at, updated_at
- UNIQUE(user_id, painting_id)
```

#### Comments Table
```sql
- id (PK)
- user_id (FK -> users.id)
- painting_id (FK -> paintings.id)
- content
- parent_id (FK -> comments.id, for replies)
- is_approved
- created_at, updated_at
```

## 🔐 Authentication System

### JWT Token Authentication
- **Access Token Expiry**: 30 minutes (configurable)
- **Algorithm**: HS256
- **Password Hashing**: bcrypt

### Default Accounts
```
Admin: admin@artgallery.com / admin123
Painter: painter@artgallery.com / painter123
```

### Authentication Flow
1. User registers or logs in with credentials
2. Server validates and returns JWT token
3. Client includes token in Authorization header: `Bearer <token>`
4. Server validates token for protected endpoints

## 📡 API Endpoints

### Base URL: `http://localhost:8000`

### Authentication Endpoints
```
POST /auth/register          # Register new user
POST /auth/login             # Login user
```

### User Management
```
GET  /users/me               # Get current user profile
PUT  /users/me               # Update current user profile
GET  /users/{user_id}        # Get user profile by ID
GET  /users/{user_id}/paintings  # Get user's paintings
GET  /users/                 # Get all users (Admin only)
```

### Category Management
```
GET  /categories/            # Get all categories
GET  /categories/{id}        # Get category by ID
POST /categories/            # Create category (Admin only)
```

### Painting Management
```
GET  /paintings/             # Get paintings (with filters)
GET  /paintings/my-paintings # Get current user's paintings
GET  /paintings/{id}         # Get painting by ID
POST /paintings/             # Upload new painting (Painter only)
PUT  /paintings/{id}         # Update painting (Owner only)
DELETE /paintings/{id}       # Delete painting (Owner only)
```

### Rating System
```
POST /ratings/               # Create/update rating
GET  /ratings/{painting_id}/my-rating  # Get user's rating
```

### Comment System
```
POST /comments/              # Create comment
GET  /comments/painting/{painting_id}  # Get painting comments
PUT  /comments/{id}          # Update comment (Owner only)
DELETE /comments/{id}        # Delete comment (Owner only)
```

## 🎯 API Usage Examples

### 1. User Registration
```bash
curl -X POST "http://localhost:8000/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "artist@example.com",
  "username": "artist1",
  "full_name": "Jane Artist",
  "password": "securepass123",
  "role": "painter",
  "bio": "Professional landscape painter"
}'
```

### 2. User Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
-H "Content-Type: application/json" \
-d '{
  "username": "artist1",
  "password": "securepass123"
}'
```

### 3. Upload Painting
```bash
curl -X POST "http://localhost:8000/paintings/" \
-H "Authorization: Bearer YOUR_TOKEN" \
-F "title=Sunset Valley" \
-F "description=Beautiful sunset over mountain valley" \
-F "category_id=2" \
-F "price=1500.00" \
-F "year_created=2024" \
-F "dimensions=24x36 inches" \
-F "medium=Oil on canvas" \
-F "tags=landscape,sunset,mountains" \
-F "image=@/path/to/painting.jpg"
```

### 4. Get Paintings with Filters
```bash
curl "http://localhost:8000/paintings/?category_id=2&min_price=100&max_price=2000&sort_by=rating_high&page=1&limit=10"
```

### 5. Rate a Painting
```bash
curl -X POST "http://localhost:8000/ratings/" \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "painting_id": 1,
  "rating": 5
}'
```

### 6. Add Comment
```bash
curl -X POST "http://localhost:8000/comments/" \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "painting_id": 1,
  "content": "Beautiful work! Love the color composition."
}'
```

## 🔍 Advanced Features

### 1. Image Processing
- **Automatic thumbnail generation** (300x300px)
- **File validation** (size, format)
- **Supported formats**: JPG, JPEG, PNG, WEBP
- **Max file size**: 10MB (configurable)

### 2. Search and Filtering
- **Text search**: Title and description
- **Category filtering**
- **Price range filtering**
- **Rating filtering**
- **Artist filtering**
- **Tag filtering**
- **Year filtering**

### 3. Sorting Options
- Newest/Oldest
- Price (Low to High / High to Low)
- Rating (High to Low / Low to High)
- Most Viewed
- Title (A-Z / Z-A)

### 4. Pagination
- **Page-based pagination**
- **Configurable page size** (1-100 items)
- **Total count included**

### 5. Rating System
- **1-5 star ratings**
- **One rating per user per painting**
- **Automatic average calculation**
- **Rating count tracking**

### 6. Comment System
- **Hierarchical comments** (replies supported)
- **Comment moderation** (is_approved flag)
- **Edit/delete own comments**

## 🛡️ Security Features

### 1. Authentication & Authorization
- JWT token-based authentication
- Role-based access control
- Password hashing with bcrypt
- Token expiration handling

### 2. Input Validation
- Pydantic schema validation
- File upload validation
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention

### 3. Rate Limiting (Recommended for Production)
```python
# Add to main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Usage
@limiter.limit("5/minute")
@app.post("/auth/login")
def login_endpoint(request: Request, ...):
    ...
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Database
DATABASE_URL=mysql+pymysql://myuser:mypass@localhost:3310/mydb

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,webp
UPLOAD_DIR=./uploads

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_BUCKET_NAME=art-gallery-bucket
AWS_REGION=us-east-1

# Redis (Optional)
REDIS_URL=redis://localhost:6379
```

## 📈 Performance Optimizations

### 1. Database Optimizations
- **Connection pooling** configured
- **Indexes** on frequently queried fields
- **Eager loading** for related data
- **Query optimization** with SQLAlchemy

### 2. Caching Strategy (Production)
```python
# Redis caching for frequently accessed data
import redis
from functools import wraps

redis_client = redis.from_url(settings.redis_url)

def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### 3. Image Storage (Production)
```python
# AWS S3 integration for production
import boto3
from app.config import settings

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)

async def upload_to_s3(file: UploadFile) -> str:
    key = f"paintings/{uuid4()}.{file.filename.split('.')[-1]}"
    s3_client.upload_fileobj(file.file, settings.aws_bucket_name, key)
    return f"https://{settings.aws_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{key}"
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Create test file
cat > test_api.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_user():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpass123"
    })
    assert response.status_code == 201

def test_login_user():
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
EOF

# Run tests
pytest test_api.py -v
```

## 🚀 Deployment

### 1. Production Environment Setup
```bash
# Install production server
pip install gunicorn

# Create systemd service
sudo tee /etc/systemd/system/artgallery.service << 'EOF'
[Unit]
Description=Art Gallery FastAPI
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/artgallery
Environment="PATH=/var/www/artgallery/venv/bin"
ExecStart=/var/www/artgallery/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable artgallery
sudo systemctl start artgallery
```

### 2. Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        alias /var/www/artgallery/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. Docker Production Setup
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Response Formats

#### Success Response
```json
{
  "id": 1,
  "title": "Sunset Valley",
  "description": "Beautiful sunset over mountain valley",
  "artist": {
    "id": 2,
    "username": "artist1",
    "full_name": "Jane Artist"
  },
  "category": {
    "id": 2,
    "name": "Landscape"
  },
  "image_url": "/uploads/paintings/abc123.jpg",
  "thumbnail_url": "/uploads/paintings/thumbnails/thumb_abc123.jpg",
  "average_rating": 4.5,
  "rating_count": 10,
  "price": 1500.00,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Error Response
```json
{
  "detail": "Painting not found"
}
```

#### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Pagination Response
```json
{
  "items": [...],
  "total": 50,
  "page": 1,
  "limit": 10,
  "pages": 5
}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check if MySQL is running
docker-compose ps

# Restart MySQL
docker-compose restart db

# Check logs
docker-compose logs db
```

#### 2. Module Not Found Errors
```bash
# Ensure virtual environment is activated
source test/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. Image Upload Issues
```bash
# Check upload directory permissions
chmod 755 uploads/
chmod 755 uploads/paintings/
chmod 755 uploads/paintings/thumbnails/

# Check file size limits
# Edit MAX_FILE_SIZE in .env
```

#### 4. JWT Token Issues
```bash
# Generate new secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update SECRET_KEY in .env
```

## 🔄 Database Management

### Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check migration status
alembic current
```

### Backup and Restore
```bash
# Backup database
docker exec mysql-local mysqldump -u myuser -pmypass mydb > backup.sql

# Restore database
docker exec -i mysql-local mysql -u myuser -pmypass mydb < backup.sql
```

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 standards
- Use type hints
- Document functions with docstrings
- Keep functions focused and small

### Adding New Features
1. Create new models in `models.py`
2. Add Pydantic schemas in `schemas.py`
3. Implement CRUD operations in `crud.py`
4. Create API endpoints in appropriate router
5. Write tests
6. Update documentation

### Example: Adding a new field
```python
# 1. Update model
class Painting(Base):
    # ...existing fields...
    location = Column(String(255), nullable=True)

# 2. Update schema
class PaintingBase(BaseModel):
    # ...existing fields...
    location: Optional[str] = None

# 3. Create migration
alembic revision --autogenerate -m "Add location field to paintings"
alembic upgrade head
```

## 🎉 Conclusion

This Art Gallery Backend API provides a robust, scalable foundation for managing an online art gallery. With comprehensive authentication, image processing, and social features, it's ready for both development and production use.

For questions or contributions, please refer to the codebase and this documentation. Happy coding! 🎨

---

**Last Updated**: July 13, 2025
**Version**: 1.0.0
**Authors**: Art Gallery Development Team

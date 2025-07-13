# Art Gallery Backend API - Complete Documentation

## 🎨 Overview

This is a professional, enterprise-level art gallery backend API built with FastAPI. It allows painters to upload their artwork and visitors to view, rate, and comment on paintings. The system features role-based authentication, image processing, and comprehensive CRUD operations.

## 🏗️ Architecture

### Technology Stack
- **Framework**: FastAPI 0.116.1
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0.41
- **Authentication**: JWT with bcrypt
- **Image Processing**: Pillow
- **Migrations**: Alembic
- **File Upload**: python-multipart
- **Validation**: Pydantic

### Project Structure
```
fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and session
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic schemas for validation
│   ├── auth.py              # Authentication and authorization
│   ├── crud.py              # Database CRUD operations
│   ├── utils.py             # Utility functions (image processing)
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── users.py         # User management endpoints
│       ├── categories.py    # Category management endpoints
│       ├── paintings.py     # Painting management endpoints
│       ├── ratings.py       # Rating system endpoints
│       └── comments.py      # Comment system endpoints
├── alembic/                 # Database migrations
├── uploads/                 # File upload directory
├── test/                    # Virtual environment
├── docker-compose.yml       # MySQL database setup
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── init_db.py              # Database initialization script
└── start.sh                # Startup script
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Virtual environment (recommended)

### 2. Setup Instructions

```bash
# Clone and navigate to project
cd /path/to/fastapi

# Start MySQL database
docker-compose up -d

# Activate virtual environment
source test/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Initialize database with sample data
python init_db.py

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Quick Start Script
```bash
chmod +x start.sh
./start.sh
```

## 📊 Database Schema

### User Roles
- **VISITOR**: Can view, rate, and comment on paintings
- **PAINTER**: Can upload, manage paintings + visitor permissions
- **ADMIN**: Full system access + painter permissions

### Core Models

#### Users Table
```sql
- id (PK)
- email (unique)
- username (unique)
- full_name
- hashed_password
- role (visitor/painter/admin)
- is_active
- bio
- profile_picture
- created_at, updated_at
```

#### Paintings Table
```sql
- id (PK)
- title
- description
- artist_id (FK -> users.id)
- category_id (FK -> categories.id)
- image_url
- thumbnail_url
- price (optional)
- year_created
- dimensions
- medium
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

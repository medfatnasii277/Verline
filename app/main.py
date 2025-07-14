from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.exc import SQLAlchemyError
from app.database import engine, Base
from app.routers import auth, users, categories, paintings, ratings, comments
import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app with proper OpenAPI configuration
app = FastAPI(
    title="Art Gallery API",
    description="""
    A comprehensive backend API for an art gallery platform where artists can upload their work 
    and enthusiasts can view, rate, and comment on paintings.
    
    ## Authentication
    
    Most endpoints require authentication using Bearer tokens:
    1. Register a new account using `/auth/register`
    2. Login using `/auth/login` to get an access token
    3. Include the token in the Authorization header: `Bearer YOUR_TOKEN_HERE`
    
    ## User Roles
    
    - **Artist**: Can upload paintings, create categories, and do everything enthusiasts can do
    - **Enthusiast**: Can view paintings, rate them, and leave comments
    
    ## Usage
    
    You can test all endpoints using the interactive documentation below or use the provided 
    HTTP file (`api-tests.http`) for comprehensive testing with tools like REST Client.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure security scheme for OpenAPI
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/paintings", exist_ok=True)
os.makedirs("uploads/paintings/thumbnails", exist_ok=True)

# Mount static files for serving uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(paintings.router)
app.include_router(ratings.router)
app.include_router(comments.router)

# Global exception handler
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Art Gallery API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Art Gallery API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

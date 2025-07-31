# Verline - Modern Art Gallery Platform

## Overview
Verline is a full-stack art gallery platform built with FastAPI (Python) and React (TypeScript). It enables artists to showcase their work and enthusiasts to discover, rate, and comment on paintings. The platform features real-time notifications, advanced profile management, and a modern, minimalist UI.

---

## Key Features
- Role-based authentication for Artists and Enthusiasts
- Profile management: bio, location, website, profile picture upload
- Painting management: upload, edit, delete, image validation, thumbnail generation
- Ratings: 1-5 star system, artist and enthusiast views
- Comments: threaded, real-time notifications
- Real-time notifications: WebSocket for ratings and comments
- Statistics: artist dashboards, painting metrics
- Comprehensive unit tests: backend logic and API endpoints
- Modern UI/UX: responsive, painting-focused design


---

## Tech Stack
- **Backend**: FastAPI, Python, SQLAlchemy, Pydantic, Alembic, MySQL, pytest
- **Frontend**: React, TypeScript, Styled Components, Tailwind CSS, Vite
- **Other**: REST API, WebSocket, File Upload, Image Processing

---

## How to Run

### Backend
1. Create and activate a Python virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Set up `.env` with MySQL connection and secret key
4. Run migrations: `alembic upgrade head`
5. Start server: `uvicorn app.main:app --reload`

### Frontend
1. Navigate to `verline-frontend`
2. Install dependencies: `npm install`
3. Start dev server: `npm run dev`

---

## Directory Structure
```
Verline/
├── app/                # FastAPI backend
│   ├── models.py       # Database models
│   ├── crud.py         # CRUD logic
│   ├── routers/        # API endpoints
│   ├── notification_service.py # WebSocket notifications
│   └── ...
├── verline-frontend/   # React frontend
│   ├── src/pages/      # Main pages
│   ├── src/components/ # UI components
│   └── ...
├── tests/              # Backend unit tests
├── uploads/            # Uploaded images
├── alembic/            # DB migrations
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # MySQL setup
└── README.md           # This file
```

---

## Testing
- Run backend unit tests: `pytest tests/ -v`
- Coverage includes authentication, profile, paintings, ratings, comments, notifications

---

## Important Notes
- No cloud, external storage, or rate limiting implemented
- All features listed above are present and tested
- Designed for local or self-hosted deployment

---

## License
MIT

#!/bin/bash
# Art Gallery Backend Startup Script

echo "🎨 Welcome to Art Gallery Backend Setup!"
echo "======================================="

# Check if virtual environment exists
if [ ! -d "test" ]; then
    echo "❌ Virtual environment 'test' not found!"
    echo "Please run: python3 -m venv test"
    exit 1
fi

# Activate virtual environment
source test/bin/activate

echo "✅ Virtual environment activated"

# Check if requirements are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
else
    echo "✅ Dependencies already installed"
fi

# Check database connection
echo "🔍 Checking database connection..."
python -c "
import pymysql
try:
    connection = pymysql.connect(
        host='localhost',
        port=3310,
        user='myuser',
        password='mypass',
        database='mydb'
    )
    connection.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('Make sure to run: docker-compose up -d')
    exit(1)
"

# Run migrations
echo "🔄 Running database migrations..."
if [ -f "alembic/versions/*" ]; then
    alembic upgrade head
else
    echo "📝 Creating initial migration..."
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
fi

echo "✅ Database migrations completed"

# Create uploads directory
mkdir -p uploads/paintings/thumbnails
echo "✅ Upload directories created"

echo ""
echo "🚀 Starting Art Gallery Backend Server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo "💾 Database: MySQL on localhost:3310"
echo ""

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

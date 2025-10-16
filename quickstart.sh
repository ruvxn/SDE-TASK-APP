#!/bin/bash

echo "==================================="
echo "Project Management App Quick Start"
echo "==================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your database credentials!"
    echo "   nano .env"
    echo ""
    read -p "Press Enter after you've configured .env file..."
fi

# Check PostgreSQL connection
echo ""
echo "Checking database connection..."
if psql -d project_management -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✓ Database connection successful"
else
    echo "✗ Cannot connect to database 'project_management'"
    echo ""
    echo "Creating database..."
    createdb project_management

    if [ $? -eq 0 ]; then
        echo "✓ Database created successfully"
    else
        echo "✗ Failed to create database"
        echo "Please create it manually: createdb project_management"
        exit 1
    fi
fi

# Initialize database
echo ""
read -p "Do you want to initialize database with sample data? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Initializing database with sample data..."
    python init_db.py --with-data
else
    echo "Initializing database (no sample data)..."
    python init_db.py
fi

echo ""
echo "==================================="
echo "✓ Setup complete!"
echo "==================================="
echo ""
echo "Starting application..."
echo "Access at: http://localhost:5000"
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Sample login credentials:"
    echo "  Username: testuser"
    echo "  Password: password123"
    echo ""
fi

echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python run.py

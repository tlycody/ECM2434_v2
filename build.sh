#!/usr/bin/env bash

# Exit on error
set -o errexit

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Initialize database if needed
echo "Initializing database..."
python manage.py init_db || echo "Database initialization skipped or failed, continuing..."
python manage.py check_db || echo "Database check skipped or failed, continuing..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Build React frontend
if [ -d "bingo-frontend" ]; then
    echo "Building React frontend..."
    cd bingo-frontend
    npm install
    npm run build  # This is important - use "build" not "start" for production
    cd ..
fi

echo "Build completed successfully!"
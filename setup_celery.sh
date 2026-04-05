#!/bin/bash

# Quick Celery Setup and Run Script for macOS/Linux

echo ""
echo "========================================"
echo "Finance Dashboard - Celery Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Virtual environment created!"
fi

# Activate virtual environment
source .venv/bin/activate

# Install/Update dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo ""
    echo "WARNING: Redis is not installed"
    echo "Install Redis:"
    echo "  macOS: brew install redis"
    echo "  Ubuntu: sudo apt-get install redis-server"
    echo ""
    read -p "Press Enter to continue anyway..."
else
    echo "Redis is installed!"
fi

# Display instructions
echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To run the application with Celery:"
echo ""
echo "1. Start Redis Server (in a new terminal):"
echo "   redis-server"
echo ""
echo "2. Start Celery Worker (in a new terminal):"
echo "   celery -A project_settings worker -l info"
echo ""
echo "3. Start Celery Beat (in a new terminal):"
echo "   celery -A project_settings beat -l info"
echo ""
echo "4. Start Django Server (this terminal):"
echo "   python manage.py runserver"
echo ""
echo "For more information, see CELERY_SETUP.md"
echo ""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime

# Create FastAPI application
app = FastAPI(title="Developer Dashboard")

# Models for API responses
class Repository(BaseModel):
    name: str
    url: str
    description: Optional[str]
    clone_url: str
    last_commit: Optional[str]
    branches: Optional[List[str]]

class DocumentationSection(BaseModel):
    title: str
    content: str
    last_updated: datetime
    subsections: Optional[List[Dict[str, str]]]

class DeploymentStep(BaseModel):
    step: int
    title: str
    description: str
    code_snippet: Optional[str]
    note: Optional[str]

# Serve the HTML file
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return FileResponse("developer-front.html")

# Repository information endpoint
@app.get("/api/repository", response_model=Repository)
async def get_repository_info():
    """Fetch repository information"""
    try:
        return Repository(
            name="ECM2434_v2",
            url="https://github.com/CaffeinatedDivas/ECM2434_v2",
            description="This is a BINGO game designed to promote sustainability on campus, where players complete tasks to earn points and rewards. \nThere are nine games. When a user completes a task, it turns into a stamp, and they earn points. Each game is worth a set number of points and requires either visiting a location or uploading a picture. For location-based tasks, players must scan a QR code to verify they have been there. Players can earn bonus points for completing tasks in a specific pattern. \nThe game has a time limit of one month, with bonus points for early completion. The top three players with the highest scores will receive rewards such as gift cards.",
            clone_url="https://github.com/CaffeinatedDivas/ECM2434_v2.git",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repository data: {str(e)}")

# Documentation endpoint
@app.get("/api/documentation", response_model=List[DocumentationSection])
async def get_documentation():
    """Fetch documentation sections"""
    return [
        DocumentationSection(
            title="Authentication & Setup",
            content="This session states the instructions for setting up the development environment to use the API.",
            last_updated=datetime.now(),
            subsections=[
                {
                    "title": "Create your Developer Account",
                    "content": "1. Request access via email \n2. You'll receive an invitation to complete registration form \n3. Authenticate your identity and a speicial password is created only for you"
                },
            ]
        ),
        DocumentationSection(
            title="API Documentation",
            content="This session is a detailed guidelines that explain how developers can use an API (Application Programming Interface).",
            last_updated=datetime.now(),
            subsections=[
                {
                    "title": "Authentication",
                    "content": "This section is about how to authenticate API requests. It explains how users or developers must provide proof of identity when making API calls. "
                },
                {
                    "title": "Locations API",
                    "content": "- GET /api/locations : List all game locations\n- POST /api/locations : Create a new location\n- GET /api/locations/{id} : Get location details\n- PUT /api/locations/{id} : Update a location\n- DELETE /api/locations/{id} : Remove a location"
                },
                {
                    "title": "Photo Verification API",
                    "content": "- POST /api/photos : Submit a photo for verification\n- GET /api/photos/pending : List pending verification photos\n- PUT /api/photos/{id}/verify : Mark a photo as verified"
                }
            ]
        ),
        DocumentationSection(
            title="Photo Verification System",
            content="This system allows users to submit photos from locations that can be verified by game keepers",
            last_updated=datetime.now(),
            subsections=[
                {
                    "title": "How It Works",
                    "content": "1. Users take photos at specific locations in the game\n2. Photos are uploaded to the game board. \n3. Game keepers review photos through the admin panel\n4. Verified photos unlock achievements for users"
                },
            ]
        ),
        DocumentationSection(
            title="QR Code System",
            content="This system allows users to scan the QR codes from locations",
            last_updated=datetime.now(),
            subsections=[
                {
                    "title": "How It Works",
                    "content": "1. Choose the game on the game baord. \n2. Scanner appeared to allow the users to do the scanning. \n3. Achievements are unlocked for users if the QR code is accurate."
                },
            ]
        ),
    ]

# Deployment guide endpoint
@app.get("/api/deployment", response_model=List[DeploymentStep])
async def get_deployment_guide():
    """Fetch deployment instructions"""
    return [
        DeploymentStep(
            step=1,
            title="Environment Setup",
            description="Set up your Python environment and install the repo",
            code_snippet="# Clone the repository\ngit clone https://github.com/CaffeinatedDivas/ECM2434_A_2_202425.git\n\n# Create and activate virtual environment\npython3 -m venv venv\nsource venv/bin/activate  # On Windows: venv\\Scripts\\activate\npip install django\npip install djangorestframework\npip install djangorestframework-simplejwt\npip install django-cors-headers\npip install Pillow\npython manage.py migrate\npip uninstall django-extensions\npip install django-extensions\npip install django-debug-toolbar\npython manage.py runserver\n\n# Install backend dependencies\npip install -r requirements.txt\n\n# Install frontend dependencies\ncd bingo-frontend\nnpm install\nnpm start"
        ),
        DeploymentStep(
            step=2,
            title="Configuration",
            description="Configure environment settings for your deployment",
            code_snippet="# Copy example configuration files\ncp .env.example .env\ncp frontend/.env.example frontend/.env\n\n# Edit .env file with your settings\n# Required variables:\n# - DATABASE_URL: Your database connection string\n# - SECRET_KEY: A secure random string\n# - STORAGE_PATH: Where to store uploaded photos",
        ),
        DeploymentStep(
            step=3,
            title="Database Setup",
            description="Initialize the database and run migrations",
            code_snippet="# Initialize the database\npython manage.py init_db\n\n# Run migrations\npython manage.py migrate"
        ),
        DeploymentStep(
            step=4,
            title="Testing Your Setup",
            description="Run the application in development mode to test your configuration",
            code_snippet="# Start backend server\npython manage.py runserver\n\n# In another terminal, start frontend\ncd frontend\nnpm run dev"
        ),
    ]

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
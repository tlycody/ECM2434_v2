# Import necessary modules from FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

# Import Pydantic for request/response validation
from pydantic import BaseModel

# Import typing utilities for better type hinting
from typing import List, Optional, Dict, Any

# Import OS module for file handling and datetime for timestamps
import os
from datetime import datetime


# Initialize FastAPI application
app = FastAPI(title="Developer Dashboard")

# Data Models for API Responses
class Repository(BaseModel):
    """Model representing repository metadata."""
    name: str
    url: str
    description: Optional[str]
    clone_url: str
    last_commit: Optional[str] = None  
    branches: Optional[List[str]] = None  

class DocumentationSection(BaseModel):
    """Model representing a section of the documentation."""
    title: str
    content: str
    last_updated: datetime
    subsections: Optional[List[Dict[str, str]]] = None  

class DeploymentStep(BaseModel):
    """Model representing a step in the deployment guide."""
    step: int
    title: str
    description: str
    code_snippet: Optional[str] = None 
    note: Optional[str] = None 

# API Endpoints

# Serve the HTML dashboard
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Returns the developer dashboard HTML file."""
    return FileResponse("developer-front.html")

# Health check endpoint for monitoring service status
@app.get("/health")
async def health_check():
    """Returns a simple health check response."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Endpoint to retrieve repository metadata
@app.get("/api/repository", response_model=Repository)
async def get_repository_info():
    """Fetch repository details including name, description, and URLs."""
    try:
        return Repository(
            name="ECM2434_v2",
            url="https://github.com/CaffeinatedDivas/ECM2434_v2",
            description="This is a BINGO game designed to promote sustainability on campus. Players complete tasks to earn points and rewards. \n"
                        "There are nine games, and users earn stamps for completed tasks. Tasks require visiting a location or uploading a picture. \n"
                        "For location-based tasks, players must scan a QR code for verification. Bonus points are awarded for specific patterns. \n"
                        "The game lasts one month, and the top three players win prizes like gift cards.",
            clone_url="https://github.com/CaffeinatedDivas/ECM2434_v2.git",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repository data: {str(e)}")


# Endpoint to retrieve API documentation
@app.get("/api/documentation", response_model=List[DocumentationSection])
async def get_documentation():
    """Fetch documentation sections and API usage guides."""
    return [
        DocumentationSection(
            title="Authentication & Setup",
            content="Instructions for setting up the development environment to use the API.",
            last_updated=datetime.now(),
            subsections=[
                {
                    "title": "Create your Developer Account",
                    "content": "1. Request access via email \n"
                               "2. You'll receive an invitation to complete registration \n"
                               "3. Authenticate your identity and a special password is created only for you"
                },
            ]
        ),
        DocumentationSection(
            title="API Documentation",
            content="Guidelines for interacting with the API.",
            last_updated=datetime.now(),
            subsections=[
                {
                    "title": "Authentication",
                    "content": "Explains how to authenticate API requests using tokens."
                },
                {
                    "title": "Locations API",
                    "content": "- GET /api/locations : List all game locations\n"
                               "- POST /api/locations : Create a new location\n"
                               "- GET /api/locations/{id} : Retrieve location details\n"
                               "- PUT /api/locations/{id} : Update a location\n"
                               "- DELETE /api/locations/{id} : Remove a location"
                },
                {
                    "title": "Photo Verification API",
                    "content": "- POST /api/photos : Submit a photo for verification\n"
                               "- GET /api/photos/pending : List pending verification photos\n"
                               "- PUT /api/photos/{id}/verify : Approve a submitted photo"
                }
            ]
        ),
    ]


# Endpoint to retrieve the deployment guide
@app.get("/api/deployment", response_model=List[DeploymentStep])
async def get_deployment_guide():
    """Fetch step-by-step instructions for deploying the application."""
    return [
        DeploymentStep(
            step=1,
            title="Environment Setup",
            description="Set up your Python environment and install dependencies.",
            code_snippet="# Clone the repository\ngit clone https://github.com/CaffeinatedDivas/ECM2434_v2.git\n\n"
                         "# Create and activate virtual environment\npython3 -m venv venv\nsource venv/bin/activate\n\n"
                         "# Install backend dependencies\npip install -r requirements.txt\n\n"
                         "# Install frontend dependencies\ncd bingo-frontend\nnpm install\nnpm start"
        ),
        DeploymentStep(
            step=2,
            title="Configuration",
            description="Configure environment variables before deployment.",
            code_snippet="# Copy example environment file\ncp .env.example .env\n\n"
                         "# Edit .env with your settings (database URL, secret keys, storage paths)."
        ),
        DeploymentStep(
            step=3,
            title="Database Setup",
            description="Initialize the database and apply migrations.",
            code_snippet="# Initialize the database\npython manage.py init_db\n\n"
                         "# Apply migrations\npython manage.py migrate"
        ),
        DeploymentStep(
            step=4,
            title="Testing Your Setup",
            description="Run the backend and frontend locally to verify configuration.",
            code_snippet="# Start backend server\npython manage.py runserver\n\n"
                         "# In another terminal, start frontend\ncd frontend\nnpm run dev"
        ),
    ]


# Application Entry Point

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
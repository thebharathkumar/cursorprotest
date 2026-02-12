"""
ATS Resume Scoring Agent - Main Application
FastAPI server with web interface for resume analysis
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.api import router as api_router


# Create FastAPI app
app = FastAPI(
    title="ATS Resume Scoring Agent",
    description="Intelligent agent for analyzing and scoring resumes based on ATS criteria",
    version="1.0.0"
)

# Include API routes
app.include_router(api_router, prefix="/api", tags=["Resume Analysis"])

# Serve frontend
frontend_dir = Path("frontend")


@app.get("/")
async def serve_frontend():
    """Serve the main HTML page."""
    return FileResponse(frontend_dir / "index.html")


# Mount static files if needed
if (frontend_dir / "static").exists():
    app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ATS Resume Scoring Agent")
    print("=" * 60)
    print("\n📊 Starting server...")
    print("🌐 Access the application at: http://localhost:8000")
    print("\n📝 Upload your resume to get instant ATS scoring!")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

"""
FastAPI routes for ATS Resume Scoring Agent
"""

import os
import shutil
from pathlib import Path
from typing import Dict
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from backend.parser import ResumeParser
from backend.scorer import ATSScorer


router = APIRouter()

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload and analyze a resume file.
    
    Args:
        file: Resume file (PDF, DOCX, or TXT)
        
    Returns:
        JSON response with ATS score and analysis
    """
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Save uploaded file
    file_path = UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Parse and score resume
    try:
        parser = ResumeParser()
        parser.parse_file(str(file_path))
        
        scorer = ATSScorer(parser)
        results = scorer.calculate_score()
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "score": results['score'],
            "grade": results['grade'],
            "breakdown": results['breakdown'],
            "recommendations": results['recommendations'],
        })
        
    except Exception as e:
        # Clean up file if it exists
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ATS Resume Scoring Agent"}

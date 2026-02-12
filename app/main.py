"""
ATS Resume Scoring Agent - FastAPI Application
Provides a web interface and API for analyzing resumes against ATS criteria.
"""

import json
import os
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

try:
    from app.services.resume_parser import ResumeParser
    from app.services.ats_scorer import ATSScorer
    from app.services.resume_generator import ResumeGenerator
    from app.services.resume_enhancer import ResumeEnhancer
except ImportError:
    from api.resume_parser import ResumeParser
    from api.ats_scorer import ATSScorer
    from api.resume_generator import ResumeGenerator
    from api.resume_enhancer import ResumeEnhancer

# --- App Setup ---

app = FastAPI(
    title="ATS Resume Scoring Agent",
    description="Upload a resume to receive an ATS compatibility score with detailed feedback.",
    version="1.0.0",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Mount static files if any
static_dir = os.path.join(BASE_DIR, "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Service instances
parser = ResumeParser()
scorer = ATSScorer()
generator = ResumeGenerator()
enhancer = ResumeEnhancer()

# --- Constants ---

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main upload page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
):
    """
    Analyze an uploaded resume file.

    - **file**: PDF or DOCX resume file.
    - **job_description**: (Optional) Job description text for keyword matching.

    Returns a detailed ATS scoring report.
    """
    # Validate file type
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ("pdf", "docx"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a PDF or DOCX file.",
        )

    # Read file content
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File is too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB.",
        )

    # Parse the resume
    try:
        parsed = parser.parse(content, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while parsing the resume: {str(e)}",
        )

    # Check that we got meaningful content
    if not parsed["text"].strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the file. The file may be image-based or empty. "
                   "Please use a text-based resume.",
        )

    if parsed["word_count"] < 20:
        raise HTTPException(
            status_code=400,
            detail="Very little text extracted from the file. Please ensure it's a valid resume document.",
        )

    # Score the resume
    try:
        jd = job_description.strip() if job_description else None
        report = scorer.score(parsed, jd)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during scoring: {str(e)}",
        )

    report["_parsed"] = {
        "text": parsed["text"],
        "sections": parsed["sections"],
        "word_count": parsed["word_count"],
        "format": parsed["format"],
    }

    return report


@app.post("/api/enhance")
async def enhance_resume(
    parsed_data: str = Form(...),
    score_report: str = Form(...),
    job_description: Optional[str] = Form(None),
):
    """Enhance a resume and return an improved PDF."""
    try:
        parsed = json.loads(parsed_data)
        report = json.loads(score_report)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request.")

    jd = (job_description or "").strip() or None

    try:
        ctx = enhancer.enhance(parsed, report, jd)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")

    try:
        pdf_bytes = generator.generate(ctx, jd or "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    safe_name = (ctx.get("full_name") or "Enhanced_Resume").strip().replace(" ", "_")
    filename = f"{safe_name}_Enhanced_Resume.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/generate")
async def generate_resume(
    context: str = Form(...),
    job_description: str = Form(...),
):
    """
    Generate a tailored one-page PDF resume.

    - **context**: JSON string with user details.
    - **job_description**: The target job posting text.

    Returns a downloadable PDF file.
    """
    try:
        ctx = json.loads(context)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in context field.")

    if not isinstance(ctx, dict):
        raise HTTPException(status_code=400, detail="Context must be a JSON object.")

    jd = (job_description or "").strip()
    if not jd:
        raise HTTPException(status_code=400, detail="Job description is required.")

    if not ctx.get("full_name", "").strip():
        raise HTTPException(status_code=400, detail="Full name is required in the context.")

    try:
        pdf_bytes = generator.generate(ctx, jd)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate resume PDF: {str(e)}",
        )

    safe_name = ctx.get("full_name", "resume").strip().replace(" ", "_")
    filename = f"{safe_name}_Resume.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ATS Resume Scoring Agent"}

from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from ats_agent.models import ATSReviewResponse
from ats_agent.parser import ResumeParsingError, extract_text_from_upload
from ats_agent.scorer import review_resume_text


MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB

app = FastAPI(
    title="ATS Resume Scoring Agent",
    description="Upload a resume and receive an ATS compatibility review.",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/review-resume", response_model=ATSReviewResponse)
async def review_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(default=None),
) -> ATSReviewResponse:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 5 MB upload limit.")

    try:
        text = extract_text_from_upload(file.filename or "", content)
    except ResumeParsingError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc

    try:
        result = review_resume_text(text, job_description=job_description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ATSReviewResponse(filename=file.filename, **result)


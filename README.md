# ATS Resume Scoring Agent

A lightweight FastAPI agent that reviews an uploaded resume and returns an ATS (Applicant Tracking System) compatibility score with actionable feedback.

## What it does

When a resume is uploaded (`.txt`, `.pdf`, or `.docx`), the agent:

1. Extracts plain text from the file.
2. Scores ATS readiness across key components:
   - Keyword alignment (with optional job description)
   - Section coverage
   - Readability
   - Impact/quantified achievements
   - Contact detail completeness
3. Returns:
   - Overall ATS score (0-100)
   - Component breakdown
   - Matched/missing keywords
   - Improvement suggestions

## Project structure

```text
ats_agent/
  __init__.py
  main.py
  models.py
  parser.py
  scorer.py
tests/
  test_api.py
  test_scorer.py
requirements.txt
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally

```bash
uvicorn ats_agent.main:app --reload
```

Open docs at:

- `http://127.0.0.1:8000/docs`

## API usage

### Health

```bash
curl http://127.0.0.1:8000/health
```

### Review uploaded resume

```bash
curl -X POST "http://127.0.0.1:8000/review-resume" \
  -F "file=@/path/to/resume.pdf" \
  -F "job_description=Looking for Python SQL API cloud experience"
```

Example response fields:

- `score`
- `verdict`
- `component_scores`
- `matched_keywords`
- `missing_keywords`
- `suggestions`

## Run tests

```bash
pytest -q
```


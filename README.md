# ATS Resume Scoring Agent

An intelligent resume analysis tool that scores your resume against Applicant Tracking System (ATS) criteria and provides detailed, actionable feedback to help you land more interviews.

## Features

- **Resume Upload** - Supports PDF and DOCX formats via drag-and-drop or file browser
- **ATS Compatibility Scoring** - Overall score (0-100) with letter grade
- **8 Scoring Categories**:
  - Contact Information completeness
  - Section Structure and organization
  - Keyword Optimization (generic or against a job description)
  - Formatting Compatibility
  - Quantifiable Achievements
  - Action Verb usage
  - Resume Length appropriateness
  - Readability and clarity
- **Job Description Matching** - Optional job description input for targeted keyword analysis
- **Detailed Feedback** - Strengths, recommendations, and warnings for each category
- **Modern Web UI** - Beautiful dark-themed interface with animated score displays

## Quick Start

### Prerequisites

- Python 3.9+

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd <repo-name>

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

The app will start at **http://localhost:8000**.

### Alternative: Run with uvicorn directly

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

1. Open **http://localhost:8000** in your browser
2. Upload a resume (PDF or DOCX)
3. Optionally paste a job description for targeted keyword matching
4. Click **Analyze Resume**
5. Review your score, category breakdowns, and actionable feedback

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web interface |
| POST | `/api/analyze` | Analyze a resume (multipart form: `file` + optional `job_description`) |
| GET | `/api/health` | Health check |

### Example API Usage

```bash
# Basic analysis
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@resume.pdf"

# With job description
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@resume.pdf" \
  -F "job_description=We are looking for a senior Python developer..."
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application & routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── resume_parser.py    # PDF/DOCX text extraction
│   │   └── ats_scorer.py       # ATS scoring engine
│   ├── static/                 # Static assets
│   └── templates/
│       └── index.html          # Web UI
├── run.py                      # Entry point
├── requirements.txt            # Python dependencies
└── README.md
```

## Scoring Methodology

The overall score is a weighted average of 8 categories:

| Category | Weight | What It Checks |
|----------|--------|----------------|
| Contact Info | 10% | Email, phone, LinkedIn, location, name |
| Sections | 15% | Essential (experience, education, skills) + recommended sections |
| Keywords | 20% | Industry keywords or job description match |
| Formatting | 15% | ATS-safe characters, date consistency, file format |
| Achievements | 15% | Numbers, percentages, dollar amounts, metrics |
| Action Verbs | 10% | Strong verbs vs. weak phrases |
| Length | 5% | Word count within optimal range (400-800 words) |
| Readability | 10% | Sentence length, bullet points, paragraph structure |

## License

MIT

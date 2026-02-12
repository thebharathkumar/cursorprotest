# ATS Resume Agent

An intelligent resume tool that **scores your existing resume** against ATS criteria and can **generate a new one-page PDF resume** tailored to any job description.

## Features

### Score Resume
- **Resume Upload** - Supports PDF and DOCX formats via drag-and-drop or file browser
- **ATS Compatibility Scoring** - Overall score (0-100) with letter grade
- **8 Scoring Categories**: Contact Info, Section Structure, Keywords, Formatting, Achievements, Action Verbs, Length, Readability
- **Job Description Matching** - Optional JD input for targeted keyword analysis
- **Detailed Feedback** - Strengths, recommendations, and warnings per category

### Generate Resume (NEW)
- **One-Page PDF Generation** - Fill in your details and paste a job description to generate a professionally formatted, ATS-friendly PDF
- **Structured Form** - Separate fields for personal info, summary, experience (with bullet points), education, skills, certifications, and projects
- **Keyword Tailoring** - Skills are automatically reordered to prioritize JD-matching keywords
- **Instant Download** - PDF is generated server-side and downloaded directly to your browser
- **Modern Web UI** - Beautiful dark-themed tabbed interface

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
2. Use the **Score Resume** tab to upload and analyze an existing resume
3. Use the **Generate Resume** tab to create a tailored one-page PDF:
   - Fill in your personal info, experience, education, and skills
   - Paste the target job description
   - Click **Generate PDF Resume** to download

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web interface |
| POST | `/api/analyze` | Score a resume (multipart: `file` + optional `job_description`) |
| POST | `/api/generate` | Generate a PDF resume (multipart: `context` JSON + `job_description`) |
| GET | `/api/health` | Health check |

### Example API Usage

```bash
# Score an existing resume
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@resume.pdf" \
  -F "job_description=We are looking for a senior Python developer..."

# Generate a new resume PDF
curl -X POST http://localhost:8000/api/generate \
  -F 'context={"full_name":"Jane Doe","email":"jane@example.com","phone":"(555) 987-6543","location":"San Francisco, CA","summary":"Senior engineer with 7+ years experience...","experience":[{"title":"Senior Engineer","company":"Amazon","dates":"2020 - Present","bullets":["Led microservices team","Reduced costs by 35%"]}],"education":[{"degree":"M.S. CS","school":"Stanford","dates":"2015-2017"}],"skills":"Python, AWS, Docker, Kubernetes"}' \
  -F 'job_description=Senior Software Engineer: Python, AWS, microservices...' \
  -o resume.pdf
```

## Deploy to Vercel

This project is fully configured for **one-click deployment to Vercel**.

### Option 1: Deploy via Vercel Dashboard

1. Push this repo to GitHub
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import the repository
4. Vercel will auto-detect the configuration from `vercel.json`
5. Click **Deploy** -- no environment variables needed

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy (from the project root)
vercel

# Deploy to production
vercel --prod
```

### How It Works on Vercel

- **`public/index.html`** is served as a static file at the root URL (`/`)
- **`api/index.py`** runs as a Python serverless function handling `/api/*` routes
- **`vercel.json`** configures the routing between static files and the API
- No server to manage -- scales automatically with Vercel's edge network

## Project Structure

```
.
├── api/                          # Vercel serverless functions
│   ├── index.py                  # FastAPI app (Vercel entry point)
│   ├── resume_parser.py          # PDF/DOCX text extraction
│   ├── ats_scorer.py             # ATS scoring engine
│   └── resume_generator.py       # One-page PDF resume generator
├── public/
│   └── index.html                # Static web UI (served by Vercel CDN)
├── app/                          # Local development server
│   ├── __init__.py
│   ├── main.py                   # FastAPI app (local dev entry point)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── resume_parser.py      # PDF/DOCX text extraction
│   │   ├── ats_scorer.py         # ATS scoring engine
│   │   └── resume_generator.py   # One-page PDF resume generator
│   ├── static/
│   └── templates/
│       └── index.html            # Web UI template
├── vercel.json                   # Vercel deployment configuration
├── run.py                        # Local development entry point
├── requirements.txt              # Python dependencies
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

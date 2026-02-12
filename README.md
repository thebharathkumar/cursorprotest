# ATS Resume Scoring Agent

An intelligent agent that analyzes and scores resumes based on Applicant Tracking System (ATS) criteria.

## Quick Demo

Try the application with example resumes:

```bash
# Start the server
./start.sh
# or
python main.py

# Open browser to http://localhost:8000
# Upload example_resumes/good_resume.txt or example_resumes/basic_resume.txt
```

## Features

- 📄 **Multi-format Support**: Upload resumes in PDF, DOCX, or TXT format
- 🎯 **Comprehensive ATS Scoring**: Evaluates resumes across multiple criteria
- 📊 **Detailed Feedback**: Provides actionable insights to improve ATS compatibility
- 🚀 **Real-time Analysis**: Instant scoring and recommendations
- 💡 **Smart Recommendations**: Specific suggestions for improvement

## ATS Scoring Criteria

The agent evaluates resumes based on:

1. **Contact Information** (10 points): Presence of email, phone, location
2. **Keywords & Skills** (25 points): Industry-relevant keywords and technical skills
3. **Formatting** (20 points): Clean structure, proper sections, readability
4. **Experience Section** (20 points): Clear job titles, companies, dates, descriptions
5. **Education** (10 points): Degree, institution, graduation details
6. **Measurable Achievements** (10 points): Quantifiable results and metrics
7. **Length Optimization** (5 points): Appropriate resume length (1-2 pages)

**Total Score**: 100 points

### Score Interpretation

- **90-100**: Excellent - ATS-optimized
- **75-89**: Good - Minor improvements needed
- **60-74**: Fair - Several improvements recommended
- **Below 60**: Needs Work - Major improvements required

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd workspace
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download required NLP models:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Usage

### Start the Server

```bash
python main.py
```

The application will start on `http://localhost:8000`

### Using the Web Interface

1. Open your browser and navigate to `http://localhost:8000`
2. Click "Choose File" and select your resume (PDF, DOCX, or TXT)
3. Click "Analyze Resume"
4. View your ATS score and detailed feedback

### API Endpoints

#### Upload and Score Resume

```bash
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- file: Resume file (PDF, DOCX, or TXT)

Response:
{
  "score": 85,
  "grade": "Good",
  "breakdown": {
    "contact_info": {"score": 10, "max": 10, "feedback": "..."},
    "keywords": {"score": 20, "max": 25, "feedback": "..."},
    ...
  },
  "recommendations": ["...", "..."]
}
```

## Project Structure

```
workspace/
├── main.py                 # FastAPI application entry point
├── backend/
│   ├── api.py             # API routes
│   ├── parser.py          # Resume parsing logic
│   └── scorer.py          # ATS scoring algorithm
├── frontend/
│   └── index.html         # Web interface
├── requirements.txt       # Python dependencies
└── README.md             # Documentation
```

## Technologies Used

- **Backend**: FastAPI, Python
- **Resume Parsing**: PyPDF2, python-docx, NLTK
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **NLP**: NLTK for text analysis

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Support

For issues or questions, please open an issue on GitHub.

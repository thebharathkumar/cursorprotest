# ATS Resume Scoring Agent - Usage Guide

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 3. Access the Web Interface

Open your web browser and navigate to:
```
http://localhost:8000
```

## Using the Web Interface

### Step-by-Step Guide

1. **Upload Your Resume**
   - Click on the upload box or drag and drop your resume file
   - Supported formats: PDF, DOCX, TXT

2. **Analyze**
   - Click the "Analyze Resume" button
   - Wait a few seconds for processing

3. **Review Results**
   - View your overall ATS score (0-100)
   - Check your grade (Excellent, Good, Fair, or Needs Improvement)
   - Review detailed breakdown by category
   - Read personalized recommendations

4. **Improve and Re-test**
   - Make improvements based on recommendations
   - Upload the updated resume to see your new score

## Understanding Your Score

### Score Ranges

- **90-100 (Excellent)**: Your resume is highly optimized for ATS
- **75-89 (Good)**: Strong resume with minor areas for improvement
- **60-74 (Fair)**: Decent resume but needs several improvements
- **Below 60 (Needs Improvement)**: Major improvements required

### Scoring Categories

#### 1. Contact Information (10 points)
- Email address (4 points)
- Phone number (3 points)
- Professional URLs - LinkedIn, portfolio (3 points)

**Tips:**
- Always include professional email
- Add phone number with proper formatting
- Link to LinkedIn and personal portfolio/GitHub

#### 2. Keywords & Skills (25 points)
- Technical skills and keywords
- Industry-relevant terms
- Job-specific competencies

**Tips:**
- List 10-15+ relevant skills
- Include both hard and soft skills
- Match keywords from job descriptions
- Use industry-standard terminology

#### 3. Formatting (20 points)
- Clear section headers
- Consistent structure
- Readability

**Tips:**
- Use standard section names (Experience, Education, Skills)
- Keep formatting clean and simple
- Use bullet points for clarity
- Avoid complex tables or graphics

#### 4. Experience Section (20 points)
- Job titles and companies
- Employment dates
- Action verbs and achievements

**Tips:**
- Start with strong action verbs (developed, managed, led)
- Include dates in consistent format
- Focus on accomplishments, not just duties
- Use bullet points for each role

#### 5. Education (10 points)
- Degree and institution
- Graduation date
- Relevant coursework or honors

**Tips:**
- Include degree name and field of study
- Add graduation year
- Mention GPA if above 3.5

#### 6. Quantifiable Achievements (10 points)
- Numbers and percentages
- Measurable results
- Concrete metrics

**Tips:**
- Add metrics wherever possible
- Use percentages to show improvement
- Include dollar amounts, time saved, or efficiency gains
- Example: "Increased sales by 30%" instead of "Improved sales"

#### 7. Length Optimization (5 points)
- Appropriate word count
- 1-2 pages optimal

**Tips:**
- Aim for 400-800 words (1-2 pages)
- Remove outdated or irrelevant information
- Be concise but comprehensive

## API Usage

### Upload and Score Endpoint

**Endpoint:** `POST /api/upload`

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/resume.pdf"
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/upload"
files = {"file": open("resume.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Response Format:**
```json
{
  "success": true,
  "filename": "resume.pdf",
  "score": 85,
  "grade": "Good",
  "breakdown": {
    "contact_info": {
      "score": 10,
      "max": 10,
      "feedback": ["✓ Email address found", "✓ Phone number found"]
    },
    ...
  },
  "recommendations": [
    "Add more industry-relevant keywords",
    "Include quantifiable achievements"
  ]
}
```

### Health Check Endpoint

**Endpoint:** `GET /api/health`

**Example:**
```bash
curl http://localhost:8000/api/health
```

## Best Practices for ATS-Friendly Resumes

### DO:
✓ Use standard fonts (Arial, Calibri, Times New Roman)
✓ Include relevant keywords from job description
✓ Use standard section headers
✓ Save as PDF or DOCX
✓ Include contact information at the top
✓ Use bullet points for achievements
✓ Add quantifiable metrics
✓ Keep it to 1-2 pages
✓ Use chronological format

### DON'T:
✗ Use tables, images, or graphics
✗ Include headers/footers
✗ Use unusual fonts or colors
✗ Abbreviate without explanation
✗ Use first-person pronouns (I, me, my)
✗ Include personal information (age, photo, marital status)
✗ Use multiple columns
✗ Save as .jpg or other image formats

## Troubleshooting

### Issue: File Upload Failed
- **Solution**: Check file format (PDF, DOCX, or TXT only)
- **Solution**: Ensure file size is reasonable (< 10MB)

### Issue: Low Score Despite Good Resume
- **Solution**: Check if all sections are clearly labeled
- **Solution**: Add more relevant keywords
- **Solution**: Include measurable achievements

### Issue: Server Won't Start
- **Solution**: Check if port 8000 is available
- **Solution**: Ensure all dependencies are installed
- **Solution**: Verify Python version (3.8+)

## Tips for Maximum Score

1. **Customize for Each Job**
   - Read the job description carefully
   - Include keywords from the posting
   - Highlight relevant experience

2. **Use Action Verbs**
   - Start bullets with strong verbs
   - Examples: achieved, developed, led, implemented, increased

3. **Quantify Everything**
   - Add numbers to show impact
   - Use percentages, dollars, time periods

4. **Keep It Current**
   - Update regularly
   - Remove outdated skills or experience
   - Focus on recent 10-15 years

5. **Proofread**
   - Check for typos and grammar
   - Ensure consistent formatting
   - Ask someone to review

## Support

For issues or questions:
- Check the README.md file
- Review this usage guide
- Open an issue on GitHub

## License

MIT License - see LICENSE file for details

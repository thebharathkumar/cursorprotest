"""
Resume Parser Module
Extracts text and structured information from various resume formats.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
import docx


class ResumeParser:
    """Parse resumes from different file formats."""
    
    def __init__(self):
        self.text = ""
        self.sections = {}
        
    def parse_file(self, file_path: str) -> str:
        """
        Parse resume file and extract text content.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Extracted text content
        """
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            self.text = self._parse_pdf(file_path)
        elif file_extension == '.docx':
            self.text = self._parse_docx(file_path)
        elif file_extension == '.txt':
            self.text = self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        self._extract_sections()
        return self.text
    
    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
        return text
    
    def _parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {str(e)}")
    
    def _parse_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Error parsing TXT: {str(e)}")
    
    def _extract_sections(self):
        """Extract common resume sections from text."""
        section_headers = {
            'contact': r'(contact|personal\s+information)',
            'summary': r'(summary|objective|profile)',
            'experience': r'(experience|work\s+history|employment)',
            'education': r'(education|academic|qualification)',
            'skills': r'(skills|technical\s+skills|competencies)',
            'projects': r'(projects|portfolio)',
            'certifications': r'(certifications|certificates|licenses)',
        }
        
        for section_name, pattern in section_headers.items():
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                self.sections[section_name] = True
    
    def extract_email(self) -> Optional[str]:
        """Extract email address from resume."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, self.text)
        return match.group(0) if match else None
    
    def extract_phone(self) -> Optional[str]:
        """Extract phone number from resume."""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, self.text)
            if match:
                return match.group(0)
        return None
    
    def extract_urls(self) -> List[str]:
        """Extract URLs (LinkedIn, GitHub, portfolio) from resume."""
        url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
        urls = re.findall(url_pattern, self.text)
        return urls
    
    def extract_skills(self) -> List[str]:
        """Extract skills mentioned in the resume."""
        # Common technical and professional skills
        skill_keywords = [
            'python', 'java', 'javascript', 'c\\+\\+', 'c#', 'ruby', 'php', 'swift', 'kotlin',
            'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'express',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'machine learning', 'deep learning', 'data analysis', 'artificial intelligence',
            'project management', 'agile', 'scrum', 'leadership', 'communication',
            'html', 'css', 'typescript', 'graphql', 'rest api', 'microservices',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn',
        ]
        
        found_skills = []
        text_lower = self.text.lower()
        
        for skill in skill_keywords:
            if re.search(r'\b' + skill + r'\b', text_lower):
                found_skills.append(skill.replace('\\+\\+', '++').replace('\\#', '#'))
        
        return list(set(found_skills))
    
    def count_words(self) -> int:
        """Count total words in resume."""
        words = re.findall(r'\b\w+\b', self.text)
        return len(words)
    
    def has_section(self, section: str) -> bool:
        """Check if resume has a specific section."""
        return section in self.sections
    
    def extract_dates(self) -> List[str]:
        """Extract dates from resume (for experience/education)."""
        date_patterns = [
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b',
            r'\b\d{4}\s*-\s*(?:Present|Current|\d{4})\b',
            r'\b\d{1,2}/\d{4}\b',
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, self.text, re.IGNORECASE))
        
        return dates
    
    def has_quantifiable_achievements(self) -> bool:
        """Check if resume contains quantifiable achievements (numbers, percentages)."""
        patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Dollar amounts
            r'\d+\s*(?:million|thousand|billion)',  # Large numbers
            r'(?:increased|decreased|improved|reduced|grew)\s+(?:by\s+)?\d+',  # Action + number
        ]
        
        for pattern in patterns:
            if re.search(pattern, self.text, re.IGNORECASE):
                return True
        
        return False
    
    def get_text_length(self) -> int:
        """Get character count of resume text."""
        return len(self.text)

"""
ATS Scorer Module
Evaluates resumes based on Applicant Tracking System criteria.
"""

from typing import Dict, List, Tuple
from backend.parser import ResumeParser


class ATSScorer:
    """Score resumes based on ATS compatibility criteria."""
    
    # Scoring weights for different criteria
    WEIGHTS = {
        'contact_info': 10,
        'keywords': 25,
        'formatting': 20,
        'experience': 20,
        'education': 10,
        'achievements': 10,
        'length': 5,
    }
    
    def __init__(self, parser: ResumeParser):
        """
        Initialize scorer with a resume parser.
        
        Args:
            parser: ResumeParser instance with parsed resume data
        """
        self.parser = parser
        self.breakdown = {}
        
    def calculate_score(self) -> Dict:
        """
        Calculate comprehensive ATS score.
        
        Returns:
            Dictionary with score, grade, breakdown, and recommendations
        """
        total_score = 0
        
        # Score each criterion
        contact_score = self._score_contact_info()
        keywords_score = self._score_keywords()
        formatting_score = self._score_formatting()
        experience_score = self._score_experience()
        education_score = self._score_education()
        achievements_score = self._score_achievements()
        length_score = self._score_length()
        
        # Add to total
        total_score = (
            contact_score +
            keywords_score +
            formatting_score +
            experience_score +
            education_score +
            achievements_score +
            length_score
        )
        
        # Determine grade
        grade = self._get_grade(total_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        return {
            'score': total_score,
            'grade': grade,
            'breakdown': self.breakdown,
            'recommendations': recommendations,
        }
    
    def _score_contact_info(self) -> int:
        """Score contact information (10 points)."""
        score = 0
        feedback = []
        max_score = self.WEIGHTS['contact_info']
        
        # Check email (4 points)
        email = self.parser.extract_email()
        if email:
            score += 4
            feedback.append("✓ Email address found")
        else:
            feedback.append("✗ Missing email address")
        
        # Check phone (3 points)
        phone = self.parser.extract_phone()
        if phone:
            score += 3
            feedback.append("✓ Phone number found")
        else:
            feedback.append("✗ Missing phone number")
        
        # Check URLs (LinkedIn, portfolio) (3 points)
        urls = self.parser.extract_urls()
        if urls:
            score += 3
            feedback.append(f"✓ {len(urls)} professional URL(s) found")
        else:
            feedback.append("✗ No professional URLs (LinkedIn, portfolio) found")
        
        self.breakdown['contact_info'] = {
            'score': score,
            'max': max_score,
            'feedback': feedback,
        }
        
        return score
    
    def _score_keywords(self) -> int:
        """Score keywords and skills (25 points)."""
        max_score = self.WEIGHTS['keywords']
        feedback = []
        
        # Extract skills
        skills = self.parser.extract_skills()
        skill_count = len(skills)
        
        # Score based on number of relevant skills
        if skill_count >= 15:
            score = max_score
            feedback.append(f"✓ Excellent: {skill_count} relevant skills/keywords found")
        elif skill_count >= 10:
            score = int(max_score * 0.8)
            feedback.append(f"✓ Good: {skill_count} relevant skills/keywords found")
        elif skill_count >= 5:
            score = int(max_score * 0.6)
            feedback.append(f"⚠ Fair: {skill_count} relevant skills/keywords found")
        else:
            score = int(max_score * 0.3)
            feedback.append(f"✗ Limited: Only {skill_count} relevant skills/keywords found")
        
        if skills:
            feedback.append(f"Found skills: {', '.join(skills[:10])}")
            if len(skills) > 10:
                feedback.append(f"... and {len(skills) - 10} more")
        
        self.breakdown['keywords'] = {
            'score': score,
            'max': max_score,
            'feedback': feedback,
            'skills_found': skills,
        }
        
        return score
    
    def _score_formatting(self) -> int:
        """Score formatting and structure (20 points)."""
        score = 0
        max_score = self.WEIGHTS['formatting']
        feedback = []
        
        # Check for key sections (12 points - 3 per section)
        required_sections = ['experience', 'education', 'skills']
        sections_found = 0
        
        for section in required_sections:
            if self.parser.has_section(section):
                score += 4
                sections_found += 1
                feedback.append(f"✓ {section.title()} section present")
            else:
                feedback.append(f"✗ {section.title()} section missing or unclear")
        
        # Check for optional but valuable sections (4 points)
        optional_sections = ['summary', 'projects', 'certifications']
        optional_found = sum(1 for s in optional_sections if self.parser.has_section(s))
        
        if optional_found >= 2:
            score += 4
            feedback.append(f"✓ {optional_found} additional sections found (summary/projects/certifications)")
        elif optional_found == 1:
            score += 2
            feedback.append("⚠ Consider adding more sections (summary, projects, certifications)")
        else:
            feedback.append("✗ Missing additional sections (summary, projects, certifications)")
        
        # Check for clean formatting indicators (4 points)
        text_length = self.parser.get_text_length()
        word_count = self.parser.count_words()
        
        # Check if text isn't too cluttered (reasonable word/char ratio)
        if word_count > 0 and (text_length / word_count) < 10:
            score += 4
            feedback.append("✓ Clean formatting with good readability")
        else:
            feedback.append("⚠ Formatting may be too cluttered or have issues")
        
        self.breakdown['formatting'] = {
            'score': score,
            'max': max_score,
            'feedback': feedback,
        }
        
        return score
    
    def _score_experience(self) -> int:
        """Score experience section (20 points)."""
        max_score = self.WEIGHTS['experience']
        feedback = []
        
        # Check if experience section exists
        has_experience = self.parser.has_section('experience')
        
        if not has_experience:
            self.breakdown['experience'] = {
                'score': 0,
                'max': max_score,
                'feedback': ["✗ No experience section found"],
            }
            return 0
        
        score = 5  # Base points for having the section
        feedback.append("✓ Experience section present")
        
        # Check for dates (5 points)
        dates = self.parser.extract_dates()
        if len(dates) >= 2:
            score += 5
            feedback.append(f"✓ Employment dates found ({len(dates)} date entries)")
        elif len(dates) == 1:
            score += 2
            feedback.append("⚠ Limited date information")
        else:
            feedback.append("✗ No clear employment dates found")
        
        # Check for action verbs and descriptions (10 points)
        action_verbs = [
            'developed', 'managed', 'led', 'created', 'implemented', 'designed',
            'built', 'improved', 'increased', 'reduced', 'achieved', 'delivered',
            'collaborated', 'coordinated', 'analyzed', 'optimized', 'established',
        ]
        
        text_lower = self.parser.text.lower()
        verbs_found = sum(1 for verb in action_verbs if verb in text_lower)
        
        if verbs_found >= 8:
            score += 10
            feedback.append(f"✓ Strong action verbs used ({verbs_found} found)")
        elif verbs_found >= 4:
            score += 6
            feedback.append(f"✓ Good use of action verbs ({verbs_found} found)")
        elif verbs_found >= 2:
            score += 3
            feedback.append(f"⚠ Limited action verbs ({verbs_found} found)")
        else:
            feedback.append("✗ Few or no action verbs found")
        
        self.breakdown['experience'] = {
            'score': min(score, max_score),
            'max': max_score,
            'feedback': feedback,
        }
        
        return min(score, max_score)
    
    def _score_education(self) -> int:
        """Score education section (10 points)."""
        max_score = self.WEIGHTS['education']
        feedback = []
        
        # Check if education section exists
        has_education = self.parser.has_section('education')
        
        if has_education:
            score = 10
            feedback.append("✓ Education section present")
            
            # Check for dates
            dates = self.parser.extract_dates()
            if dates:
                feedback.append("✓ Graduation date(s) included")
        else:
            score = 0
            feedback.append("✗ No education section found")
        
        self.breakdown['education'] = {
            'score': score,
            'max': max_score,
            'feedback': feedback,
        }
        
        return score
    
    def _score_achievements(self) -> int:
        """Score quantifiable achievements (10 points)."""
        max_score = self.WEIGHTS['achievements']
        feedback = []
        
        has_achievements = self.parser.has_quantifiable_achievements()
        
        if has_achievements:
            score = max_score
            feedback.append("✓ Quantifiable achievements found (numbers, percentages, metrics)")
            feedback.append("This helps demonstrate measurable impact")
        else:
            score = 0
            feedback.append("✗ No quantifiable achievements found")
            feedback.append("Add metrics and numbers to show impact (e.g., 'Increased sales by 25%')")
        
        self.breakdown['achievements'] = {
            'score': score,
            'max': max_score,
            'feedback': feedback,
        }
        
        return score
    
    def _score_length(self) -> int:
        """Score resume length optimization (5 points)."""
        max_score = self.WEIGHTS['length']
        feedback = []
        
        word_count = self.parser.count_words()
        
        # Optimal length: 400-800 words (1-2 pages)
        if 400 <= word_count <= 800:
            score = max_score
            feedback.append(f"✓ Optimal length ({word_count} words)")
        elif 300 <= word_count < 400:
            score = 3
            feedback.append(f"⚠ Slightly short ({word_count} words) - consider adding more details")
        elif 800 < word_count <= 1000:
            score = 3
            feedback.append(f"⚠ Slightly long ({word_count} words) - consider condensing")
        elif word_count < 300:
            score = 1
            feedback.append(f"✗ Too short ({word_count} words) - add more content")
        else:
            score = 1
            feedback.append(f"✗ Too long ({word_count} words) - condense to 1-2 pages")
        
        self.breakdown['length'] = {
            'score': score,
            'max': max_score,
            'feedback': feedback,
            'word_count': word_count,
        }
        
        return score
    
    def _get_grade(self, score: int) -> str:
        """Convert numerical score to letter grade."""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on scores."""
        recommendations = []
        
        # Contact info recommendations
        if self.breakdown['contact_info']['score'] < self.WEIGHTS['contact_info']:
            recommendations.append("Add missing contact information (email, phone, LinkedIn profile)")
        
        # Keywords recommendations
        if self.breakdown['keywords']['score'] < self.WEIGHTS['keywords'] * 0.8:
            recommendations.append("Include more industry-relevant keywords and technical skills")
            recommendations.append("Tailor keywords to match the job description")
        
        # Formatting recommendations
        if self.breakdown['formatting']['score'] < self.WEIGHTS['formatting'] * 0.7:
            recommendations.append("Improve resume structure with clear section headers (Experience, Education, Skills)")
            recommendations.append("Use consistent formatting throughout the document")
        
        # Experience recommendations
        if self.breakdown['experience']['score'] < self.WEIGHTS['experience'] * 0.7:
            recommendations.append("Start bullet points with strong action verbs (developed, managed, led, etc.)")
            recommendations.append("Include employment dates for all positions")
        
        # Achievements recommendations
        if self.breakdown['achievements']['score'] < self.WEIGHTS['achievements'] * 0.5:
            recommendations.append("Add quantifiable achievements with metrics (e.g., 'Increased revenue by 30%')")
            recommendations.append("Use numbers, percentages, and specific results to show impact")
        
        # Length recommendations
        if self.breakdown['length']['score'] < self.WEIGHTS['length'] * 0.6:
            word_count = self.breakdown['length']['word_count']
            if word_count < 400:
                recommendations.append("Expand resume content - add more details about your experience and achievements")
            else:
                recommendations.append("Condense resume to 1-2 pages by removing less relevant information")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Great job! Your resume is well-optimized for ATS systems")
            recommendations.append("Consider customizing for each job application")
        
        return recommendations

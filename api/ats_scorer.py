"""
ATS Resume Scoring Engine
Analyzes resumes against common ATS criteria and provides detailed scoring.
"""

import re
from typing import Optional


class ATSScorer:
    """
    Scores resumes against Applicant Tracking System (ATS) criteria.

    Evaluates multiple dimensions:
    - Contact Information completeness
    - Section Structure and organization
    - Keyword Optimization
    - Formatting Compatibility
    - Quantifiable Achievements
    - Action Verbs usage
    - Length and Readability
    - ATS-Friendly Formatting
    """

    # Common ATS action verbs
    ACTION_VERBS = {
        "achieved", "administered", "analyzed", "built", "collaborated",
        "conducted", "created", "decreased", "delivered", "designed",
        "developed", "directed", "drove", "engineered", "established",
        "evaluated", "executed", "expanded", "generated", "grew",
        "identified", "implemented", "improved", "increased", "initiated",
        "launched", "led", "managed", "mentored", "negotiated",
        "optimized", "orchestrated", "oversaw", "partnered", "pioneered",
        "planned", "produced", "reduced", "reorganized", "resolved",
        "revamped", "scaled", "secured", "simplified", "spearheaded",
        "streamlined", "strengthened", "supervised", "surpassed",
        "transformed", "upgraded", "utilized", "coordinated", "facilitated",
        "formulated", "influenced", "integrated", "maximized", "modernized",
        "motivated", "navigated", "outperformed", "persuaded", "presented",
        "prioritized", "proposed", "recruited", "restructured", "standardized",
        "supported", "trained", "translated", "troubleshot", "volunteered",
    }

    # Common industry keywords grouped by category
    INDUSTRY_KEYWORDS = {
        "technical": {
            "python", "java", "javascript", "typescript", "react", "angular",
            "vue", "node", "sql", "nosql", "aws", "azure", "gcp", "docker",
            "kubernetes", "ci/cd", "devops", "agile", "scrum", "api", "rest",
            "graphql", "microservices", "cloud", "machine learning", "ai",
            "data analysis", "database", "git", "linux", "html", "css",
            "tensorflow", "pytorch", "pandas", "numpy", "django", "flask",
            "spring", "mongodb", "postgresql", "mysql", "redis", "kafka",
            "elasticsearch", "terraform", "ansible", "jenkins", "github",
        },
        "soft_skills": {
            "leadership", "communication", "teamwork", "problem-solving",
            "critical thinking", "time management", "adaptability",
            "collaboration", "attention to detail", "project management",
            "strategic planning", "decision making", "interpersonal",
            "organizational", "analytical", "creative", "innovative",
            "self-motivated", "results-driven", "deadline-oriented",
        },
        "business": {
            "roi", "kpi", "stakeholder", "budget", "revenue", "profit",
            "strategy", "operations", "compliance", "risk management",
            "business development", "market analysis", "client relations",
            "vendor management", "supply chain", "process improvement",
            "quality assurance", "change management", "cross-functional",
        },
    }

    # Essential sections for a strong resume
    ESSENTIAL_SECTIONS = {"experience", "education", "skills"}
    RECOMMENDED_SECTIONS = {"summary", "certifications", "projects", "awards"}

    def __init__(self):
        pass

    def score(self, parsed_resume: dict, job_description: Optional[str] = None) -> dict:
        """
        Score a parsed resume against ATS criteria.

        Args:
            parsed_resume: Output from ResumeParser.parse()
            job_description: Optional job description for keyword matching.

        Returns:
            Detailed scoring report.
        """
        text = parsed_resume["text"]
        sections = parsed_resume["sections"]
        word_count = parsed_resume["word_count"]

        # Run all scoring checks
        contact_score = self._score_contact_info(text)
        section_score = self._score_sections(sections)
        keyword_score = self._score_keywords(text, job_description)
        formatting_score = self._score_formatting(text, parsed_resume["format"])
        achievement_score = self._score_achievements(text)
        action_verb_score = self._score_action_verbs(text)
        length_score = self._score_length(word_count)
        readability_score = self._score_readability(text)

        # Compute weighted overall score
        weights = {
            "contact_info": 0.10,
            "sections": 0.15,
            "keywords": 0.20,
            "formatting": 0.15,
            "achievements": 0.15,
            "action_verbs": 0.10,
            "length": 0.05,
            "readability": 0.10,
        }

        scores = {
            "contact_info": contact_score,
            "sections": section_score,
            "keywords": keyword_score,
            "formatting": formatting_score,
            "achievements": achievement_score,
            "action_verbs": action_verb_score,
            "length": length_score,
            "readability": readability_score,
        }

        overall = sum(
            scores[key]["score"] * weights[key] for key in weights
        )

        # Aggregate all suggestions
        all_suggestions = []
        all_warnings = []
        all_good = []

        for category in scores.values():
            all_suggestions.extend(category.get("suggestions", []))
            all_warnings.extend(category.get("warnings", []))
            all_good.extend(category.get("good", []))

        # Determine grade
        grade = self._get_grade(overall)

        return {
            "overall_score": round(overall, 1),
            "grade": grade,
            "category_scores": {
                key: {
                    "score": val["score"],
                    "weight": int(weights[key] * 100),
                    "label": val["label"],
                    "details": val.get("details", ""),
                    "suggestions": val.get("suggestions", []),
                    "warnings": val.get("warnings", []),
                    "good": val.get("good", []),
                }
                for key, val in scores.items()
            },
            "suggestions": all_suggestions,
            "warnings": all_warnings,
            "strengths": all_good,
            "summary": self._generate_summary(overall, all_suggestions, all_warnings, all_good),
            "word_count": word_count,
        }

    def _score_contact_info(self, text: str) -> dict:
        """Score the presence and completeness of contact information."""
        score = 0
        max_score = 100
        found = []
        missing = []
        suggestions = []
        warnings = []
        good = []

        # Email check
        email_pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
        if re.search(email_pattern, text):
            score += 25
            found.append("Email address")
            good.append("Email address found")
        else:
            missing.append("Email address")
            warnings.append("No email address detected - this is critical for ATS")

        # Phone number check
        phone_pattern = r"(\+?\d{1,3}[\s\-]?)?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}"
        if re.search(phone_pattern, text):
            score += 25
            found.append("Phone number")
            good.append("Phone number found")
        else:
            missing.append("Phone number")
            suggestions.append("Add a phone number to your resume")

        # LinkedIn check
        linkedin_pattern = r"(?i)linkedin\.com/in/|linkedin"
        if re.search(linkedin_pattern, text):
            score += 20
            found.append("LinkedIn profile")
            good.append("LinkedIn profile included")
        else:
            missing.append("LinkedIn profile")
            suggestions.append("Consider adding your LinkedIn profile URL")

        # Location check
        location_indicators = [
            r"(?i)\b\d{5}(?:\-\d{4})?\b",  # ZIP code
            r"(?i)\b(?:new york|los angeles|chicago|houston|phoenix|philadelphia|san antonio|san diego|dallas|san jose|austin|jacksonville|fort worth|columbus|charlotte|san francisco|indianapolis|seattle|denver|washington|nashville|oklahoma city|el paso|boston|portland|las vegas|memphis|louisville|baltimore|milwaukee|albuquerque|tucson|fresno|sacramento|mesa|kansas city|atlanta|omaha|colorado springs|raleigh|long beach|virginia beach|miami|oakland|minneapolis|tulsa|tampa|arlington|new orleans)\b",
            r"(?i)\b(?:remote|hybrid|on-?site)\b",
            r"(?i)\b[A-Z][a-z]+,\s*[A-Z]{2}\b",  # City, ST format
        ]
        location_found = False
        for pattern in location_indicators:
            if re.search(pattern, text):
                location_found = True
                break
        if location_found:
            score += 15
            found.append("Location")
            good.append("Location information included")
        else:
            missing.append("Location/City")
            suggestions.append("Include your city and state or indicate remote preference")

        # Name check (usually first line, with capitalized words)
        first_lines = text.strip().split("\n")[:3]
        name_found = False
        for line in first_lines:
            stripped = line.strip()
            if stripped and len(stripped.split()) <= 5:
                words = stripped.split()
                if all(w[0].isupper() for w in words if w.isalpha()):
                    name_found = True
                    break
        if name_found:
            score += 15
            found.append("Name")
            good.append("Name appears at the top of the resume")
        else:
            missing.append("Name (at top)")
            suggestions.append("Ensure your full name is prominently displayed at the top")

        return {
            "score": min(score, max_score),
            "label": "Contact Information",
            "details": f"Found: {', '.join(found) if found else 'None'}. Missing: {', '.join(missing) if missing else 'None'}.",
            "suggestions": suggestions,
            "warnings": warnings,
            "good": good,
        }

    def _score_sections(self, sections: dict) -> dict:
        """Score the presence and organization of resume sections."""
        score = 0
        suggestions = []
        warnings = []
        good = []
        found_essential = []
        found_recommended = []
        missing_essential = []
        missing_recommended = []

        # Essential sections (60 points)
        for section in self.ESSENTIAL_SECTIONS:
            if section in sections:
                score += 20
                found_essential.append(section.title())
                good.append(f"'{section.title()}' section present")
            else:
                missing_essential.append(section.title())
                warnings.append(f"Missing essential section: '{section.title()}'")

        # Recommended sections (40 points, 10 each, max 40)
        recommended_score = 0
        for section in self.RECOMMENDED_SECTIONS:
            if section in sections:
                recommended_score += 10
                found_recommended.append(section.title())
                good.append(f"'{section.title()}' section present")
            else:
                missing_recommended.append(section.title())

        score += min(recommended_score, 40)

        if missing_recommended:
            suggestions.append(
                f"Consider adding these sections: {', '.join(missing_recommended)}"
            )

        # Bonus: check section content length
        thin_sections = []
        for section_name, content in sections.items():
            if section_name == "header":
                continue
            word_count = len(content.split())
            if word_count < 10 and section_name in self.ESSENTIAL_SECTIONS:
                thin_sections.append(section_name.title())

        if thin_sections:
            suggestions.append(
                f"These sections seem thin and could use more detail: {', '.join(thin_sections)}"
            )

        return {
            "score": min(score, 100),
            "label": "Section Structure",
            "details": f"Essential: {', '.join(found_essential) or 'None'}. Recommended: {', '.join(found_recommended) or 'None'}.",
            "suggestions": suggestions,
            "warnings": warnings,
            "good": good,
        }

    def _score_keywords(self, text: str, job_description: Optional[str] = None) -> dict:
        """Score keyword optimization."""
        score = 0
        suggestions = []
        warnings = []
        good = []
        text_lower = text.lower()

        if job_description:
            # Score against job description keywords
            jd_words = set(re.findall(r"\b[a-z]{3,}\b", job_description.lower()))
            resume_words = set(re.findall(r"\b[a-z]{3,}\b", text_lower))

            # Filter out very common words
            stop_words = {
                "the", "and", "for", "are", "but", "not", "you", "all",
                "can", "had", "her", "was", "one", "our", "out", "has",
                "have", "been", "this", "that", "with", "they", "from",
                "will", "would", "could", "should", "their", "there",
                "what", "about", "which", "when", "make", "like", "just",
                "over", "such", "take", "also", "into", "than", "them",
                "very", "some", "more", "other", "these", "your",
            }
            jd_keywords = jd_words - stop_words
            matched = jd_keywords & resume_words
            match_rate = len(matched) / max(len(jd_keywords), 1) * 100

            score = min(match_rate, 100)

            if match_rate >= 70:
                good.append(f"Strong keyword match with job description ({match_rate:.0f}%)")
            elif match_rate >= 40:
                suggestions.append(
                    f"Moderate keyword match ({match_rate:.0f}%). Consider incorporating more keywords from the job description."
                )
            else:
                warnings.append(
                    f"Low keyword match ({match_rate:.0f}%). Your resume may not pass ATS keyword filters."
                )

            # Find important missing keywords
            missing_jd = jd_keywords - resume_words
            if missing_jd:
                top_missing = sorted(missing_jd)[:10]
                suggestions.append(
                    f"Missing job description keywords: {', '.join(top_missing)}"
                )
        else:
            # Generic keyword scoring based on industry keywords
            total_keywords_found = 0
            category_results = {}

            for category, keywords in self.INDUSTRY_KEYWORDS.items():
                found = set()
                for kw in keywords:
                    if kw.lower() in text_lower:
                        found.add(kw)
                category_results[category] = found
                total_keywords_found += len(found)

            # Score based on keyword density
            if total_keywords_found >= 15:
                score = 90
                good.append(f"Excellent keyword coverage ({total_keywords_found} industry keywords found)")
            elif total_keywords_found >= 10:
                score = 75
                good.append(f"Good keyword coverage ({total_keywords_found} industry keywords found)")
            elif total_keywords_found >= 5:
                score = 55
                suggestions.append(
                    f"Moderate keyword coverage ({total_keywords_found} keywords). Add more industry-specific terms."
                )
            elif total_keywords_found >= 1:
                score = 35
                warnings.append(
                    f"Low keyword count ({total_keywords_found}). ATS systems rely heavily on keyword matching."
                )
            else:
                score = 10
                warnings.append(
                    "Very few recognized industry keywords found. This may hurt ATS ranking."
                )

            # Check for skill-related keywords specifically
            if not category_results.get("technical") and not category_results.get("soft_skills"):
                suggestions.append(
                    "Include more technical skills and soft skills keywords relevant to your target role."
                )

            if category_results.get("technical"):
                good.append(
                    f"Technical keywords found: {', '.join(sorted(category_results['technical'])[:8])}"
                )

        return {
            "score": min(score, 100),
            "label": "Keyword Optimization",
            "details": f"Keyword analysis {'against job description' if job_description else 'using industry benchmarks'}.",
            "suggestions": suggestions,
            "warnings": warnings,
            "good": good,
        }

    def _score_formatting(self, text: str, file_format: str) -> dict:
        """Score ATS-compatibility of formatting."""
        score = 80  # Start high and deduct
        suggestions = []
        warnings = []
        good = []

        # Check for problematic characters
        special_chars = re.findall(r"[^\x00-\x7F]", text)
        if len(special_chars) > 10:
            score -= 15
            warnings.append(
                f"Found {len(special_chars)} non-ASCII characters. Some ATS systems may not parse these correctly."
            )
        elif len(special_chars) == 0:
            good.append("No problematic special characters detected")

        # Check for excessive use of symbols in headers
        fancy_bullets = re.findall(r"[■□●○►▸▪▫★☆✓✗✔✘➤➢⚡]", text)
        if fancy_bullets:
            score -= 10
            suggestions.append(
                "Replace fancy bullet characters with standard bullets (-, *, or •) for better ATS compatibility."
            )
        else:
            good.append("Standard formatting characters used")

        # Check for tables (DOCX indicator)
        table_indicators = re.findall(r"\t{2,}", text)
        if len(table_indicators) > 5:
            score -= 10
            warnings.append(
                "Possible table-based layout detected. Many ATS systems cannot parse tables correctly."
            )

        # Check for consistent date formatting
        date_formats = {
            "mm/yyyy": re.findall(r"\b\d{2}/\d{4}\b", text),
            "month year": re.findall(
                r"(?i)\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{4}\b",
                text,
            ),
            "yyyy": re.findall(r"(?<!\d)\b20\d{2}\b(?!\d)", text),
        }

        formats_used = {k: v for k, v in date_formats.items() if v}
        if len(formats_used) > 1:
            score -= 5
            suggestions.append(
                "Use a consistent date format throughout your resume (e.g., 'Month Year')."
            )
        elif formats_used:
            good.append("Date formatting appears consistent")

        # File format check
        if file_format == "PDF":
            score += 5
            good.append("PDF format is widely accepted by ATS systems")
        elif file_format == "DOCX":
            score += 10
            good.append("DOCX format is the most ATS-friendly format")

        # Check for headers/footers indicators (repeated patterns)
        lines = text.strip().split("\n")
        if len(lines) > 5:
            # Check if there are page number-like patterns
            page_nums = re.findall(r"(?i)page\s+\d+\s+of\s+\d+|\b\d+\s*/\s*\d+\b", text)
            if page_nums:
                suggestions.append(
                    "Consider removing page numbers - some ATS systems may misinterpret them."
                )

        # Check for URL formatting
        urls = re.findall(r"https?://\S+", text)
        if urls:
            good.append(f"{len(urls)} URL(s) found - ensure they are plain text links")

        score = max(score, 0)

        return {
            "score": min(score, 100),
            "label": "Formatting Compatibility",
            "details": f"Format: {file_format}. Analyzed for ATS parsing compatibility.",
            "suggestions": suggestions,
            "warnings": warnings,
            "good": good,
        }

    def _score_achievements(self, text: str) -> dict:
        """Score the presence of quantifiable achievements."""
        score = 0
        suggestions = []
        warnings = []
        good = []

        # Look for numbers and percentages (quantified results)
        percentages = re.findall(r"\d+(?:\.\d+)?%", text)
        dollar_amounts = re.findall(r"\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|M|B|K))?", text)
        numbers_with_context = re.findall(
            r"\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:\+\s*)?(?:users?|clients?|customers?|team\s*members?|people|employees?|projects?|years?|months?|companies|accounts?|transactions?|leads?|sales|orders?|tickets?|reports?|applications?)",
            text,
            re.IGNORECASE,
        )
        time_savings = re.findall(
            r"(?i)(?:reduced|decreased|saved|cut)\s+.*?\b\d+",
            text,
        )
        growth_metrics = re.findall(
            r"(?i)(?:increased|grew|improved|boosted|expanded|raised)\s+.*?\b\d+",
            text,
        )

        total_metrics = (
            len(percentages)
            + len(dollar_amounts)
            + len(numbers_with_context)
            + len(time_savings)
            + len(growth_metrics)
        )

        if total_metrics >= 8:
            score = 95
            good.append(f"Excellent use of quantified achievements ({total_metrics} metrics found)")
        elif total_metrics >= 5:
            score = 80
            good.append(f"Good use of metrics and numbers ({total_metrics} found)")
        elif total_metrics >= 3:
            score = 60
            suggestions.append(
                f"Found {total_metrics} quantified achievements. Aim for 5+ metrics to strengthen your resume."
            )
        elif total_metrics >= 1:
            score = 35
            suggestions.append(
                "Add more quantifiable achievements (e.g., 'Increased revenue by 25%', 'Managed a team of 12')."
            )
        else:
            score = 10
            warnings.append(
                "No quantifiable achievements detected. ATS-ranked resumes with metrics score significantly higher."
            )
            suggestions.append(
                "Add specific numbers, percentages, and metrics to demonstrate your impact."
            )

        if percentages:
            good.append(f"Percentage metrics found: {', '.join(percentages[:5])}")
        if dollar_amounts:
            good.append(f"Dollar amounts referenced: {', '.join(dollar_amounts[:3])}")

        return {
            "score": min(score, 100),
            "label": "Quantifiable Achievements",
            "details": f"Found {total_metrics} quantified achievement(s) across your resume.",
            "suggestions": suggestions,
            "warnings": warnings,
            "good": good,
        }

    def _score_action_verbs(self, text: str) -> dict:
        """Score the use of strong action verbs."""
        score = 0
        suggestions = []
        warnings = []
        good = []

        text_lower = text.lower()
        words = set(re.findall(r"\b[a-z]+\b", text_lower))
        found_verbs = words & self.ACTION_VERBS

        # Check for weak language
        weak_phrases = [
            "responsible for",
            "duties included",
            "helped with",
            "assisted with",
            "worked on",
            "was involved",
            "participated in",
            "tasked with",
        ]
        found_weak = [p for p in weak_phrases if p in text_lower]

        if len(found_verbs) >= 10:
            score = 90
            good.append(f"Excellent action verb usage ({len(found_verbs)} strong verbs found)")
        elif len(found_verbs) >= 6:
            score = 70
            good.append(f"Good action verb usage ({len(found_verbs)} found)")
        elif len(found_verbs) >= 3:
            score = 50
            suggestions.append(
                f"Found {len(found_verbs)} action verbs. Use more powerful verbs like: led, managed, developed, increased."
            )
        else:
            score = 20
            warnings.append(
                "Very few action verbs detected. Start bullet points with strong action verbs."
            )

        if found_weak:
            score = max(score - 15, 0)
            warnings.append(
                f"Weak phrases detected: '{', '.join(found_weak[:3])}'. Replace with action verbs."
            )

        if found_verbs:
            good.append(f"Action verbs used: {', '.join(sorted(found_verbs)[:8])}")

        return {
            "score": min(score, 100),
            "label": "Action Verbs",
            "details": f"Found {len(found_verbs)} strong action verb(s) and {len(found_weak)} weak phrase(s).",
            "suggestions": suggestions,
            "warnings": warnings,
            "good": good,
        }

    def _score_length(self, word_count: int) -> dict:
        """Score resume length appropriateness."""
        score = 0
        suggestions = []
        warnings = []
        good = []

        if 400 <= word_count <= 800:
            score = 95
            good.append(f"Resume length is ideal ({word_count} words) for a 1-page resume")
        elif 300 <= word_count < 400:
            score = 75
            suggestions.append(
                f"Resume is slightly short ({word_count} words). Consider adding more detail to your experience."
            )
        elif 800 < word_count <= 1200:
            score = 80
            good.append(f"Resume length ({word_count} words) is appropriate for 1-2 pages")
        elif 200 <= word_count < 300:
            score = 50
            warnings.append(
                f"Resume is too short ({word_count} words). Add more content to showcase your qualifications."
            )
        elif word_count > 1200:
            score = 60
            suggestions.append(
                f"Resume is long ({word_count} words). Consider trimming to focus on the most relevant experience."
            )
        elif word_count < 200:
            score = 20
            warnings.append(
                f"Resume is very short ({word_count} words). ATS systems may rank this poorly."
            )
        else:
            score = 40

        return {
            "score": min(score, 100),
            "label": "Resume Length",
            "details": f"Word count: {word_count}.",
            "suggestions": suggestions,
            "warnings": warnings,
            "good": good,
        }

    def _score_readability(self, text: str) -> dict:
        """Score readability and clarity."""
        score = 70
        suggestions = []
        warnings = []
        good = []

        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

            if avg_sentence_length <= 20:
                score += 15
                good.append(f"Good sentence length (avg {avg_sentence_length:.0f} words)")
            elif avg_sentence_length <= 30:
                score += 5
                suggestions.append(
                    f"Average sentence length is {avg_sentence_length:.0f} words. Aim for shorter, punchier sentences."
                )
            else:
                score -= 10
                warnings.append(
                    f"Sentences are too long (avg {avg_sentence_length:.0f} words). Break them into shorter statements."
                )

        # Check for bullet-point style (preferred by ATS)
        bullet_patterns = re.findall(r"^[\s]*[\-\*\•\►\▸]", text, re.MULTILINE)
        if len(bullet_patterns) >= 5:
            score += 10
            good.append(f"Good use of bullet points ({len(bullet_patterns)} found)")
        elif len(bullet_patterns) >= 2:
            score += 5
            suggestions.append("Use more bullet points to organize your experience")
        else:
            suggestions.append(
                "Add bullet points to list your responsibilities and achievements. ATS systems parse these well."
            )

        # Check for paragraph-heavy text
        long_paragraphs = [
            p for p in text.split("\n\n") if len(p.split()) > 50
        ]
        if long_paragraphs:
            score -= 10
            suggestions.append(
                "Break long paragraphs into bullet points for better ATS parsing and readability."
            )

        # Check for abbreviation consistency
        acronyms = re.findall(r"\b[A-Z]{2,5}\b", text)
        if acronyms:
            unique_acronyms = set(acronyms)
            if len(unique_acronyms) > 8:
                suggestions.append(
                    "Many acronyms used. Spell out abbreviations at least once for ATS clarity."
                )

        score = max(min(score, 100), 0)

        return {
            "score": score,
            "label": "Readability",
            "details": "Analyzed sentence structure, bullet usage, and paragraph formatting.",
            "suggestions": suggestions,
            "warnings": warnings,
            "good": good,
        }

    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        elif score >= 45:
            return "D+"
        elif score >= 40:
            return "D"
        else:
            return "F"

    def _generate_summary(
        self, score: float, suggestions: list, warnings: list, good: list
    ) -> str:
        """Generate a human-readable summary of the analysis."""
        if score >= 85:
            opener = "Excellent! Your resume is well-optimized for ATS systems."
        elif score >= 70:
            opener = "Good job! Your resume has solid ATS compatibility with room for improvement."
        elif score >= 55:
            opener = "Your resume has moderate ATS compatibility. Several improvements are recommended."
        elif score >= 40:
            opener = "Your resume needs significant improvements for better ATS performance."
        else:
            opener = "Your resume may struggle with ATS systems. Major revisions are recommended."

        parts = [opener]

        if warnings:
            parts.append(f"\n\nKey Issues ({len(warnings)}):")
            for w in warnings[:3]:
                parts.append(f"  - {w}")

        if suggestions:
            parts.append(f"\n\nTop Recommendations ({len(suggestions)}):")
            for s in suggestions[:5]:
                parts.append(f"  - {s}")

        if good:
            parts.append(f"\n\nStrengths ({len(good)}):")
            for g in good[:5]:
                parts.append(f"  + {g}")

        return "\n".join(parts)

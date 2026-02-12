import re
from collections import Counter
from typing import Dict, List, Optional, Tuple


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
    "will",
    "this",
    "your",
    "you",
    "our",
    "their",
    "they",
    "them",
    "i",
    "my",
    "me",
    "we",
    "us",
    "about",
    "into",
    "than",
    "then",
    "when",
    "where",
    "which",
    "who",
    "while",
    "not",
    "can",
    "should",
    "must",
    "required",
    "preferred",
}

DEFAULT_ROLE_KEYWORDS = [
    "python",
    "sql",
    "excel",
    "analytics",
    "data",
    "communication",
    "leadership",
    "project",
    "agile",
    "stakeholder",
    "automation",
    "testing",
    "documentation",
    "api",
    "cloud",
    "aws",
    "docker",
    "kubernetes",
    "javascript",
    "typescript",
]

SECTION_PATTERNS = {
    "summary": [r"\bsummary\b", r"\bobjective\b", r"\bprofile\b"],
    "experience": [r"\bexperience\b", r"\bemployment\b", r"\bwork history\b"],
    "education": [r"\beducation\b", r"\bacademic\b"],
    "skills": [r"\bskills\b", r"\btechnical skills\b", r"\bcore competencies\b"],
    "projects_or_certs": [r"\bprojects\b", r"\bcertification\b", r"\bcertifications\b"],
}

ACTION_VERBS = [
    "achieved",
    "analyzed",
    "built",
    "created",
    "delivered",
    "designed",
    "developed",
    "drove",
    "enhanced",
    "executed",
    "implemented",
    "improved",
    "increased",
    "launched",
    "led",
    "managed",
    "optimized",
    "orchestrated",
    "reduced",
    "resolved",
    "scaled",
    "streamlined",
]

WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}")


def _tokenize(text: str) -> List[str]:
    return [token.lower() for token in WORD_RE.findall(text)]


def _extract_keywords(text: str, max_keywords: int = 30) -> List[str]:
    tokens = [
        token
        for token in _tokenize(text)
        if token not in STOP_WORDS and len(token) > 2 and not token.isdigit()
    ]
    ranked = [token for token, _ in Counter(tokens).most_common(max_keywords)]
    return ranked


def _keyword_present(resume_text_lower: str, resume_tokens: set, keyword: str) -> bool:
    if " " in keyword:
        return keyword in resume_text_lower
    return keyword in resume_tokens


def _score_keyword_alignment(
    resume_text: str, job_description: Optional[str]
) -> Tuple[int, List[str], List[str], List[str]]:
    resume_text_lower = resume_text.lower()
    resume_tokens = set(_tokenize(resume_text))

    if job_description and job_description.strip():
        target_keywords = _extract_keywords(job_description, max_keywords=30)
    else:
        target_keywords = DEFAULT_ROLE_KEYWORDS.copy()

    if len(target_keywords) < 12:
        for keyword in DEFAULT_ROLE_KEYWORDS:
            if keyword not in target_keywords:
                target_keywords.append(keyword)
            if len(target_keywords) >= 20:
                break

    matched = [
        keyword
        for keyword in target_keywords
        if _keyword_present(resume_text_lower, resume_tokens, keyword)
    ]
    missing = [keyword for keyword in target_keywords if keyword not in matched]
    ratio = len(matched) / max(len(target_keywords), 1)
    score = int(round(ratio * 40))

    suggestions: List[str] = []
    if missing:
        focus = ", ".join(missing[:6])
        suggestions.append(f"Add missing role-specific keywords: {focus}.")
    if score < 20:
        suggestions.append(
            "Tailor your resume summary and skills section to mirror the job description wording."
        )

    return score, matched[:20], missing[:20], suggestions


def _score_sections(resume_text: str) -> Tuple[int, List[str]]:
    lower = resume_text.lower()
    present_sections = 0
    suggestions: List[str] = []

    for section_name, patterns in SECTION_PATTERNS.items():
        found = any(re.search(pattern, lower) for pattern in patterns)
        if found:
            present_sections += 1
            continue

        if section_name == "summary":
            suggestions.append("Add a short professional summary near the top.")
        elif section_name == "experience":
            suggestions.append("Include a clear work experience section with recent roles.")
        elif section_name == "education":
            suggestions.append("Add an education section with degree and institution.")
        elif section_name == "skills":
            suggestions.append("Add a dedicated technical/functional skills section.")
        else:
            suggestions.append("Include a projects or certifications section.")

    score = present_sections * 4
    return score, suggestions


def _score_readability(resume_text: str) -> Tuple[int, List[str]]:
    words = re.findall(r"\b\w+\b", resume_text)
    word_count = len(words)
    lines = [line for line in resume_text.splitlines() if line.strip()]
    bullet_lines = sum(
        1 for line in lines if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line)
    )
    sentence_parts = [part.strip() for part in re.split(r"[.!?]+", resume_text) if part.strip()]
    average_sentence_words = (
        sum(len(re.findall(r"\b\w+\b", sentence)) for sentence in sentence_parts)
        / max(len(sentence_parts), 1)
    )

    score = 0
    suggestions: List[str] = []

    if 250 <= word_count <= 900:
        score += 5
    elif 150 <= word_count <= 1200:
        score += 3
        suggestions.append("Aim for roughly 1-2 pages (about 250-900 words).")
    else:
        score += 1
        suggestions.append("Resume length is outside the ATS-friendly range (250-900 words).")

    if bullet_lines >= 5:
        score += 5
    elif bullet_lines >= 2:
        score += 3
        suggestions.append("Use more bullet points to improve scanability.")
    else:
        score += 1
        suggestions.append("Use bullet points for responsibilities and achievements.")

    if 8 <= average_sentence_words <= 22:
        score += 5
    elif 6 <= average_sentence_words <= 28:
        score += 3
        suggestions.append("Keep sentence length concise for ATS readability.")
    else:
        score += 1
        suggestions.append("Reduce long sentence blocks; keep content concise.")

    return score, suggestions


def _score_impact(resume_text: str) -> Tuple[int, List[str]]:
    lower = resume_text.lower()
    quantified_results = re.findall(r"(?:\$?\d+(?:\.\d+)?%?)", resume_text)
    action_verb_hits = re.findall(r"\b(" + "|".join(ACTION_VERBS) + r")\b", lower)

    score = 0
    suggestions: List[str] = []

    quantified_count = len(quantified_results)
    if quantified_count >= 6:
        score += 8
    elif quantified_count >= 3:
        score += 6
    elif quantified_count >= 1:
        score += 4
        suggestions.append("Add more measurable achievements (percentages, revenue, time saved).")
    else:
        score += 1
        suggestions.append("Quantify impact with numbers (%, $, or volume-based outcomes).")

    verb_count = len(action_verb_hits)
    if verb_count >= 10:
        score += 7
    elif verb_count >= 5:
        score += 5
    elif verb_count >= 2:
        score += 3
        suggestions.append("Start bullet points with stronger action verbs.")
    else:
        score += 1
        suggestions.append("Use action verbs (e.g., led, implemented, optimized) in bullets.")

    return min(score, 15), suggestions


def _score_contact_details(resume_text: str) -> Tuple[int, List[str]]:
    score = 0
    suggestions: List[str] = []

    has_email = bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text))
    has_phone = bool(re.search(r"\+?\d[\d()\-\s]{7,}\d", resume_text))
    lower = resume_text.lower()
    has_linkedin = "linkedin.com/in" in lower
    has_website = bool(re.search(r"https?://", lower))

    first_nonempty_line = next((line.strip() for line in resume_text.splitlines() if line.strip()), "")
    has_name_like_header = bool(
        re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$", first_nonempty_line)
    )

    if has_email:
        score += 4
    else:
        suggestions.append("Add a professional email address in the header.")

    if has_phone:
        score += 3
    else:
        suggestions.append("Include a reachable phone number.")

    if has_linkedin:
        score += 2
    elif has_website:
        score += 1
        suggestions.append("Add a complete LinkedIn profile URL (linkedin.com/in/...).")
    else:
        suggestions.append("Include LinkedIn (and optional portfolio/GitHub) links.")

    if has_name_like_header:
        score += 1
    else:
        suggestions.append("Start the resume with your full name as a clear header.")

    return min(score, 10), suggestions


def _verdict(score: int) -> str:
    if score >= 85:
        return "Excellent ATS alignment"
    if score >= 70:
        return "Strong ATS readiness"
    if score >= 55:
        return "Fair ATS readiness"
    return "Needs ATS optimization"


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        deduped.append(item)
        seen.add(item)
    return deduped


def review_resume_text(resume_text: str, job_description: Optional[str] = None) -> Dict:
    if not resume_text or len(resume_text.strip()) < 40:
        raise ValueError("Extracted resume text is too short to score.")

    keyword_score, matched_keywords, missing_keywords, keyword_suggestions = _score_keyword_alignment(
        resume_text, job_description
    )
    section_score, section_suggestions = _score_sections(resume_text)
    readability_score, readability_suggestions = _score_readability(resume_text)
    impact_score, impact_suggestions = _score_impact(resume_text)
    contact_score, contact_suggestions = _score_contact_details(resume_text)

    total_score = keyword_score + section_score + readability_score + impact_score + contact_score
    total_score = max(0, min(100, total_score))

    suggestions = _dedupe(
        keyword_suggestions
        + section_suggestions
        + readability_suggestions
        + impact_suggestions
        + contact_suggestions
    )

    if not suggestions:
        suggestions.append("Great structure overall. Keep tailoring keywords per role.")

    return {
        "score": total_score,
        "verdict": _verdict(total_score),
        "component_scores": {
            "keyword_alignment": keyword_score,
            "section_coverage": section_score,
            "readability": readability_score,
            "impact": impact_score,
            "contact_details": contact_score,
        },
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "suggestions": suggestions[:12],
        "text_length": len(resume_text),
    }


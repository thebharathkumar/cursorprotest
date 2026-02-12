"""
Resume Enhancer Service
Takes a parsed resume + ATS score report and produces an improved structured
context that the ResumeGenerator can render into a better-scoring PDF.
"""

import re
from typing import Optional


class ResumeEnhancer:
    """
    Transforms raw parsed resume data into an improved structured context
    by applying ATS best-practice fixes driven by the score report.
    """

    # Strong action verbs to inject when bullets start with weak language
    _STRONG_VERBS = [
        "Spearheaded", "Developed", "Implemented", "Engineered", "Optimized",
        "Streamlined", "Orchestrated", "Delivered", "Designed", "Led",
        "Managed", "Launched", "Transformed", "Reduced", "Increased",
        "Drove", "Pioneered", "Established", "Scaled", "Built",
    ]

    _WEAK_STARTS = [
        "responsible for", "duties included", "helped with", "assisted with",
        "worked on", "was involved", "participated in", "tasked with",
        "helped", "assisted", "involved in",
    ]

    def enhance(
        self,
        parsed_resume: dict,
        score_report: dict,
        job_description: Optional[str] = None,
    ) -> dict:
        """
        Build an improved resume context dict from parsed data + score feedback.

        Args:
            parsed_resume: output of ResumeParser.parse()
            score_report:  output of ATSScorer.score()
            job_description: optional JD text

        Returns:
            A context dict suitable for ResumeGenerator.generate()
        """
        text = parsed_resume["text"]
        sections = parsed_resume["sections"]

        # --- extract contact info from header / full text ---
        contact = self._extract_contact(text, sections)

        # --- professional summary ---
        summary = self._build_summary(sections, score_report, job_description)

        # --- experience ---
        experience = self._build_experience(sections, score_report, job_description)

        # --- education ---
        education = self._build_education(sections)

        # --- skills (enhanced with JD keywords) ---
        skills = self._build_skills(sections, text, score_report, job_description)

        # --- certifications ---
        certs = (sections.get("certifications") or "").strip()

        # --- projects ---
        projects = (sections.get("projects") or "").strip()

        return {
            "full_name": contact["name"],
            "email": contact["email"],
            "phone": contact["phone"],
            "location": contact["location"],
            "linkedin": contact["linkedin"],
            "summary": summary,
            "experience": experience,
            "education": education,
            "skills": skills,
            "certifications": certs,
            "projects": projects,
        }

    # ------------------------------------------------------------------
    #  Contact extraction
    # ------------------------------------------------------------------

    def _extract_contact(self, text: str, sections: dict) -> dict:
        header = sections.get("header", "") or ""
        full = header + "\n" + text[:500]  # look at top of resume

        email = ""
        m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", full)
        if m:
            email = m.group(0)

        phone = ""
        m = re.search(r"(\+?\d[\d\s\-\(\)]{7,}\d)", full)
        if m:
            phone = m.group(0).strip()

        linkedin = ""
        m = re.search(r"(?i)((?:https?://)?(?:www\.)?linkedin\.com/in/[^\s,|]+)", full)
        if m:
            linkedin = m.group(1)

        location = ""
        m = re.search(r"(?i)\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Z]{2})\b", full)
        if m:
            location = m.group(1)
        if not location:
            m = re.search(r"\b(\d{5}(?:-\d{4})?)\b", full)
            if m:
                location = m.group(1)

        # Name: first non-empty line of header that looks like a name
        name = ""
        for line in (header or text).split("\n"):
            s = line.strip()
            if not s or "@" in s:
                continue
            words = s.split()
            if 1 < len(words) <= 5 and all(w[0].isupper() for w in words if w.isalpha()):
                name = s
                break
        if not name:
            # fallback: first line
            for line in text.strip().split("\n"):
                s = line.strip()
                if s and len(s) < 60:
                    name = s
                    break

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "location": location,
            "linkedin": linkedin,
        }

    # ------------------------------------------------------------------
    #  Summary
    # ------------------------------------------------------------------

    def _build_summary(
        self, sections: dict, report: dict, jd: Optional[str]
    ) -> str:
        existing = (sections.get("summary") or "").strip()

        # If summary exists and is decent, keep it
        if existing and len(existing.split()) >= 10:
            return self._strengthen_text(existing, jd)

        # Synthesise a simple summary from experience keywords
        exp_text = sections.get("experience", "")
        skills_text = sections.get("skills", "")
        words = set(re.findall(r"\b[A-Za-z]{3,}\b", exp_text + " " + skills_text))
        top = sorted(words, key=lambda w: len(w), reverse=True)[:6]
        return (
            f"Results-driven professional with expertise in "
            f"{', '.join(top[:4])} and a track record of delivering impactful results."
        )

    # ------------------------------------------------------------------
    #  Experience
    # ------------------------------------------------------------------

    def _build_experience(
        self, sections: dict, report: dict, jd: Optional[str]
    ) -> list:
        raw = (sections.get("experience") or "").strip()
        if not raw:
            return []

        entries = self._parse_experience_text(raw)

        # Enhance each bullet
        for entry in entries:
            improved = []
            for bullet in entry["bullets"]:
                improved.append(self._improve_bullet(bullet, jd))
            entry["bullets"] = improved

        return entries

    def _parse_experience_text(self, text: str) -> list:
        """
        Heuristic parser: split experience section text into structured entries.
        Looks for lines that resemble "Title - Company" or "Title at Company"
        followed by date-like patterns, then collects bullets.
        """
        lines = text.split("\n")
        entries: list[dict] = []
        current: Optional[dict] = None

        date_re = re.compile(
            r"(?i)(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}"
            r"|(?:\d{1,2}/\d{4})"
            r"|(?:20\d{2})"
            r"|present|current",
        )

        title_re = re.compile(
            r"(?i)^(.+?)(?:\s+[-|@at]+\s+|\s+-\s+|\s+at\s+)(.+)$"
        )

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Does this line look like a role header?
            is_header = False
            dates_found = date_re.findall(stripped)
            title_match = title_re.match(stripped)

            # A line with dates and a title-company split
            if dates_found and (title_match or len(stripped.split()) <= 12):
                is_header = True
            # Or a short line that looks like a title (no bullet prefix)
            elif (
                not stripped.startswith(("-", "*", "\u2022"))
                and len(stripped.split()) <= 10
                and title_match
            ):
                is_header = True

            if is_header:
                # Save previous entry
                if current:
                    entries.append(current)

                # Parse title / company / dates
                title = stripped
                company = ""
                dates = ""

                if title_match:
                    title = title_match.group(1).strip()
                    company = title_match.group(2).strip()

                # Extract dates from the line
                if dates_found:
                    date_str = " - ".join(dates_found[:2])
                    dates = date_str
                    # Clean dates from title/company
                    for d in dates_found:
                        title = title.replace(d, "").strip(" -|,")
                        company = company.replace(d, "").strip(" -|,")

                current = {
                    "title": title.strip(" -|,()"),
                    "company": company.strip(" -|,()"),
                    "dates": dates,
                    "bullets": [],
                }
            else:
                # It's a bullet/content line
                if current is None:
                    current = {"title": "", "company": "", "dates": "", "bullets": []}
                cleaned = stripped.lstrip("-*\u2022\u25cf ").strip()
                if cleaned:
                    current["bullets"].append(cleaned)

        if current:
            entries.append(current)

        # If we failed to parse any structured entries, create one blob
        if not entries and text.strip():
            bullets = [
                l.strip().lstrip("-*\u2022 ").strip()
                for l in text.strip().split("\n")
                if l.strip()
            ]
            entries.append({
                "title": "",
                "company": "",
                "dates": "",
                "bullets": bullets,
            })

        return entries

    def _improve_bullet(self, bullet: str, jd: Optional[str]) -> str:
        """Strengthen a single bullet point for ATS."""
        b = bullet.strip()

        # Replace weak starts with stronger verbs
        lower = b.lower()
        for weak in self._WEAK_STARTS:
            if lower.startswith(weak):
                rest = b[len(weak):].strip().lstrip(",: ")
                if rest:
                    # Pick a contextual verb
                    verb = self._pick_verb(rest)
                    b = f"{verb} {rest[0].lower()}{rest[1:]}" if rest else b
                break

        # Ensure starts with a capital letter
        if b and b[0].islower():
            b = b[0].upper() + b[1:]

        return b

    def _pick_verb(self, context: str) -> str:
        """Pick a strong action verb that roughly fits the context."""
        ctx = context.lower()
        if any(w in ctx for w in ("team", "engineer", "report", "junior", "staff")):
            return "Led"
        if any(w in ctx for w in ("cost", "time", "reduc", "efficien", "optim")):
            return "Optimized"
        if any(w in ctx for w in ("system", "platform", "service", "application", "tool")):
            return "Developed"
        if any(w in ctx for w in ("process", "workflow", "pipeline")):
            return "Streamlined"
        if any(w in ctx for w in ("launch", "releas", "deploy", "ship")):
            return "Launched"
        if any(w in ctx for w in ("revenue", "growth", "sales", "metric")):
            return "Drove"
        if any(w in ctx for w in ("design", "architect", "plan")):
            return "Designed"
        return "Delivered"

    # ------------------------------------------------------------------
    #  Education
    # ------------------------------------------------------------------

    def _build_education(self, sections: dict) -> list:
        raw = (sections.get("education") or "").strip()
        if not raw:
            return []

        entries = []
        lines = raw.split("\n")
        for line in lines:
            s = line.strip()
            if not s:
                continue
            # Try to split degree / school / dates
            degree = s
            school = ""
            dates = ""

            # Extract dates
            dm = re.findall(
                r"(?i)(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+)?\d{4}",
                s,
            )
            if dm:
                dates = " - ".join(dm[:2])
                for d in dm:
                    degree = degree.replace(d, "").strip(" -|,")

            # Split degree/school on common delimiters
            for sep in [" - ", " | ", ", ", " at "]:
                if sep in degree:
                    parts = degree.split(sep, 1)
                    degree = parts[0].strip()
                    school = parts[1].strip()
                    break

            if degree or school:
                entries.append({
                    "degree": degree.strip(" -,"),
                    "school": school.strip(" -,"),
                    "dates": dates,
                })

        return entries

    # ------------------------------------------------------------------
    #  Skills
    # ------------------------------------------------------------------

    def _build_skills(
        self, sections: dict, full_text: str, report: dict, jd: Optional[str]
    ) -> str:
        existing = (sections.get("skills") or "").strip()

        # Collect all skill-like tokens already present
        skill_items = [
            s.strip()
            for s in re.split(r"[,;|\n]", existing)
            if s.strip() and len(s.strip()) < 40
        ]

        # If JD provided, find JD keywords missing from skills and add them
        if jd:
            jd_lower = jd.lower()
            existing_lower = " ".join(skill_items).lower() + " " + full_text.lower()

            tech_kw = {
                "python", "java", "javascript", "typescript", "react", "angular",
                "vue", "node.js", "sql", "aws", "azure", "gcp", "docker",
                "kubernetes", "ci/cd", "devops", "agile", "scrum", "rest",
                "graphql", "microservices", "git", "linux", "html", "css",
                "mongodb", "postgresql", "mysql", "redis", "kafka", "terraform",
                "jenkins", "flask", "django", "spring", "machine learning",
            }
            for kw in tech_kw:
                if kw in jd_lower and kw not in existing_lower:
                    skill_items.append(kw.title() if len(kw) > 3 else kw.upper())

        # Deduplicate (case-insensitive)
        seen = set()
        deduped = []
        for s in skill_items:
            key = s.lower()
            if key not in seen:
                seen.add(key)
                deduped.append(s)

        return ", ".join(deduped) if deduped else existing

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------

    def _strengthen_text(self, text: str, jd: Optional[str]) -> str:
        """Light cleanup of summary/objective text."""
        # Remove trailing periods if they look like fragments
        text = text.strip()
        # Ensure it ends with a period
        if text and text[-1] not in ".!":
            text += "."
        return text

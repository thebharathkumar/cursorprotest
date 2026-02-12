"""
Resume PDF Generator Service
Generates a clean, ATS-friendly one-page PDF resume tailored to a job description.
"""

import io
import re
import textwrap
from typing import Optional

from fpdf import FPDF


class ResumePDF(FPDF):
    """Custom FPDF subclass for resume generation."""

    def __init__(self):
        super().__init__(format="letter")
        self.set_auto_page_break(auto=True, margin=12)

    def _section_line(self):
        """Draw a thin horizontal rule under a section heading."""
        self.set_draw_color(80, 80, 80)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)


class ResumeGenerator:
    """
    Generates a tailored one-page PDF resume.

    Accepts structured user context and a job description, then produces
    a professional, ATS-compatible PDF.
    """

    # Unicode -> ASCII replacements for PDF-safe text
    _UNICODE_MAP = {
        "\u2014": " - ",   # em dash
        "\u2013": " - ",   # en dash
        "\u2018": "'",     # left single quote
        "\u2019": "'",     # right single quote
        "\u201c": '"',     # left double quote
        "\u201d": '"',     # right double quote
        "\u2026": "...",   # ellipsis
        "\u2022": "-",     # bullet
        "\u2023": "-",     # triangle bullet
        "\u25cf": "-",     # black circle
        "\u25cb": "-",     # white circle
        "\u2192": "->",    # right arrow
        "\u2190": "<-",    # left arrow
        "\u00a0": " ",     # non-breaking space
        "\u200b": "",      # zero-width space
    }

    @staticmethod
    def _sanitize(text: str) -> str:
        """Replace Unicode characters that Helvetica can't render."""
        for uc, repl in ResumeGenerator._UNICODE_MAP.items():
            text = text.replace(uc, repl)
        # Strip any remaining non-latin-1 characters
        return text.encode("latin-1", errors="replace").decode("latin-1")

    # ---- public API ----

    def generate(self, context: dict, job_description: str) -> bytes:
        """
        Generate a one-page PDF resume.

        Args:
            context: dict with keys —
                full_name, email, phone, location, linkedin (all str, optional)
                summary       (str)  – career summary / objective
                experience    (list) – each item: {title, company, dates, bullets: [str]}
                education     (list) – each item: {degree, school, dates}
                skills        (str)  – comma-separated skill list
                certifications (str) – optional
                projects       (str) – optional
            job_description: the target job posting text.

        Returns:
            Raw PDF bytes.
        """
        jd_keywords = self._extract_jd_keywords(job_description)
        pdf = ResumePDF()
        pdf.add_page()

        # ---- Margins / font base ----
        pdf.set_left_margin(14)
        pdf.set_right_margin(14)
        pdf.set_y(12)
        usable = pdf.w - pdf.l_margin - pdf.r_margin

        # ---- Header (name + contact) ----
        name = self._sanitize((context.get("full_name") or "Your Name").strip())
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(usable, 8, name, ln=True, align="C")

        contact_parts = self._sanitize(self._build_contact_line(context))
        if contact_parts:
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(usable, 4.5, contact_parts, ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

        # ---- Professional Summary ----
        summary = self._sanitize((context.get("summary") or "").strip())
        if summary:
            summary = self._tailor_summary(summary, jd_keywords)
            self._section_heading(pdf, "PROFESSIONAL SUMMARY", usable)
            pdf.set_font("Helvetica", "", 9)
            for line in self._wrap(summary, 105):
                pdf.cell(usable, 4.2, line, ln=True)
            pdf.ln(2)

        # ---- Experience ----
        experience = context.get("experience") or []
        if experience:
            self._section_heading(pdf, "EXPERIENCE", usable)
            for i, exp in enumerate(experience):
                if pdf.get_y() > 255:
                    break  # keep to one page
                self._render_experience(pdf, exp, usable, jd_keywords)
                if i < len(experience) - 1:
                    pdf.ln(1.5)

        # ---- Education ----
        education = context.get("education") or []
        if education:
            self._section_heading(pdf, "EDUCATION", usable)
            for edu in education:
                if pdf.get_y() > 265:
                    break
                self._render_education(pdf, edu, usable)

        # ---- Skills ----
        skills = self._sanitize((context.get("skills") or "").strip())
        if skills:
            skills = self._tailor_skills(skills, jd_keywords)
            self._section_heading(pdf, "SKILLS", usable)
            pdf.set_font("Helvetica", "", 9)
            for line in self._wrap(skills, 110):
                pdf.cell(usable, 4.2, line, ln=True)
            pdf.ln(2)

        # ---- Certifications (optional) ----
        certs = self._sanitize((context.get("certifications") or "").strip())
        if certs and pdf.get_y() < 260:
            self._section_heading(pdf, "CERTIFICATIONS", usable)
            pdf.set_font("Helvetica", "", 9)
            for line in self._wrap(certs, 110):
                pdf.cell(usable, 4.2, line, ln=True)
            pdf.ln(2)

        # ---- Projects (optional) ----
        projects = self._sanitize((context.get("projects") or "").strip())
        if projects and pdf.get_y() < 260:
            self._section_heading(pdf, "PROJECTS", usable)
            pdf.set_font("Helvetica", "", 9)
            for line in self._wrap(projects, 110):
                pdf.cell(usable, 4.2, line, ln=True)
            pdf.ln(2)

        # ---- Output ----
        buf = io.BytesIO()
        pdf.output(buf)
        return buf.getvalue()

    # ---- internal helpers ----

    def _build_contact_line(self, ctx: dict) -> str:
        parts = []
        for key in ("email", "phone", "location", "linkedin"):
            val = (ctx.get(key) or "").strip()
            if val:
                parts.append(val)
        return "  |  ".join(parts)

    def _section_heading(self, pdf: ResumePDF, title: str, usable: float):
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(usable, 5.5, title, ln=True)
        pdf._section_line()
        pdf.set_text_color(0, 0, 0)

    def _render_experience(self, pdf: ResumePDF, exp: dict, usable: float, jd_kw: set):
        title = self._sanitize((exp.get("title") or "").strip())
        company = self._sanitize((exp.get("company") or "").strip())
        dates = self._sanitize((exp.get("dates") or "").strip())

        # Title | Company         Dates (right-aligned)
        pdf.set_font("Helvetica", "B", 9.5)
        left_text = title
        if company:
            left_text += f"  -  {company}"
        left_w = pdf.get_string_width(left_text)

        pdf.set_font("Helvetica", "", 8.5)
        date_w = pdf.get_string_width(dates)

        pdf.set_font("Helvetica", "B", 9.5)
        pdf.cell(usable - date_w - 2, 4.5, left_text)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(date_w + 2, 4.5, dates, ln=True, align="R")
        pdf.set_text_color(0, 0, 0)

        bullets = exp.get("bullets") or []
        pdf.set_font("Helvetica", "", 9)
        for bullet in bullets:
            if pdf.get_y() > 262:
                break
            bullet = self._sanitize(bullet.strip().lstrip("-*").strip())
            if not bullet:
                continue
            text = f"  -  {bullet}"
            for line in self._wrap(text, 103):
                pdf.cell(usable, 4.2, line, ln=True)

    def _render_education(self, pdf: ResumePDF, edu: dict, usable: float):
        degree = self._sanitize((edu.get("degree") or "").strip())
        school = self._sanitize((edu.get("school") or "").strip())
        dates = self._sanitize((edu.get("dates") or "").strip())

        pdf.set_font("Helvetica", "B", 9.5)
        left = degree
        if school:
            left += f"  -  {school}"
        left_w = pdf.get_string_width(left)

        pdf.set_font("Helvetica", "", 8.5)
        date_w = pdf.get_string_width(dates)

        pdf.set_font("Helvetica", "B", 9.5)
        pdf.cell(usable - date_w - 2, 4.5, left)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(date_w + 2, 4.5, dates, ln=True, align="R")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)

    # ---- keyword / tailoring helpers ----

    def _extract_jd_keywords(self, jd: str) -> set:
        """Pull meaningful keywords from a job description."""
        stop = {
            "the", "and", "for", "are", "but", "not", "you", "all", "can",
            "had", "her", "was", "one", "our", "out", "has", "have", "been",
            "this", "that", "with", "they", "from", "will", "would", "could",
            "should", "their", "there", "what", "about", "which", "when",
            "make", "like", "just", "over", "such", "take", "also", "into",
            "than", "them", "very", "some", "more", "other", "these", "your",
            "must", "able", "well", "work", "role", "join", "team", "etc",
            "who", "how", "may", "its", "use", "new", "way", "any", "each",
            "including", "strong", "looking", "ideal", "candidate", "required",
            "preferred", "qualifications", "responsibilities", "requirements",
            "experience", "years", "year", "plus", "minimum", "knowledge",
        }
        words = set(re.findall(r"\b[a-z][a-z\+\#\.]{1,}\b", jd.lower()))
        # Also grab multi-word terms
        bigrams = set(re.findall(r"\b[a-z]+[\s\-][a-z]+\b", jd.lower()))
        return (words | bigrams) - stop

    def _tailor_summary(self, summary: str, jd_kw: set) -> str:
        """Return summary as-is (user-written); future: inject missing JD terms."""
        return summary

    def _tailor_skills(self, skills: str, jd_kw: set) -> str:
        """
        Re-order skills so that JD-matching ones appear first.
        """
        items = [s.strip() for s in re.split(r"[,;|]", skills) if s.strip()]
        matched = []
        rest = []
        for s in items:
            if s.lower() in jd_kw or any(kw in s.lower() for kw in jd_kw if len(kw) > 3):
                matched.append(s)
            else:
                rest.append(s)
        reordered = matched + rest
        return ", ".join(reordered)

    def _wrap(self, text: str, width: int = 105) -> list[str]:
        """Word-wrap a string to fit the PDF line width."""
        lines = textwrap.wrap(text, width=width)
        return lines if lines else [""]

from ats_agent.scorer import review_resume_text


def test_review_resume_text_returns_component_breakdown():
    resume = """
    Jane Doe
    jane.doe@email.com | +1 555 123 4567 | https://linkedin.com/in/janedoe

    Summary
    Data analyst with 5 years of experience building analytics pipelines.

    Experience
    - Developed Python ETL pipelines that reduced reporting time by 40%.
    - Implemented SQL dashboards used by 50+ stakeholders.
    - Optimized data quality checks and improved accuracy by 25%.

    Skills
    Python, SQL, API, Tableau, Excel, Communication, Automation

    Education
    B.S. in Computer Science

    Projects
    - Built a cloud-based analytics API in AWS.
    """
    job_description = """
    Looking for a data analyst with Python, SQL, Excel, analytics, communication,
    stakeholder management, API development, cloud experience, and automation.
    """

    result = review_resume_text(resume, job_description)

    assert 0 <= result["score"] <= 100
    assert "component_scores" in result
    assert result["component_scores"]["keyword_alignment"] > 0
    assert "python" in result["matched_keywords"]
    assert isinstance(result["suggestions"], list)


def test_review_resume_text_rejects_too_short_content():
    try:
        review_resume_text("Short text")
    except ValueError as exc:
        assert "too short" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for too-short resume text")


from fastapi.testclient import TestClient

from ats_agent.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_review_resume_with_text_upload():
    resume = """
    John Smith
    john.smith@email.com | +1 (555) 111-2222 | https://linkedin.com/in/johnsmith

    Summary
    Software engineer with strong Python and cloud experience.

    Experience
    - Built API services in Python and improved latency by 35%.
    - Implemented automation for testing and deployment pipelines.

    Skills
    Python, SQL, API, Docker, AWS, Communication

    Education
    B.Tech in Information Technology
    """
    job_description = "Need Python, SQL, API, automation, communication, and cloud expertise."

    response = client.post(
        "/review-resume",
        files={"file": ("resume.txt", resume.encode("utf-8"), "text/plain")},
        data={"job_description": job_description},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"] == "resume.txt"
    assert 0 <= payload["score"] <= 100
    assert "component_scores" in payload
    assert "keyword_alignment" in payload["component_scores"]


def test_review_resume_rejects_unsupported_file_type():
    response = client.post(
        "/review-resume",
        files={"file": ("resume.png", b"binary-content", "image/png")},
    )
    assert response.status_code == 415
    assert "unsupported file type" in response.json()["detail"].lower()


def test_review_resume_rejects_empty_file():
    response = client.post(
        "/review-resume",
        files={"file": ("resume.txt", b"", "text/plain")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


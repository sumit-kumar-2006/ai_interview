import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models import User, Interview, QuestionResult
from backend.app.auth import create_access_token, get_password_hash
import uuid

client = TestClient(app)

@pytest.fixture
def test_users():
    db = SessionLocal()
    # Create User A
    email_a = f"user_a_{uuid.uuid4().hex[:6]}@example.com"
    user_a = User(email=email_a, hashed_password=get_password_hash("password123"), full_name="User A")
    db.add(user_a)
    
    # Create User B
    email_b = f"user_b_{uuid.uuid4().hex[:6]}@example.com"
    user_b = User(email=email_b, hashed_password=get_password_hash("password123"), full_name="User B")
    db.add(user_b)
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)
    
    token_a = create_access_token({"sub": str(user_a.id)})
    token_b = create_access_token({"sub": str(user_b.id)})
    
    yield {
        "user_a": user_a,
        "token_a": token_a,
        "user_b": user_b,
        "token_b": token_b
    }
    
    # Teardown: delete child records before parent users to satisfy FK constraints
    try:
        user_ids = [user_a.id, user_b.id]
        interview_rows = db.query(Interview.id).filter(Interview.user_id.in_(user_ids)).all()
        int_ids = [r[0] for r in interview_rows]
        if int_ids:
            db.query(QuestionResult).filter(QuestionResult.interview_id.in_(int_ids)).delete(synchronize_session=False)
        db.query(Interview).filter(Interview.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

def test_evaluate_answer_endpoint_accurate_scoring():
    """Verify POST /evaluate-answer evaluates answer against rubrics and returns structured feedback."""
    spec = {
        "expected_answer": "REST APIs follow architectural principles like statelessness and standard HTTP methods like GET, POST, PUT, DELETE.",
        "required_concepts": ["stateless", "http methods", "get post"],
        "optional_concepts": ["idempotent", "uniform interface"],
        "acceptable_alternatives": ["Representational State Transfer"],
        "common_misconceptions": ["REST requires SOAP", "GET modifies server state"],
        "rubric": {"statelessness": 50, "methods": 50}
    }
    
    payload = {
        "question": "What are the core principles and HTTP methods of a RESTful API?",
        "candidate_answer": "REST APIs are stateless client-server systems that utilize standard HTTP verbs like GET for reading and POST for writing.",
        "reference_answer": spec["expected_answer"],
        "evaluation_spec": spec,
        "attempt_number": 1
    }
    
    res = client.post("/evaluate-answer", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["final_score"] >= 75.0
    assert len(data["correct_concepts"]) >= 1
    assert "explanation" in data
    assert "relevance_score" in data
    assert "attempt_number" in data

def test_retry_and_transcript_editing_workflow():
    """Verify candidate can edit transcript to fix speech misrecognition and submit edited version."""
    spec = {
        "expected_answer": "PostgreSQL uses Multi-Version Concurrency Control (MVCC) to ensure read consistency.",
        "required_concepts": ["mvcc", "multi-version concurrency control", "read consistency"],
        "rubric": {"mvcc_concept": 60, "consistency": 40}
    }
    
    # 1. Candidate's draft had a typo: "NVC" instead of "MVCC"
    raw_draft = "PostgreSQL utilizes NVC for database consistency."
    
    # 2. Candidate used Edit Transcript to fix technical acronym
    edited_answer = "PostgreSQL utilizes MVCC (Multi-Version Concurrency Control) for read consistency without locking."
    
    payload = {
        "question": "How does PostgreSQL handle concurrency without locking tables?",
        "candidate_answer": edited_answer,
        "reference_answer": spec["expected_answer"],
        "evaluation_spec": spec,
        "attempt_number": 2  # Second attempt after re-recording/editing
    }
    
    res = client.post("/evaluate-answer", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["final_score"] >= 80.0
    assert "mvcc" in " ".join(data["correct_concepts"]).lower()
    assert data["attempt_number"] == 2

def test_jwt_authorization_and_ownership_isolation(test_users):
    """Ensure User B cannot view or delete interviews owned by User A."""
    token_a = test_users["token_a"]
    token_b = test_users["token_b"]
    
    # User A creates an interview
    interview_payload = {
        "target_role": "Python Engineer",
        "overall_score": 88.5,
        "duration_seconds": 180,
        "questions_answered": 1,
        "questions_skipped": 0,
        "question_results": [
            {
                "question_number": 1,
                "question": "What is polymorphism?",
                "transcript": "Polymorphism allows different objects to share the same interface.",
                "final_score": 88.5,
                "relevance_score": 90.0,
                "concept_coverage": 85.0,
                "correct_concepts": ["interface", "different objects"],
                "missing_concepts": [],
                "attempt_count": 1
            }
        ]
    }
    
    create_res = client.post(
        "/interviews",
        headers={"Authorization": f"Bearer {token_a}"},
        json=interview_payload
    )
    assert create_res.status_code == 201
    created_id = create_res.json()["id"]
    
    # User A can retrieve interview
    get_res_a = client.get(
        f"/interviews/{created_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert get_res_a.status_code == 200
    assert get_res_a.json()["id"] == created_id
    
    # User B attempting to view User A's interview receives 404
    get_res_b = client.get(
        f"/interviews/{created_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert get_res_b.status_code == 404
    
    # User B attempting to delete User A's interview receives 404
    del_res_b = client.delete(
        f"/interviews/{created_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert del_res_b.status_code == 404
    
    # Report endpoint is also isolated
    rep_res_b = client.get(
        f"/interviews/{created_id}/report",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert rep_res_b.status_code == 404

def test_mysql_persistence_and_pdf_report(test_users):
    """Verify saved interview generates consistent structured report and PDF binary."""
    token_a = test_users["token_a"]
    
    interview_payload = {
        "target_role": "Cybersecurity Specialist",
        "overall_score": 85.0,
        "duration_seconds": 120,
        "questions_answered": 1,
        "questions_skipped": 0,
        "question_results": [
            {
                "question_number": 1,
                "question": "What is SQL Injection and how do you prevent it?",
                "transcript": "SQL injection occurs when untrusted input alters database queries. Prevent it using parameterized queries and prepared statements.",
                "final_score": 85.0,
                "relevance_score": 88.0,
                "concept_coverage": 85.0,
                "correct_concepts": ["parameterized queries", "prepared statements"],
                "missing_concepts": [],
                "ai_feedback": "Solid understanding of parameterized query prevention.",
                "attempt_count": 1
            }
        ]
    }
    
    create_res = client.post(
        "/interviews",
        headers={"Authorization": f"Bearer {token_a}"},
        json=interview_payload
    )
    assert create_res.status_code == 201
    created_id = create_res.json()["id"]
    
    # Check structured report
    report_res = client.get(
        f"/interviews/{created_id}/report",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert report_res.status_code == 200
    report = report_res.json()["report"]
    assert report["candidate"]["target_role"] == "Cybersecurity Specialist"
    assert len(report["question_wise_analysis"]) == 1
    assert report["question_wise_analysis"][0]["score"] == 85.0
    assert "parameterized queries" in report["question_wise_analysis"][0]["correct_concepts"]
    
    # Check PDF generation
    pdf_res = client.get(
        f"/interviews/{created_id}/pdf",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF")

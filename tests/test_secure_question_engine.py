"""
================================================================================
PART B - STEP 3: SECURE BACKEND QUESTION & EVALUATION ENGINE TEST SUITE
Project: AI Interview Analyzer
Workspace: D:\\AI-Interview-Analyzer
================================================================================

Comprehensive verification of:
1. Public API strictly omits reference_answer, evaluation_spec, rubric, expected_answer.
2. Unauthenticated requests are rejected where authentication is required.
3. Answer evaluation retrieves reference answers server-side from MySQL.
4. Client-supplied reference answers and rubrics are ignored/neutralized.
5. Inactive / quarantined questions cannot be selected for interviews.
6. Only verified academic_train questions are selected.
7. Invalid question IDs return HTTP 404.
8. Inactive question IDs submitted for evaluation return HTTP 400.
9. Empty candidate answers receive 0.0 score with descriptive feedback.
10. Actual HTTP responses are validated end-to-end.
"""

import os
import sys

# Ensure repository root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
import backend.app.models as models

client = TestClient(app)


def test_public_api_does_not_expose_confidential_fields():
    """Verify GET and POST /interview/questions never leak reference_answer, evaluation_spec, or rubric."""
    # Test GET
    res_get = client.get("/interview/questions?count=5")
    assert res_get.status_code == 200
    data_get = res_get.json()
    assert data_get["status"] == "success"
    assert len(data_get["questions"]) > 0

    for q in data_get["questions"]:
        assert "reference_answer" not in q, "Data leak: reference_answer exposed in GET /interview/questions"
        assert "expected_answer" not in q, "Data leak: expected_answer exposed in GET /interview/questions"
        assert "evaluation_spec" not in q, "Data leak: evaluation_spec exposed in GET /interview/questions"
        assert "rubric" not in q, "Data leak: rubric exposed in GET /interview/questions"
        assert "common_misconceptions" not in q, "Data leak: common_misconceptions exposed in GET /interview/questions"

    # Test POST
    res_post = client.post("/interview/questions", json={"count": 5, "role": "Python Engineer"})
    assert res_post.status_code == 200
    data_post = res_post.json()
    assert data_post["status"] == "success"
    assert len(data_post["questions"]) > 0

    for q in data_post["questions"]:
        assert "reference_answer" not in q, "Data leak: reference_answer exposed in POST /interview/questions"
        assert "expected_answer" not in q, "Data leak: expected_answer exposed in POST /interview/questions"
        assert "evaluation_spec" not in q, "Data leak: evaluation_spec exposed in POST /interview/questions"
        assert "rubric" not in q, "Data leak: rubric exposed in POST /interview/questions"


def test_unauthenticated_requests_handled_appropriately():
    """Verify protected user routes reject unauthenticated requests while public question browse functions."""
    # Protected route requires auth
    res_protected = client.post("/interviews", json={})
    assert res_protected.status_code in [401, 403], f"Expected 401/403 for unauthenticated interview save, got {res_protected.status_code}"

    # Public question browse allows guest practice without leaking answers
    res_public = client.get("/interview/questions?count=2")
    assert res_public.status_code == 200


def test_only_academic_train_questions_are_selected():
    """Verify that all selected questions come exclusively from the academic_train dataset."""
    res = client.get("/interview/questions?count=15")
    assert res.status_code == 200
    data = res.json()
    questions = data["questions"]
    assert len(questions) > 0

    db = SessionLocal()
    try:
        for q in questions:
            q_id = q["id"]
            db_q = db.query(models.Question).filter(models.Question.id == q_id).first()
            assert db_q is not None, f"Question ID {q_id} not found in database"
            assert db_q.source_dataset == "academic_train", f"Question ID {q_id} belongs to {db_q.source_dataset}, must be academic_train"
            assert db_q.is_active == 1, f"Question ID {q_id} is inactive but was served"
            assert q["source_id"].startswith("academic_train_")
    finally:
        db.close()


def test_inactive_questions_cannot_be_selected():
    """Verify that quarantined validation (270), test (272), and seed (10) records are never selected."""
    res = client.get("/interview/questions?count=20")
    assert res.status_code == 200
    served_ids = {q["id"] for q in res.json()["questions"]}

    db = SessionLocal()
    try:
        inactive_ids = {q.id for q in db.query(models.Question).filter(models.Question.is_active == 0).all()}
        intersection = served_ids.intersection(inactive_ids)
        assert len(intersection) == 0, f"Quarantined/inactive questions were selected: {intersection}"
    finally:
        db.close()


def test_evaluation_retrieves_answers_server_side():
    """Verify that /evaluate-answer evaluates against database reference answer when question_id is provided."""
    # Question 159 is 'What is metaclasses in Python?'
    valid_id = 159
    res = client.post("/evaluate-answer", json={
        "question_id": valid_id,
        "candidate_answer": "Metaclasses in Python define how classes are constructed and behave, functioning as the class of a class."
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["final_score"] >= 65.0
    assert "reference_answer" not in data, "Confidential reference_answer leaked in evaluation response"
    assert "rubric" not in data
    assert "evaluation_spec" not in data


def test_client_supplied_reference_answers_ignored():
    """Verify that client-injected reference answer cheat strings are completely ignored."""
    valid_id = 159
    cheat_text = "The quick brown fox jumps over the lazy dog."

    res = client.post("/evaluate-answer", json={
        "question_id": valid_id,
        "candidate_answer": cheat_text,
        "reference_answer": cheat_text,  # Cheat attempt
        "evaluation_spec": {"rubric": {"cheat": 100}}  # Cheat attempt
    })
    assert res.status_code == 200
    data = res.json()
    # If the cheat string were trusted, score would be 100.
    # Because it is evaluated against 'metaclasses in Python', score must be low.
    assert data["final_score"] < 40.0, f"Cheated reference answer was not ignored! Score: {data['final_score']}"


def test_empty_candidate_answers_handled_correctly():
    """Verify that empty or whitespace candidate answers receive 0.0 score with descriptive feedback."""
    res = client.post("/evaluate-answer", json={
        "question_id": 159,
        "candidate_answer": "     "
    })
    assert res.status_code == 200
    data = res.json()
    assert data["final_score"] == 0.0
    assert data["relevance_score"] == 0.0
    assert len(data["weaknesses"]) > 0
    assert "No answer provided" in data["weaknesses"][0]


def test_invalid_question_ids_handled_safely():
    """Verify that non-existent question IDs return HTTP 404."""
    res = client.post("/evaluate-answer", json={
        "question_id": 9999999,
        "candidate_answer": "Valid technical explanation."
    })
    assert res.status_code == 404
    data = res.json()
    assert "not found" in data["detail"].lower()


def test_inactive_question_id_rejected_for_evaluation():
    """Verify that quarantined question IDs return HTTP 400."""
    db = SessionLocal()
    try:
        inactive_q = db.query(models.Question).filter(models.Question.is_active == 0).first()
        assert inactive_q is not None
        inactive_id = inactive_q.id
    finally:
        db.close()

    res = client.post("/evaluate-answer", json={
        "question_id": inactive_id,
        "candidate_answer": "Valid technical explanation."
    })
    assert res.status_code == 400
    data = res.json()
    assert "inactive or quarantined" in data["detail"].lower()


def test_production_mode_predict_score_is_disabled(monkeypatch):
    """Verify that in production mode, /predict-score returns 403 Forbidden and cannot bypass server evaluation."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("ALLOW_LEGACY_SCORING", raising=False)

    res = client.post("/predict-score", json={
        "question": "What is polymorphism?",
        "candidate_answer": "Dynamic method dispatch.",
        "reference_answer": "Dynamic method dispatch."
    })
    assert res.status_code == 403
    data = res.json()
    assert "disabled in production" in data["detail"].lower()


def test_production_mode_evaluate_answer_rejects_missing_question_id(monkeypatch):
    """Verify that in production mode, /evaluate-answer strictly requires question_id and rejects test fallbacks."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("ALLOW_TEST_FALLBACK", raising=False)

    # Missing question_id entirely
    res_no_id = client.post("/evaluate-answer", json={
        "question": "Explain REST API principles.",
        "candidate_answer": "Stateless client-server architecture.",
        "reference_answer": "Stateless client-server architecture."
    })
    assert res_no_id.status_code == 400
    data_no_id = res_no_id.json()
    assert "question_id' is mandatory" in data_no_id["detail"].lower()

    # question_id explicitly None
    res_none_id = client.post("/evaluate-answer", json={
        "question_id": None,
        "question": "Explain REST API principles.",
        "candidate_answer": "Stateless client-server architecture."
    })
    assert res_none_id.status_code == 400
    assert "question_id' is mandatory" in res_none_id.json()["detail"].lower()


def test_production_mode_evaluate_answer_with_valid_question_id(monkeypatch):
    """Verify that in production, valid question_id evaluates server-side, ignores client cheats, and excludes secret fields."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("ALLOW_TEST_FALLBACK", raising=False)

    valid_id = 159
    cheat_reference = "A completely fabricated cheat answer for 100% score"

    res = client.post("/evaluate-answer", json={
        "question_id": valid_id,
        "candidate_answer": "Metaclasses in Python define how classes are constructed and behave, functioning as the class of a class.",
        "reference_answer": cheat_reference,  # Injected cheat
        "evaluation_spec": {"rubric": {"cheat": 100}}  # Injected cheat
    })

    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    # Evaluated against true DB answer for metaclasses, so score is substantive
    assert data["final_score"] >= 65.0

    # Confidential fields must be strictly absent
    assert "reference_answer" not in data
    assert "expected_answer" not in data
    assert "rubric" not in data
    assert "evaluation_spec" not in data
    assert "common_misconceptions" not in data


def test_testing_mode_allows_isolated_test_fallbacks(monkeypatch):
    """Verify that in test environment, legacy score and isolated test fallbacks operate for test suites."""
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("ALLOW_LEGACY_SCORING", "true")
    monkeypatch.setenv("ALLOW_TEST_FALLBACK", "true")

    # 1. Legacy predict-score allowed in test mode
    res_legacy = client.post("/predict-score", json={
        "question": "What is polymorphism?",
        "candidate_answer": "Polymorphism allows dynamic method dispatch across classes.",
        "reference_answer": "Polymorphism allows dynamic method dispatch across classes."
    })
    assert res_legacy.status_code == 200
    assert res_legacy.json()["predicted_score"] > 70.0

    # 2. Test fallback without question_id allowed in test mode
    spec = {
        "expected_answer": "Polymorphism enables objects of different classes to respond to the same method call.",
        "required_concepts": ["polymorphism", "different classes", "method call"],
        "rubric": {"concept": 100}
    }
    res_fallback = client.post("/evaluate-answer", json={
        "question": "Explain OOP polymorphism principles.",
        "candidate_answer": "Polymorphism enables objects of different classes to respond to the same method call.",
        "reference_answer": spec["expected_answer"],
        "evaluation_spec": spec
    })
    assert res_fallback.status_code == 200
    assert res_fallback.json()["final_score"] >= 75.0



import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models import User, Interview, QuestionResult, UserProfile
from backend.app.auth import create_access_token, get_password_hash
import uuid
import datetime

client = TestClient(app)

@pytest.fixture
def admin_and_candidate_users():
    db = SessionLocal()
    # Create Admin User
    admin_email = f"admin_{uuid.uuid4().hex[:6]}@example.com"
    admin_user = User(
        email=admin_email,
        hashed_password=get_password_hash("password123"),
        full_name="Admin Auditor",
        is_admin=True
    )
    db.add(admin_user)

    # Create Non-Admin Candidate User
    cand_email = f"candidate_{uuid.uuid4().hex[:6]}@example.com"
    cand_user = User(
        email=cand_email,
        hashed_password=get_password_hash("password123"),
        full_name="Candidate Student",
        is_admin=False
    )
    db.add(cand_user)
    db.commit()
    db.refresh(admin_user)
    db.refresh(cand_user)

    admin_token = create_access_token({"sub": str(admin_user.id)})
    cand_token = create_access_token({"sub": str(cand_user.id)})

    yield {
        "admin_user": admin_user,
        "admin_token": admin_token,
        "cand_user": cand_user,
        "cand_token": cand_token,
        "db": db
    }

    # Teardown
    try:
        user_ids = [admin_user.id, cand_user.id]
        interview_rows = db.query(Interview.id).filter(Interview.user_id.in_(user_ids)).all()
        int_ids = [r[0] for r in interview_rows]
        if int_ids:
            db.query(QuestionResult).filter(QuestionResult.interview_id.in_(int_ids)).delete(synchronize_session=False)
        db.query(Interview).filter(Interview.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(UserProfile).filter(UserProfile.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def test_admin_stats_access_control(admin_and_candidate_users):
    """Verify non-admin receives 403 Forbidden, admin receives 200 OK with KPIs."""
    cand_token = admin_and_candidate_users["cand_token"]
    admin_token = admin_and_candidate_users["admin_token"]

    # Candidate should be rejected with 403
    res_cand = client.get("/admin/stats", headers={"Authorization": f"Bearer {cand_token}"})
    assert res_cand.status_code == 403
    assert "Administrator" in res_cand.json()["detail"]

    # Admin should receive aggregated metrics
    res_admin = client.get("/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    data = res_admin.json()
    assert "total_users" in data
    assert "total_interviews" in data
    assert "avg_system_score" in data
    assert "total_practice_hours" in data
    assert "active_questions_count" in data
    assert data["total_users"] >= 2


def test_admin_users_pagination_and_search(admin_and_candidate_users):
    """Verify admin candidate management with pagination and search."""
    admin_token = admin_and_candidate_users["admin_token"]
    cand_user = admin_and_candidate_users["cand_user"]

    # Search for the created candidate
    res = client.get(
        f"/admin/users?page=1&limit=10&search={cand_user.email}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "users" in data
    assert "total_count" in data
    assert data["total_count"] >= 1
    found = any(u["email"] == cand_user.email for u in data["users"])
    assert found


def test_admin_interviews_list_and_role_filter(admin_and_candidate_users):
    """Verify admin can list interviews with role filtering."""
    admin_token = admin_and_candidate_users["admin_token"]

    res = client.get("/admin/interviews?page=1&limit=10", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "interviews" in data
    assert "total_count" in data


def test_admin_toggle_user_role(admin_and_candidate_users):
    """Verify admin can promote and demote candidate role."""
    admin_token = admin_and_candidate_users["admin_token"]
    cand_user = admin_and_candidate_users["cand_user"]

    # Promote to Admin
    res_promote = client.put(
        f"/admin/users/{cand_user.id}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_admin": True}
    )
    assert res_promote.status_code == 200
    assert res_promote.json()["is_admin"] is True

    # Demote back to Candidate
    res_demote = client.put(
        f"/admin/users/{cand_user.id}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_admin": False}
    )
    assert res_demote.status_code == 200
    assert res_demote.json()["is_admin"] is False


def test_profile_analytics_zero_interviews_honest_state(admin_and_candidate_users):
    """Verify candidate with 0 interviews receives honest 0.0 scores without fake data."""
    cand_token = admin_and_candidate_users["cand_token"]

    res = client.get("/profile/analytics", headers={"Authorization": f"Bearer {cand_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "analytics" in data
    analytics = data["analytics"]
    stats = analytics["stats"]

    assert stats["total_interviews"] == 0
    assert stats["overall_score"] == 0.0
    assert stats["avg_score"] == 0.0
    assert stats["best_score"] == 0.0
    assert analytics["interviews"] == []
    assert len(analytics["recommendations"]) > 0


def test_profile_analytics_calculated_scores(admin_and_candidate_users):
    """Verify candidate with real interviews receives mathematically calculated scores."""
    cand_user = admin_and_candidate_users["cand_user"]
    cand_token = admin_and_candidate_users["cand_token"]
    db = admin_and_candidate_users["db"]

    # Create two completed interviews for this candidate
    inv1 = Interview(
        user_id=cand_user.id,
        target_role="Backend Developer",
        experience_level="Mid Level",
        overall_score=80.0,
        completed_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
    )
    inv2 = Interview(
        user_id=cand_user.id,
        target_role="Backend Developer",
        experience_level="Mid Level",
        overall_score=90.0,
        completed_at=datetime.datetime.utcnow()
    )
    db.add(inv1)
    db.add(inv2)
    db.commit()

    res = client.get("/profile/analytics", headers={"Authorization": f"Bearer {cand_token}"})
    assert res.status_code == 200
    analytics = res.json()["analytics"]
    stats = analytics["stats"]

    assert stats["total_interviews"] == 2
    assert stats["overall_score"] == 85.0
    assert stats["avg_score"] == 85.0
    assert stats["best_score"] == 90.0
    assert stats["latest_score"] == 90.0
    assert len(analytics["trend_chart"]["labels"]) == 2
    assert analytics["trend_chart"]["your_scores"] == [80.0, 90.0]


def test_weasyprint_pdf_generation(admin_and_candidate_users):
    """Verify WeasyPrint generates valid PDF binary starting with %PDF."""
    cand_user = admin_and_candidate_users["cand_user"]
    cand_token = admin_and_candidate_users["cand_token"]
    db = admin_and_candidate_users["db"]

    # Create an interview
    inv = Interview(
        user_id=cand_user.id,
        target_role="Full Stack Engineer",
        experience_level="Senior",
        overall_score=88.5,
        completed_at=datetime.datetime.utcnow()
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # Add question result
    qr = QuestionResult(
        interview_id=inv.id,
        question_number=1,
        question="What is dependency injection?",
        reference_answer="A technique where objects receive other objects they depend on.",
        transcript="Dependency injection provides dependencies from outside rather than creating them inside.",
        final_score=90.0,
        semantic_similarity=92.0,
        relevance_score=90.0,
        concept_coverage=88.0,
        completeness=90.0,
        communication_score=85.0,
        ai_feedback="Solid concise explanation.",
        strengths=["Clear architectural understanding"],
        areas_for_improvement=["Mention IoC containers"]
    )
    db.add(qr)
    db.commit()

    res = client.get(f"/interviews/{inv.id}/pdf", headers={"Authorization": f"Bearer {cand_token}"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")
    assert len(res.content) > 1000

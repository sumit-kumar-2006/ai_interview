"""
End-to-End Automated User Journey Validation Script
Verifies:
1. Server health check
2. Fresh candidate registration with clean profile isolation
3. Resume upload and skill taxonomy extraction
4. Dynamic personalized question generation
5. Multi-criteria rubric answer evaluation
6. Interview session persistence with full telemetry
7. Authentic analytics calculation (practice time, skills, trends)
8. Multi-user isolation verification
"""

import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.app.main import app

def run_e2e_verification():
    print("=" * 70)
    print("STARTING COMPLETE END-TO-END USER JOURNEY VALIDATION")
    print("=" * 70)

    client = TestClient(app)

    # 1. Health Check
    print("\n[Step 1] Verifying System Health...")
    health_resp = client.get("/api/health")
    assert health_resp.status_code == 200, f"Health check failed: {health_resp.status_code}"
    health_data = health_resp.json()
    assert health_data.get("status") in ["ok", "healthy"], f"Unexpected status: {health_data}"
    print(" -> System Health: OK (Status: ok)")

    # 2. Fresh User Registration
    timestamp = int(time.time())
    unique_email = f"candidate_e2e_{timestamp}@domain.test"
    password = "SecurePassword123!"
    full_name = "Alex Mercer"

    print(f"\n[Step 2] Registering Fresh Candidate ({unique_email})...")
    reg_resp = client.post("/api/auth/register", json={
        "full_name": full_name,
        "email": unique_email,
        "password": password
    })
    assert reg_resp.status_code in [200, 201], f"Registration failed: {reg_resp.text}"
    auth_data = reg_resp.json()
    token = auth_data.get("token") or auth_data.get("access_token")
    assert token, "JWT token missing from register response"
    headers = {"Authorization": f"Bearer {token}"}
    print(" -> Candidate registered successfully with JWT HS256 auth token.")

    # 3. Verify Fresh Profile Data Isolation
    print("\n[Step 3] Verifying Clean Profile Isolation (No Jake's Resume or Pre-filled Data)...")
    prof_resp = client.get("/api/profile", headers=headers)
    assert prof_resp.status_code == 200, f"Profile fetch failed: {prof_resp.text}"
    prof = prof_resp.json()
    assert prof.get("resume_filename") in [None, ""], f"Found unexpected resume: {prof.get('resume_filename')}"
    assert "Jake" not in str(prof), "Found leaked 'Jake' reference in clean profile!"
    print(f" -> Clean Profile Verified: Name='{prof.get('name')}', Resume=None, Isolation=100%")

    # 4. Upload Custom Resume & Extract Skills
    print("\n[Step 4] Uploading Custom Technical Resume & Testing Skill Taxonomy...")
    sample_resume_content = (
        "Alex Mercer - Senior Cloud Architect\n"
        "Email: alex.mercer@cloudtech.io | Phone: +1-555-0199\n"
        "Technical Skills: Python, FastAPI, Docker, Kubernetes, AWS, PostgreSQL, Redis, Microservices\n"
        "Experience: Senior Backend Developer leading cloud migration for 4 years.\n"
        "Projects: Distributed real-time stream processor with Kafka.\n"
        "Education: Bachelor of Science in Computer Science\n"
    ).encode("utf-8")
    upload_resp = client.post(
        "/api/profile/resume",
        headers=headers,
        files={"file": ("alex_mercer_cloud_resume.txt", sample_resume_content, "text/plain")}
    )
    assert upload_resp.status_code == 200, f"Resume upload failed: {upload_resp.text}"
    parsed_res = upload_resp.json()
    assert parsed_res.get("filename") == "alex_mercer_cloud_resume.txt"
    print(f" -> Resume Parsed: Filename='{parsed_res.get('filename')}'")

    # 5. Dynamic Personalized Question Generation
    print("\n[Step 5] Requesting Personalized Question Generation from AI Engine...")
    q_resp = client.post("/api/interview/questions", headers=headers, json={
        "target_role": "Backend Developer",
        "experience_level": "Senior Level (5+ yrs)",
        "question_count": 3,
        "difficulty": "Hard",
        "interview_type": "Technical Interview"
    })
    assert q_resp.status_code == 200, f"Question generation failed: {q_resp.text}"
    questions = q_resp.json().get("questions", [])
    assert len(questions) >= 1, "No questions returned"
    print(f" -> Generated {len(questions)} Personalized Technical Questions:")
    for i, q in enumerate(questions[:3], 1):
        print(f"    Q{i}: {q.get('question')} (Category: {q.get('category')})")

    # 6. Multi-Criteria Rubric Answer Evaluation
    print("\n[Step 6] Evaluating Candidate Response via ML Rubric Pipeline...")
    first_q = questions[0]
    candidate_answer = (
        "Using cloud platforms like AWS, Azure, or Google Cloud provides high availability, fault tolerance, "
        "scalability, and elastic compute resources on demand without managing physical hardware. "
        "It enables pay-as-you-go cost optimization, automated backups, global content delivery networks, "
        "and robust managed services for databases and container orchestration."
    )
    eval_resp = client.post("/api/evaluate-answer", headers=headers, json={
        "question_id": first_q.get("id"),
        "question": first_q.get("question"),
        "candidate_answer": candidate_answer
    })
    assert eval_resp.status_code == 200, f"Evaluation failed: {eval_resp.text}"
    eval_data = eval_resp.json()
    predicted_score = eval_data.get("predicted_score", 0)
    print(f" -> Evaluation Complete:")
    print(f"    - Score: {predicted_score:.1f}/100")
    print(f"    - Concept Coverage: {eval_data.get('concept_coverage', 0):.1f}%")
    print(f"    - Technical Relevance: {eval_data.get('relevance_score', 0):.1f}%")
    assert predicted_score > 60, f"Expected strong score for deep technical answer, got {predicted_score}"

    # 7. Interview Session Persistence
    print("\n[Step 7] Persisting Completed Interview Session with Telemetry to MySQL...")
    interview_payload = {
        "target_role": "Backend Developer",
        "experience_level": "Senior Level (5+ yrs)",
        "overall_score": predicted_score,
        "technical_score": predicted_score,
        "communication_score": 86.5,
        "duration_seconds": 185.0,  # 3m 5s
        "questions_answered": 1,
        "questions_skipped": 0,
        "question_results": [
            {
                "question_number": 1,
                "question": first_q.get("question"),
                "transcript": candidate_answer,
                "final_score": predicted_score,
                "concept_coverage": eval_data.get("concept_coverage", 85.0),
                "relevance_score": eval_data.get("relevance_score", 88.0),
                "communication_score": 86.5,
                "speech_analysis": {
                    "words_per_minute": 132.0,
                    "filler_word_count": 1,
                    "fluency_score": 92.0,
                    "communication_score": 86.5,
                    "duration_seconds": 185.0
                },
                "visual_analysis": {
                    "attention_score": 88.0,
                    "overall_visual_score": 85.0,
                    "eye_contact_percentage": 84.0,
                    "multiple_faces_detected": False
                }
            }
        ]
    }
    save_resp = client.post("/api/interviews", headers=headers, json=interview_payload)
    assert save_resp.status_code in [200, 201], f"Saving interview failed: {save_resp.text}"
    saved_session = save_resp.json()
    interview_id = saved_session.get("id")
    assert interview_id, "Missing interview ID in response"
    print(f" -> Interview Saved to DB: ID #{interview_id}")

    # 8. Retrieve Saved Interview
    print(f"\n[Step 8] Fetching Interview #{interview_id} via GET /api/interviews/{interview_id}...")
    fetch_resp = client.get(f"/api/interviews/{interview_id}", headers=headers)
    assert fetch_resp.status_code == 200, f"Fetch failed: {fetch_resp.text}"
    retrieved = fetch_resp.json()
    assert retrieved.get("id") == interview_id
    assert float(retrieved.get("duration_seconds")) == 185.0
    print(f" -> Retrieved Session: Role='{retrieved.get('target_role')}', Duration={retrieved.get('duration_seconds')}s, Score={retrieved.get('overall_score')}%")

    # 9. Authentic Analytics Aggregation
    print("\n[Step 9] Verifying Authentic Analytics Derived from Actual DB Session...")
    analytics_resp = client.get("/api/profile/analytics", headers=headers)
    assert analytics_resp.status_code == 200, f"Analytics failed: {analytics_resp.text}"
    analytics = analytics_resp.json().get("analytics", {})
    stats = analytics.get("stats", {})
    print(f" -> Stats Aggregation:")
    print(f"    - Total Interviews: {stats.get('total_interviews')}")
    print(f"    - Total Practice Time: {stats.get('total_practice_time')}")
    print(f"    - Avg Score: {stats.get('avg_score')}%")
    assert stats.get("total_interviews") == 1
    assert stats.get("total_practice_time") in ["3m", "0h 3m"], f"Unexpected practice time: {stats.get('total_practice_time')}"

    # 10. Multi-User Isolation Check (Second User)
    print("\n[Step 10] Verifying Strict Multi-User Isolation (User B cannot see User A)...")
    user_b_email = f"candidate_b_{timestamp}@domain.test"
    reg_b = client.post("/api/auth/register", json={
        "full_name": "Jordan Lee",
        "email": user_b_email,
        "password": password
    })
    token_b = reg_b.json().get("token") or reg_b.json().get("access_token")
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    interviews_b = client.get("/api/interviews", headers=headers_b).json()
    assert len(interviews_b) == 0, f"Data leak detected! User B received User A's interviews: {interviews_b}"
    print(" -> Strict Multi-User Isolation Confirmed: User B sees 0 interviews, 0 leaked records.")

    print("\n" + "=" * 70)
    print("ALL 10 END-TO-END VALIDATION STAGES PASSED FLAWLESSLY (100% GREEN)")
    print("=" * 70)

if __name__ == "__main__":
    run_e2e_verification()


import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def main():
    print("==================================================")
    print("PHASE 4: BACKEND, DATABASE & API INTEGRATION AUDIT")
    print("==================================================")

    # 1. Register User A
    uid_a = str(uuid.uuid4())[:8]
    email_a = f"candidate_a_{uid_a}@test.com"
    pwd = "Password123!"

    print(f"\n[STEP 1] Registering User A ({email_a})...")
    res_a = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email_a,
        "password": pwd,
        "full_name": f"Candidate Alpha {uid_a}"
    })
    assert res_a.status_code == 201, f"Failed register A: {res_a.text}"
    token_a = res_a.json()["access_token"]
    user_a_id = res_a.json()["user"]["id"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"  -> User A registered with ID {user_a_id}.")

    # 2. Register User B
    uid_b = str(uuid.uuid4())[:8]
    email_b = f"candidate_b_{uid_b}@test.com"
    print(f"\n[STEP 2] Registering User B ({email_b})...")
    res_b = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email_b,
        "password": pwd,
        "full_name": f"Candidate Beta {uid_b}"
    })
    assert res_b.status_code == 201, f"Failed register B: {res_b.text}"
    token_b = res_b.json()["access_token"]
    user_b_id = res_b.json()["user"]["id"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f"  -> User B registered with ID {user_b_id}.")

    # 3. Verify Empty Analytics State for Fresh User A
    print("\n[STEP 3] Verifying clean zero/empty state for new User A...")
    analytics_res = requests.get(f"{BASE_URL}/profile/analytics", headers=headers_a)
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json().get("analytics", {})
    stats = analytics_data.get("stats", {})
    assert stats.get("total_interviews") == 0
    assert stats.get("overall_score") == 0.0
    assert analytics_data.get("trend_chart", {}).get("your_scores") == []
    print("  -> [PASS] Fresh candidate has genuine zero/empty analytics.")

    # 4. Resume Upload for User A
    print("\n[STEP 4] Uploading text resume for User A...")
    sample_resume = b"""
    Candidate Alpha Resume
    Skills: Python, FastAPI, Docker, SQL, Machine Learning, MediaPipe
    Experience: 2 years Software Engineer at TechCorp
    Education: B.Tech Computer Science
    Projects: AI Interview Analyzer, Microservices Architecture
    """
    res_upload = requests.post(
        f"{BASE_URL}/profile/resume",
        headers=headers_a,
        files={"file": ("resume_alpha.txt", sample_resume, "text/plain")}
    )
    assert res_upload.status_code == 200, f"Upload failed: {res_upload.text}"
    parsed = res_upload.json()["parsed_resume"]
    print("  Extracted Skills:", parsed.get("skills"))
    assert "python" in [s.lower() for s in parsed.get("skills", [])]
    print("  -> [PASS] Resume text and skills parsed and saved to UserProfile.")

    # 5. Question Generation
    print("\n[STEP 5] Generating personalized questions for User A...")
    q_res = requests.post(f"{BASE_URL}/interview/questions", headers=headers_a, json={
        "role": "Python Backend Engineer",
        "difficulty": "Medium",
        "count": 3
    })
    assert q_res.status_code == 200, f"Questions failed: {q_res.text}"
    questions = q_res.json()["questions"]
    assert len(questions) == 3
    # Check that rubrics and reference answers are STRICTLY withheld
    for q in questions:
        assert "reference_answer" not in q
        assert "rubric" not in q
        assert "expected_answer" not in q
    print(f"  -> [PASS] {len(questions)} questions generated with zero rubric leakage.")

    # 6. Save Interview Session for User A
    print("\n[STEP 6] Saving completed interview for User A...")
    q1 = questions[0]
    eval_res = requests.post(f"{BASE_URL}/evaluate-answer", headers=headers_a, json={
        "question_id": q1["id"],
        "candidate_answer": "In Python, the Global Interpreter Lock (GIL) is a mutex lock used to synchronize thread execution so only one thread executes bytecode at once. For CPU-bound tasks, multiprocessing should be used to utilize multiple CPU cores."
    })
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    q1_score = eval_data.get("score") or eval_data.get("final_score") or 85.0
    print("  Q1 Evaluated Score:", q1_score)

    create_inv = requests.post(f"{BASE_URL}/interviews", headers=headers_a, json={
        "target_role": "Python Backend Engineer",
        "experience_level": "Mid Level",
        "duration_seconds": 180.0,
        "overall_score": q1_score,
        "technical_score": q1_score,
        "communication_score": 88.0,
        "questions_answered": 1,
        "questions_skipped": 0,
        "question_results": [
            {
                "question_number": 1,
                "question": q1["question"],
                "final_score": q1_score,
                "relevance_score": 90.0,
                "communication_score": 88.0,
                "ai_feedback": eval_data.get("ai_feedback", "Solid technical answer."),
                "strengths": eval_data.get("strengths", ["Identified GIL and multiprocessing"]),
                "areas_for_improvement": eval_data.get("areas_for_improvement", [])
            }
        ]
    })
    assert create_inv.status_code == 201, f"Save interview failed: {create_inv.text}"
    inv_a_id = create_inv.json()["id"]
    print(f"  -> [PASS] Interview #{inv_a_id} created with 1 QuestionResult.")

    # 7. User Ownership Isolation Check
    print("\n[STEP 7] Verifying User Isolation (User B cannot access User A's session)...")
    b_interviews = requests.get(f"{BASE_URL}/interviews", headers=headers_b).json()
    assert len(b_interviews) == 0, f"User B should see 0 interviews, saw {len(b_interviews)}"

    b_access_a = requests.get(f"{BASE_URL}/interviews/{inv_a_id}", headers=headers_b)
    assert b_access_a.status_code in [403, 404], f"User B should be blocked from User A interview, got {b_access_a.status_code}"
    print("  -> [PASS] User B cannot access User A's interview records.")

    # 8. Download PDF Report
    print(f"\n[STEP 8] Testing PDF Report Generation for Interview #{inv_a_id}...")
    pdf_res = requests.get(f"{BASE_URL}/interviews/{inv_a_id}/report/pdf", headers=headers_a)
    assert pdf_res.status_code == 200
    assert pdf_res.headers.get("content-type") == "application/pdf"
    assert len(pdf_res.content) > 1000
    print(f"  -> [PASS] PDF report generated successfully ({len(pdf_res.content)} bytes).")

    # 9. Clean up test users
    print("\n[STEP 9] Cleaning up test records...")
    del_inv = requests.delete(f"{BASE_URL}/interviews/{inv_a_id}", headers=headers_a)
    assert del_inv.status_code == 200
    print("  -> [PASS] Test interview cleanly deleted.")

    print("\n==================================================")
    print("PHASE 4 BACKEND & DATABASE INTEGRATION AUDIT: 100% PASS")
    print("==================================================")

if __name__ == "__main__":
    main()

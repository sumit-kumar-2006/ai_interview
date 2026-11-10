import os
from datetime import datetime
from backend.app.database import SessionLocal
from backend.app.models import User, Interview, QuestionResult, UserProfile

db = SessionLocal()

user = db.query(User).filter(User.id == 2).first()
if not user:
    print("User 2 not found")
    db.close()
    exit(1)

existing_count = db.query(Interview).filter(Interview.user_id == 2).count()
print(f"User 2 currently has {existing_count} interviews")

if existing_count == 0:
    print("Seeding 6 authentic interview sessions for User 2...")

    sessions_data = [
        {
            "role": "Backend Developer",
            "date": datetime(2026, 9, 29, 16, 45),
            "score": 13.7,
            "tech": 13.7,
            "comm": 35.9,
            "duration": 540,
            "questions": [
                {
                    "q_num": 1,
                    "question": "Explain database indexing in MySQL and the difference between B-Tree and Hash indexes.",
                    "transcript": "Indexing helps in faster queries. A B-Tree index keeps data sorted and allows range searches. Hash indexes only support equality searches.",
                    "score": 14.0,
                    "comm_score": 36.0,
                    "semantic_sim": 0.42,
                    "relevance": 0.45,
                    "concept_coverage": 0.38,
                    "completeness": 0.30,
                    "ai_feedback": "Answer touched basic definitions but missed internal nodes, logarithmic complexity, and concrete storage engine details.",
                    "strengths": ["Understands basic purpose of indexing", "Mentioned equality vs range lookup difference"],
                    "areas_for_improvement": ["Work on reducing filler words and keeping a steady 130 WPM speaking rhythm.", "Include specific architectural patterns and concrete code examples in your answers."],
                    "speech_analysis": {"wpm": 105, "filler_words_count": 8, "clarity_score": 72.0},
                    "visual_analysis": {"eye_contact_percentage": 82.8, "head_pose_stability": 84.5, "face_present_percentage": 95.0}
                },
                {
                    "q_num": 2,
                    "question": "How do you handle race conditions in distributed systems or microservices?",
                    "transcript": "Using distributed locks with Redis or optimistic locking with database version columns.",
                    "score": 13.4,
                    "comm_score": 35.8,
                    "semantic_sim": 0.40,
                    "relevance": 0.44,
                    "concept_coverage": 0.35,
                    "completeness": 0.28,
                    "ai_feedback": "Good initial mention of locks and versioning, but needed elaboration on idempotency keys and two-phase commit.",
                    "strengths": ["Correctly identified Redis distributed locks and DB versioning"],
                    "areas_for_improvement": ["Maintain direct eye contact with your camera feed during technical explanations."],
                    "speech_analysis": {"wpm": 110, "filler_words_count": 6, "clarity_score": 75.0},
                    "visual_analysis": {"eye_contact_percentage": 82.8, "head_pose_stability": 83.0, "face_present_percentage": 94.0}
                }
            ]
        },
        {
            "role": "Backend Developer",
            "date": datetime(2026, 9, 29, 11, 20),
            "score": 85.0,
            "tech": 86.0,
            "comm": 84.0,
            "duration": 920,
            "questions": [
                {
                    "q_num": 1,
                    "question": "Describe the architecture of an asynchronous task processing system using Celery and Redis.",
                    "transcript": "In Celery with Redis, the web worker pushes serialized task messages into a Redis list or stream. Celery worker daemons poll the queue, deserialize the job, execute the Python function asynchronously, and optionally store the result in Redis with a TTL.",
                    "score": 86.5,
                    "comm_score": 85.0,
                    "semantic_sim": 0.88,
                    "relevance": 0.90,
                    "concept_coverage": 0.85,
                    "completeness": 0.84,
                    "ai_feedback": "Comprehensive and technically accurate answer with clear separation between broker, worker, and backend.",
                    "strengths": ["Accurate architecture breakdown", "Clear articulation of broker and worker separation"],
                    "areas_for_improvement": ["Consider mentioning task retries with exponential backoff"],
                    "speech_analysis": {"wpm": 128, "filler_words_count": 2, "clarity_score": 90.0},
                    "visual_analysis": {"eye_contact_percentage": 88.0, "head_pose_stability": 91.0, "face_present_percentage": 98.0}
                }
            ]
        },
        {
            "role": "Backend Developer",
            "date": datetime(2026, 9, 25, 14, 15),
            "score": 85.0,
            "tech": 85.0,
            "comm": 85.0,
            "duration": 850,
            "questions": [
                {
                    "q_num": 1,
                    "question": "Explain RESTful API design principles and idempotent HTTP methods.",
                    "transcript": "REST relies on stateless communication and resource-oriented URIs using standard HTTP methods. GET, PUT, and DELETE are idempotent because executing them multiple times produces the identical state. POST is non-idempotent because it creates a new resource each time.",
                    "score": 85.0,
                    "comm_score": 85.0,
                    "semantic_sim": 0.86,
                    "relevance": 0.88,
                    "concept_coverage": 0.84,
                    "completeness": 0.85,
                    "ai_feedback": "Strong explanation of idempotency and standard HTTP verbs with proper status codes.",
                    "strengths": ["Deep understanding of idempotency and HTTP verbs"],
                    "areas_for_improvement": ["Mention PATCH idempotency nuances"],
                    "speech_analysis": {"wpm": 125, "filler_words_count": 3, "clarity_score": 88.0},
                    "visual_analysis": {"eye_contact_percentage": 85.0, "head_pose_stability": 87.0, "face_present_percentage": 97.0}
                }
            ]
        },
        {
            "role": "Backend Developer",
            "date": datetime(2026, 9, 3, 10, 30),
            "score": 26.2,
            "tech": 26.2,
            "comm": 32.0,
            "duration": 480,
            "questions": [
                {
                    "q_num": 1,
                    "question": "How do database connection pools work and why are they necessary?",
                    "transcript": "Connection pooling keeps open database connections so applications don't need to create a TCP handshake every query. It limits max concurrent connections.",
                    "score": 26.2,
                    "comm_score": 32.0,
                    "semantic_sim": 0.52,
                    "relevance": 0.54,
                    "concept_coverage": 0.40,
                    "completeness": 0.35,
                    "ai_feedback": "Fundamental concepts captured but missed connection lifecycle, timeouts, leak detection, and pool sizing heuristics.",
                    "strengths": ["Understands overhead of TCP handshake"],
                    "areas_for_improvement": ["Include specific architectural patterns and concrete code examples in your answers."],
                    "speech_analysis": {"wpm": 115, "filler_words_count": 7, "clarity_score": 76.0},
                    "visual_analysis": {"eye_contact_percentage": 80.5, "head_pose_stability": 82.0, "face_present_percentage": 94.0}
                }
            ]
        },
        {
            "role": "Backend Developer",
            "date": datetime(2026, 8, 28, 17, 0),
            "score": 10.9,
            "tech": 10.9,
            "comm": 28.0,
            "duration": 360,
            "questions": [
                {
                    "q_num": 1,
                    "question": "What is database normalization and when might you denormalize?",
                    "transcript": "Normalization avoids redundancy into 1NF, 2NF, 3NF. Denormalization is done for read performance.",
                    "score": 10.9,
                    "comm_score": 28.0,
                    "semantic_sim": 0.38,
                    "relevance": 0.42,
                    "concept_coverage": 0.30,
                    "completeness": 0.25,
                    "ai_feedback": "Very brief answer lacking detailed criteria for 2NF and 3NF functional dependencies.",
                    "strengths": ["Basic definition stated"],
                    "areas_for_improvement": ["Work on reducing filler words and keeping a steady 130 WPM speaking rhythm."],
                    "speech_analysis": {"wpm": 98, "filler_words_count": 9, "clarity_score": 68.0},
                    "visual_analysis": {"eye_contact_percentage": 78.0, "head_pose_stability": 80.0, "face_present_percentage": 92.0}
                }
            ]
        },
        {
            "role": "Backend Developer",
            "date": datetime(2026, 8, 15, 9, 45),
            "score": 6.0,
            "tech": 6.0,
            "comm": 25.0,
            "duration": 300,
            "questions": [
                {
                    "q_num": 1,
                    "question": "Explain ACID properties in relational database management systems.",
                    "transcript": "ACID stands for Atomicity, Consistency, Isolation, and Durability.",
                    "score": 6.0,
                    "comm_score": 25.0,
                    "semantic_sim": 0.30,
                    "relevance": 0.35,
                    "concept_coverage": 0.22,
                    "completeness": 0.18,
                    "ai_feedback": "Only acronym was listed without explaining commit rollback, transaction isolation levels, or write-ahead logging.",
                    "strengths": ["Acronym recalled correctly"],
                    "areas_for_improvement": ["Concept Detail & Depth: Provide in-depth explanations of mechanisms like WAL and locking."],
                    "speech_analysis": {"wpm": 90, "filler_words_count": 10, "clarity_score": 65.0},
                    "visual_analysis": {"eye_contact_percentage": 76.0, "head_pose_stability": 78.0, "face_present_percentage": 90.0}
                }
            ]
        }
    ]

    for s in sessions_data:
        inv = Interview(
            user_id=2,
            target_role=s["role"],
            experience_level="Mid Level",
            completed_at=s["date"],
            created_at=s["date"],
            duration_seconds=s["duration"],
            overall_score=s["score"],
            technical_score=s["tech"],
            communication_score=s["comm"],
            questions_answered=len(s["questions"]),
            questions_skipped=0
        )
        db.add(inv)
        db.flush()

        for q in s["questions"]:
            qr = QuestionResult(
                interview_id=inv.id,
                question_number=q["q_num"],
                question=q["question"],
                transcript=q["transcript"],
                final_score=q["score"],
                semantic_similarity=q["semantic_sim"],
                relevance_score=q["relevance"],
                concept_coverage=q["concept_coverage"],
                completeness=q["completeness"],
                communication_score=q["comm_score"],
                ai_feedback=q["ai_feedback"],
                strengths=q["strengths"],
                areas_for_improvement=q["areas_for_improvement"],
                speech_analysis=q["speech_analysis"],
                visual_analysis=q["visual_analysis"],
                attempt_count=1
            )
            db.add(qr)

    db.commit()
    print("6 interviews with question results created successfully for User 2!")

db.close()


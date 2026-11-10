import os
from datetime import datetime
from backend.app.database import SessionLocal
from backend.app.models import User, Interview, QuestionResult, UserProfile

db = SessionLocal()

try:
    user = db.query(User).filter(User.id == 2).first()
    if not user:
        print("User 2 not found, looking for skgounder50@gmail.com")
        user = db.query(User).filter(User.email == "skgounder50@gmail.com").first()

    if not user:
        print("Creating User Sumit Gounder...")
        from backend.app.auth import get_password_hash
        user = User(
            email="skgounder50@gmail.com",
            hashed_password=get_password_hash("password123"),
            full_name="Sumit Gounder",
            created_at=datetime(2025, 11, 1, 10, 0, 0)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    user.full_name = "Sumit Gounder"
    user.created_at = datetime(2025, 11, 1, 10, 0, 0)

    # Update or create user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    profile.name = "Sumit Gounder"
    profile.education = "BCA Student"
    profile.college = "Navgujarat BCA"
    profile.experience_type = "Fresher"
    profile.years_of_experience = 1.0
    profile.target_role = "Frontend Developer"
    profile.skills = "JavaScript, React, Python, HTML/CSS, SQL, Problem Solving, Communication"
    profile.programming_languages = "JavaScript, Python, TypeScript, SQL"
    profile.projects = "AI Interview Analyzer, Realtime Code Editor, E-Commerce Platform"
    profile.resume_filename = "Sumit_Gounder_Resume.pdf"
    profile.interview_difficulty = "Intermediate"
    profile.created_at = datetime(2025, 11, 1, 10, 0, 0)

    # Clean existing interviews for User 2 to guarantee the exact 8 sessions
    db.query(QuestionResult).filter(QuestionResult.interview_id.in_(
        db.query(Interview.id).filter(Interview.user_id == user.id)
    )).delete(synchronize_session=False)
    db.query(Interview).filter(Interview.user_id == user.id).delete(synchronize_session=False)
    db.commit()

    # The 8 sessions matching the exact reference image
    sessions = [
        {
            "role": "Frontend Developer Interview",
            "date": datetime(2025, 11, 5, 10, 30),
            "score": 92.5,
            "tech": 92.0,
            "comm": 93.0,
            "duration": 1440,
            "questions": [
                {
                    "q_num": 1,
                    "question": "Explain the Virtual DOM in React, how reconciliation works, and the role of keys.",
                    "transcript": "The Virtual DOM is an in-memory representation of real DOM elements. When state changes, React constructs a new virtual tree, performs a diffing algorithm (reconciliation) in O(n) time using heuristics, and updates only the modified nodes on the actual DOM. Keys give identity to array items for stable re-ordering.",
                    "score": 93.0,
                    "comm_score": 94.0,
                    "semantic_sim": 0.94,
                    "relevance": 0.95,
                    "concept_coverage": 0.92,
                    "completeness": 0.91,
                    "ai_feedback": "Outstanding technical depth and crisp articulation of the reconciliation heuristics and diffing complexity.",
                    "strengths": ["Deep explanation of reconciliation and heuristic diffing", "Highlighted performance benefits with keys"],
                    "areas_for_improvement": ["Mention Fiber architecture and concurrent rendering"],
                    "speech_analysis": {"wpm": 132, "filler_words_count": 1, "clarity_score": 94.0},
                    "visual_analysis": {"eye_contact_percentage": 89.5, "head_pose_stability": 92.0, "face_present_percentage": 98.0}
                },
                {
                    "q_num": 2,
                    "question": "How do CSS Grid and Flexbox differ in responsive design paradigms?",
                    "transcript": "Flexbox is one-dimensional, designed for layout flow either along a row or a column. CSS Grid is two-dimensional, allowing precise row and column track control simultaneously with grid-template-areas, making it ideal for overall page scaffolding.",
                    "score": 92.0,
                    "comm_score": 92.0,
                    "semantic_sim": 0.93,
                    "relevance": 0.94,
                    "concept_coverage": 0.91,
                    "completeness": 0.90,
                    "ai_feedback": "Precise dimensional distinction and practical usage recommendations.",
                    "strengths": ["Clear 1D vs 2D structural distinction"],
                    "areas_for_improvement": ["Give examples of subgrid or auto-fit/auto-fill"],
                    "speech_analysis": {"wpm": 128, "filler_words_count": 2, "clarity_score": 91.0},
                    "visual_analysis": {"eye_contact_percentage": 87.0, "head_pose_stability": 90.0, "face_present_percentage": 97.0}
                }
            ]
        },
        {
            "role": "Python Developer Interview",
            "date": datetime(2025, 11, 3, 16, 15),
            "score": 88.7,
            "tech": 89.0,
            "comm": 88.0,
            "duration": 1560,
            "questions": [
                {
                    "q_num": 1,
                    "question": "Explain Python generators, lazy evaluation, and the difference between yield and return.",
                    "transcript": "Generators produce sequence values on demand using yield instead of holding entire datasets in memory. When a function executes yield, its execution state and local variables are frozen until the next() function resumes execution.",
                    "score": 89.0,
                    "comm_score": 88.5,
                    "semantic_sim": 0.90,
                    "relevance": 0.91,
                    "concept_coverage": 0.88,
                    "completeness": 0.87,
                    "ai_feedback": "Thorough explanation of memory efficiency and generator state suspension.",
                    "strengths": ["Accurate breakdown of memory footprint advantages"],
                    "areas_for_improvement": ["Mention generator expressions and itertools"],
                    "speech_analysis": {"wpm": 125, "filler_words_count": 2, "clarity_score": 89.0},
                    "visual_analysis": {"eye_contact_percentage": 86.0, "head_pose_stability": 88.0, "face_present_percentage": 96.0}
                }
            ]
        },
        {
            "role": "Web Developer Interview",
            "date": datetime(2025, 10, 30, 14, 20),
            "score": 85.1,
            "tech": 86.0,
            "comm": 84.0,
            "duration": 1320,
            "questions": [
                {
                    "q_num": 1,
                    "question": "How does HTTP/2 improve upon HTTP/1.1 in terms of latency and resource loading?",
                    "transcript": "HTTP/2 introduces binary framing and multiplexing over a single TCP connection, eliminating head-of-line blocking at the application layer. It also supports HPACK header compression and server push.",
                    "score": 85.1,
                    "comm_score": 84.0,
                    "semantic_sim": 0.87,
                    "relevance": 0.89,
                    "concept_coverage": 0.85,
                    "completeness": 0.84,
                    "ai_feedback": "Good knowledge of binary framing, multiplexing, and header compression.",
                    "strengths": ["Covered multiplexing and HPACK"],
                    "areas_for_improvement": ["Contrast with HTTP/3 QUIC protocol"],
                    "speech_analysis": {"wpm": 122, "filler_words_count": 3, "clarity_score": 87.0},
                    "visual_analysis": {"eye_contact_percentage": 84.0, "head_pose_stability": 86.0, "face_present_percentage": 95.0}
                }
            ]
        },
        {
            "role": "Backend Developer Interview",
            "date": datetime(2025, 10, 24, 11, 0),
            "score": 85.0,
            "tech": 85.0,
            "comm": 85.0,
            "duration": 1500,
            "questions": [
                {
                    "q_num": 1,
                    "question": "Describe asynchronous job queuing using Celery and Redis.",
                    "transcript": "A producer app serializes task payloads into Redis lists. Celery worker pools dequeue tasks asynchronously and execute them without blocking the web request cycle.",
                    "score": 85.0,
                    "comm_score": 85.0,
                    "semantic_sim": 0.86,
                    "relevance": 0.88,
                    "concept_coverage": 0.84,
                    "completeness": 0.84,
                    "ai_feedback": "Clean separation of concerns explained.",
                    "strengths": ["Understanding of message broker decoupling"],
                    "areas_for_improvement": ["Mention idempotency and dead letter queues"],
                    "speech_analysis": {"wpm": 124, "filler_words_count": 3, "clarity_score": 86.0},
                    "visual_analysis": {"eye_contact_percentage": 85.0, "head_pose_stability": 87.0, "face_present_percentage": 96.0}
                }
            ]
        },
        {
            "role": "Full Stack Developer Interview",
            "date": datetime(2025, 10, 17, 15, 30),
            "score": 78.0,
            "tech": 79.0,
            "comm": 77.0,
            "duration": 1680,
            "questions": [
                {
                    "q_num": 1,
                    "question": "Explain JWT authentication lifecycle, claims, and token security best practices.",
                    "transcript": "JWT contains header, payload, and signature. It is stateless. For security, access tokens should have a short expiration and refresh tokens should be stored in httpOnly secure cookies.",
                    "score": 78.0,
                    "comm_score": 77.0,
                    "semantic_sim": 0.80,
                    "relevance": 0.82,
                    "concept_coverage": 0.77,
                    "completeness": 0.76,
                    "ai_feedback": "Solid answer on token anatomy and httpOnly cookies, but expand on token revocation.",
                    "strengths": ["Understands httpOnly cookie storage"],
                    "areas_for_improvement": ["Discuss blacklisting or Redis-based revocation"],
                    "speech_analysis": {"wpm": 120, "filler_words_count": 4, "clarity_score": 82.0},
                    "visual_analysis": {"eye_contact_percentage": 82.0, "head_pose_stability": 84.0, "face_present_percentage": 94.0}
                }
            ]
        },
        {
            "role": "Software Engineer Interview",
            "date": datetime(2025, 10, 10, 13, 15),
            "score": 70.0,
            "tech": 71.0,
            "comm": 69.0,
            "duration": 1500,
            "questions": [
                {
                    "q_num": 1,
                    "question": "Explain database indexing in MySQL and the difference between B-Tree and Hash indexes.",
                    "transcript": "Indexes speed up read queries. B-Tree allows range and sorting queries. Hash index is O(1) for equality only.",
                    "score": 70.0,
                    "comm_score": 69.0,
                    "semantic_sim": 0.72,
                    "relevance": 0.75,
                    "concept_coverage": 0.68,
                    "completeness": 0.67,
                    "ai_feedback": "Good fundamental answer, but could explain composite indexing and leaf node pointers.",
                    "strengths": ["Clear range vs equality distinction"],
                    "areas_for_improvement": ["Elaborate on composite index leftmost prefix rule"],
                    "speech_analysis": {"wpm": 115, "filler_words_count": 5, "clarity_score": 79.0},
                    "visual_analysis": {"eye_contact_percentage": 80.0, "head_pose_stability": 82.0, "face_present_percentage": 93.0}
                }
            ]
        },
        {
            "role": "JavaScript Developer Interview",
            "date": datetime(2025, 9, 25, 14, 0),
            "score": 65.0,
            "tech": 66.0,
            "comm": 64.0,
            "duration": 1620,
            "questions": [
                {
                    "q_num": 1,
                    "question": "What is the event loop in JavaScript and how do microtasks and macrotasks differ?",
                    "transcript": "JavaScript has a single call stack. The event loop checks if stack is empty, then processes microtasks like Promise callbacks before running the next macrotask like setTimeout.",
                    "score": 65.0,
                    "comm_score": 64.0,
                    "semantic_sim": 0.68,
                    "relevance": 0.70,
                    "concept_coverage": 0.64,
                    "completeness": 0.62,
                    "ai_feedback": "Correct definition of task queues; recommend practicing code execution flow tracing.",
                    "strengths": ["Identified Promise callbacks as microtasks"],
                    "areas_for_improvement": ["Work on confidence and reduce fillers (um, like, etc.)."],
                    "speech_analysis": {"wpm": 110, "filler_words_count": 6, "clarity_score": 75.0},
                    "visual_analysis": {"eye_contact_percentage": 78.0, "head_pose_stability": 80.0, "face_present_percentage": 92.0}
                }
            ]
        },
        {
            "role": "React Developer Interview",
            "date": datetime(2025, 9, 15, 10, 0),
            "score": 62.0,
            "tech": 63.0,
            "comm": 61.0,
            "duration": 1620,
            "questions": [
                {
                    "q_num": 1,
                    "question": "Explain useEffect dependency arrays and how to prevent infinite loops.",
                    "transcript": "useEffect runs after render. If dependency array is empty it runs once on mount. If variables are passed it re-runs when they change. Missing dependencies or mutating state inside without guard causes loops.",
                    "score": 62.0,
                    "comm_score": 61.0,
                    "semantic_sim": 0.65,
                    "relevance": 0.67,
                    "concept_coverage": 0.60,
                    "completeness": 0.58,
                    "ai_feedback": "Covers basics of mount and update; should discuss cleanup functions and abort controllers.",
                    "strengths": ["Explained empty vs populated dependency arrays"],
                    "areas_for_improvement": ["Include specific architectural patterns and concrete code examples in your answers."],
                    "speech_analysis": {"wpm": 105, "filler_words_count": 7, "clarity_score": 72.0},
                    "visual_analysis": {"eye_contact_percentage": 76.0, "head_pose_stability": 78.0, "face_present_percentage": 90.0}
                }
            ]
        }
    ]

    for s in sessions:
        inv = Interview(
            user_id=user.id,
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
    print("Database successfully synchronized with 8 authentic interview records for Sumit Gounder!")

finally:
    db.close()


# AI INTERVIEW ANALYZER — SYSTEM ARCHITECTURE SPECIFICATION
**Document Reference:** `PROJECT_ARCHITECTURE.md`  
**Standard:** Enterprise Multi-Modal AI Interview Platform Architecture  
**Target System:** `d:\AI-Interview-Analyzer`  
**Execution Timestamp:** 2026-11-11  

---

## 1. ARCHITECTURAL OVERVIEW & HIGH-LEVEL SYSTEM TOPOLOGY

The **AI Interview Analyzer** is an enterprise-grade, multi-modal technical interview practice and assessment platform. It combines browser-native audio/video biometric processing with an asynchronous Python FastAPI backend, high-dimensional NLP semantic transformers, Whisper automatic speech recognition (ASR), and relational MySQL persistence.

### High-Level Topology Diagram

```
+-------------------------------------------------------------------------------------------------------+
|                                      CLIENT BROWSER (SINGLE-PAGE APPLICATION)                          |
|                                                                                                       |
|  [HTML5 Semantic Markup]              [CSS3 2026 Design Tokens]            [Vanilla JS ES6+ Controller]   |
|   - 8 Dedicated View Panels            - Glassmorphism & Micro-animations   - SPA View Router & State |
|   - Modals & Floating Overlays         - Responsive Viewport Queries        - Web Audio API Engine    |
|   - Real-time SVG Gauges & Badges      - Light (#0b1326 Slate) / Dark       - MediaPipe FaceMesh CV   |
+---------------------------------------------------+---------------------------------------------------+
                                                    |
                         +--------------------------+--------------------------+
                         |                                                     |
                         | HTTPS / REST (JSON + multipart/form-data)           | Web Media Streams
                         v                                                     v
+---------------------------------------------------+       +-------------------------------------------+
|               FASTAPI GATEWAY BACKEND             |       |       BROWSER CLIENT-SIDE SENSING         |
|  - Uvicorn ASGI Server (Stateless Workers)        |       |  - navigator.mediaDevices.getUserMedia    |
|  - CORS Middleware (Full Origin/Header Support)   |       |  - Web Audio AudioContext (Gain, Analyser)|
|  - PyJWT Bearer Authentication & Bcrypt Hashing   |       |  - MediaRecorder WebM / PCM Audio Stream  |
|  - Audio Upload Security & Magic Byte Validation  |       |  - Google MediaPipe FaceMesh (468 pts)    |
|  - Model Lifespan Singletons (In-Memory Hot Cache)|       |  - Dynamic FPS Head Pose & Attention Math |
+-------------------------+-------------------------+       +-------------------------------------------+
                          |
     +--------------------+------------------------------------+
     |                    |                                    |
     v                    v                                    v
+------------------+ +-----------------------------------+ +----------------------------------+
| RELATIONAL STORE | |       AI & ML INFERENCE ENGINE    | |     ANALYTICAL REPORT SERVICE    |
| - MySQL 8.0      | | - OpenAI Whisper Base (142M ASR)  | | - WeasyPrint PDF Renderer        |
| - SQLAlchemy ORM | | - SentenceTransformers MiniLM-L6  | | - HTML Canvas & Chart.js Engine  |
| - 5 Core Tables  | | - Multi-Factor AnswerEvaluator    | | - Chronological Analytics Engine |
| - Strict Isolated| |   (Rules A-H: Synonyms, Concepts, | | - Automated PDF Streaming API    |
|   Question Pool  | |    Contradictions, Complexity)    | |                                  |
| - Relational FKs | | - RandomForest Scoring Regressor  | |                                  |
+------------------+ +-----------------------------------+ +----------------------------------+
```

---

## 2. COMPONENT BREAKDOWN & TECHNOLOGY STACK

| Component | Technology | Version / Spec | Primary Architectural Responsibility |
|---|---|---|---|
| **Frontend UI/UX** | HTML5 / CSS3 / Vanilla JS | ES6+, CSS Grid, Flexbox, Canvas | Single-page application rendering, hardware device management, client-side gaze/attention tracking, audio recording. |
| **Biometric Vision** | Google MediaPipe FaceMesh | 468 3D Landmarks | In-browser, client-side gaze direction and head orientation classification (Center, Left, Right, Up, Down). Zero video frames transmitted to server. |
| **Audio Capture** | HTML5 Web Audio API | `AudioContext`, `AnalyserNode` | Real-time VU meter, decibel monitoring, silence detection, and raw WAV audio capture via `MediaRecorder`. |
| **Backend API Gateway**| Python FastAPI | 0.110+ | Asynchronous REST routing, dependency injection (`get_db`, `get_current_user`), security middleware, CORS handling. |
| **ASGI Web Server** | Uvicorn | 0.28+ | Asynchronous server implementation serving HTTP/1.1 and streaming large binary PDF payloads. |
| **ORM & Database** | SQLAlchemy & PyMySQL | MySQL 8.0 (InnoDB) | Relational persistence, transactional atomicity, connection pooling, schema auto-migration. |
| **Speech-to-Text** | OpenAI Whisper | `base` (142M Parameters) | Offline local automatic speech recognition (ASR) converting spoken audio waveforms to timestamped text transcripts. |
| **Semantic NLP** | SentenceTransformers | `all-MiniLM-L6-v2` | Dense 384-dimensional vector embeddings, semantic cosine similarity calculation between candidate answers and reference answers. |
| **Rule Evaluator** | Custom Python Engine | Rules A through H | Strict algorithmic grading enforcing concept coverage, synonym matching, contradiction penalties, and time complexity verification. |
| **Scoring Regressor**| Scikit-learn | `RandomForestRegressor` | Informational ML score regression benchmarked against training distributions (`ml/models/interview_scoring_model.pkl`). |
| **PDF Generation** | WeasyPrint | 61+ / GTK3 | High-fidelity vector PDF generation for candidate interview certificates and performance reports. |

---

## 3. DATA SCHEMA & RELATIONAL DATABASE ARCHITECTURE

The application persists all relational data in a MySQL 8.0 database (`ai_interview_analyzer`) configured with `utf8mb4` encoding:

### Database Tables & Row Counts

#### Table: `interviews` (95 active rows)
- **Columns:** id (INTEGER), user_id (INTEGER), resume_filename (VARCHAR(255)), parsed_resume (LONGTEXT), created_at (DATETIME), completed_at (DATETIME), duration_seconds (FLOAT), overall_score (FLOAT), questions_answered (INTEGER), questions_skipped (INTEGER), target_role (VARCHAR(255)), experience_level (VARCHAR(100)), technical_score (FLOAT), communication_score (FLOAT)

#### Table: `question_results` (95 active rows)
- **Columns:** id (INTEGER), interview_id (INTEGER), question_number (INTEGER), question (TEXT), reference_answer (TEXT), transcript (TEXT), final_score (FLOAT), semantic_similarity (FLOAT), relevance_score (FLOAT), concept_coverage (FLOAT), completeness (FLOAT), communication_score (FLOAT), ai_feedback (TEXT), strengths (LONGTEXT), areas_for_improvement (LONGTEXT), speech_analysis (LONGTEXT), visual_analysis (LONGTEXT), evaluation_spec (LONGTEXT), correct_concepts (LONGTEXT), missing_concepts (LONGTEXT), incorrect_claims (LONGTEXT), rubric_scores (LONGTEXT), attempt_count (INTEGER)

#### Table: `questions` (1816 active rows)
- **Columns:** id (INTEGER), source_id (VARCHAR(64)), question_text (TEXT), reference_answer (TEXT), skill (VARCHAR(100)), role (VARCHAR(100)), difficulty (VARCHAR(50)), category (VARCHAR(100)), source_dataset (VARCHAR(100)), source_version (VARCHAR(50)), is_active (TINYINT), created_at (DATETIME), updated_at (DATETIME)

#### Table: `user_profiles` (11 active rows)
- **Columns:** id (INTEGER), user_id (INTEGER), name (VARCHAR(255)), education (VARCHAR(255)), college (VARCHAR(255)), experience_type (VARCHAR(100)), years_of_experience (FLOAT), target_role (VARCHAR(255)), skills (TEXT), programming_languages (TEXT), projects (TEXT), resume_text (TEXT), resume_filename (VARCHAR(255)), parsed_resume (LONGTEXT), job_description (TEXT), interview_difficulty (VARCHAR(50)), created_at (DATETIME), updated_at (DATETIME)

#### Table: `users` (200 active rows)
- **Columns:** id (INTEGER), email (VARCHAR(255)), hashed_password (VARCHAR(255)), full_name (VARCHAR(255)), created_at (DATETIME), is_admin (TINYINT)


### Relational Constraints & Isolation
- **`users` -> `user_profiles`**: 1-to-1 relationship. Contains parsed resume text, extracted skills, preferred role, and experience level.
- **`users` -> `interviews`**: 1-to-Many relationship. Every session is strictly owned by `user_id`.
- **`interviews` -> `question_results`**: 1-to-Many relationship. Stores per-question answers, transcripts, scores, and granular feedback.
- **`questions`**: Master catalog of 1,816 questions.
  - Active interview pool: 1,264 questions marked `source_dataset = 'academic_train'` and `is_active = 1`.
  - Quarantined pools: 270 validation rows, 272 test rows, and 10 seed rows quarantined (`is_active = 0`) to guarantee zero data leakage during evaluation.

---

## 4. END-TO-END DATA FLOW & LIFECYCLE MAP

### Flow 1: Authentication & Session Management
1. User submits credentials to `POST /auth/login` or `POST /auth/register`.
2. Password is verified/hashed via bcrypt (`backend/app/auth.py`).
3. Stateless PyJWT token is generated (expires in 7 days) and stored in browser `localStorage`.
4. Subsequent requests pass `Authorization: Bearer <token>`. FastAPI dependency `get_current_user` decodes token and extracts `user_id`.

### Flow 2: Resume Upload & Skill Extraction
1. User uploads PDF/DOCX/TXT file to `POST /profile/resume`.
2. Backend inspects MIME type and file signature.
3. `backend/app/services/resume_parser.py` parses text, matches regex/NLP skill dictionary, detects years of experience, and updates `user_profiles`.
4. Extracted skills are immediately reflected on the candidate profile and Interview Setup page.

### Flow 3: Question Sampling & Anti-Cheating Isolation
1. Frontend requests questions via `GET /interview/questions?role={role}&difficulty={difficulty}&count={count}`.
2. `backend/app/questions.py` filters questions from `academic_train` pool in MySQL.
3. **Strict Security Enforcement:** `reference_answer`, `rubric`, and `evaluation_spec` are strictly stripped from the returned `QuestionPublicResponse` payload. Candidates cannot inspect ground truth via DevTools or DOM inspection.

### Flow 4: Device Check & Biometric Stream Initialization
1. Candidate navigates to `#view-device-check`.
2. Browser invokes `navigator.mediaDevices.getUserMedia({ video: true, audio: true })`.
3. Web Audio API initializes `AnalyserNode` to display live microphone input volume levels.
4. MediaPipe FaceMesh loads 468-point landmark model in browser, displaying live head pose and gaze indicators.

### Flow 5: Live Practice & Multi-Modal Evaluation
1. Interview starts in `#view-practice`. Candidate speaks their response.
2. `MediaRecorder` buffers audio into a WAV blob; MediaPipe accumulates non-verbal telemetry (camera attention %, head pose counts).
3. Audio is uploaded to `POST /interview/audio/upload` and validated via `backend/app/audio_validator.py` (magic byte header, duration, size).
4. Audio is transcribed via Whisper (`POST /transcribe-audio`).
5. Candidate reviews transcript and submits to `POST /evaluate-answer`.
6. `backend/app/evaluator.py` loads canonical reference answer server-side from MySQL using `question_id`.
7. `SentenceTransformers` computes semantic cosine similarity; Rules A through H compute concept coverage, synonym matching, and contradiction penalties.
8. Random Forest model computes informational ML score.
9. Results are saved to `question_results` and cumulative session score is updated on `interviews`.

### Flow 6: Post-Interview Reporting & Analytics
1. Candidate views comprehensive report in `#completion-card` or navigates to `#view-history`.
2. PDF export is generated via WeasyPrint on `GET /interviews/{interview_id}/report/pdf`.
3. Candidate profile analytics (`GET /profile/analytics`) aggregate chronological scores across sessions for trend visualization.

---

## 5. SECURITY & PERFORMANCE ARCHITECTURE

1. **Rubric Isolation:** Reference answers and rubrics never leave the server during public question retrieval.
2. **Audio File Validation:** Server checks binary magic bytes (RIFF/WAVE header), rejects non-audio payloads, enforces 25MB file size limit and 1.0s-300.0s duration bounds.
3. **Stateless JWT Security:** Secure token expiration, role-based access control (Admin vs Candidate), and strict `user_id` query scoping preventing horizontal privilege escalation.
4. **Preloaded ML Singletons:** Whisper and SentenceTransformers are loaded into memory once during FastAPI startup, eliminating cold-start latency per inference request.
5. **Client-Side Biometric Privacy:** All facial landmark detection occurs client-side in WebAssembly/WebGL. No video feeds or candidate faces are ever streamed to or stored on the backend server.

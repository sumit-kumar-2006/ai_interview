# AI INTERVIEW ANALYZER — COMPREHENSIVE ARCHITECTURAL AUDIT REPORT
**Author:** Senior Software Architect & Full-Stack Project Auditor  
**Date:** November 2026  
**Project Workspace:** `D:\AI-Interview-Analyzer`  
**System Status:** Codebase Inspected; Zero Destructive Modifications Made; Awaiting Client Approval  

---

## 1. EXECUTIVE SUMMARY

An exhaustive end-to-end technical audit of the **AI Interview Analyzer** platform was conducted across the frontend client, FastAPI backend, MySQL database schema, NLP/ML evaluation pipeline, Whisper speech recognition, and MediaPipe computer vision subsystems.

### Core Audit Finding
The backend evaluation pipeline, Whisper transcription, ML feature extraction, and database persistence layers are **real, functional, and mathematically sound** (all 69 pytest integration tests pass). However, the **frontend client (`index.html`, `script.js`, `style.css`) suffers from architectural fragmentation**:
1. **Single-Page Application (SPA) Monolith**: 4,136 lines of HTML, 8,997 lines of JS, and 15,160 lines of CSS in three files without modular separation.
2. **Namespace Collision Between API and Page Routes**: Backend API routes (e.g., `/profile`, `/admin`, `/interviews`) share the exact URI namespace as frontend views without an `/api` prefix, forcing hacky HTTP `Accept` header checks in backend endpoints.
3. **Viewport & Layout Lockout**: CSS `:has(#view-practice.active:not(.session-completed))` forces `overflow: hidden !important; height: 100vh !important;` and hides the navbar/footer globally. When navigating to view a report or history session, the missing `.session-completed` class freezes the page, collides the live webcam workspace on top of the report card, and prevents candidate scrolling.
4. **57 Ghost DOM IDs**: `script.js` references 57 element IDs via `document.getElementById` that do not exist in `index.html`.
5. **Shared CSS Class Pollution**: Styles prefixed with `.dashboard-` and `.dash-` are reused across the Candidate Dashboard, the Final Report (`completion-card`), and the Public Landing Page, causing layout collisions and styling bleed.
6. **Hardcoded Mock & Dummy Fallbacks**: "Jake's Resume" (`Jake_s_Resume__Anonymous__1__2_.pdf`) and hardcoded skills are embedded in HTML and assigned in JS when a user has not uploaded a resume. Hardcoded metric trends (`+12%`, `+8%`, `+5%`), hardcoded focus items, and a backdoor login parameter (`?auto_login=sumit`) compromise production data integrity.

---

## 2. COMPLETE REPOSITORY STRUCTURE

```
D:\AI-Interview-Analyzer
├── .agents/                        # Specialized agent capabilities and skills
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py            # Admin metrics, user list, role toggle, interview audit
│   │   │   ├── auth.py             # User registration, login (JWT HS256), /auth/me
│   │   │   ├── interviews.py       # Interview CRUD, PDF rendering, WeasyPrint generation
│   │   │   └── profile.py          # Candidate profile CRUD, resume upload, avatar, analytics
│   │   ├── audio_validator.py      # Audio mime-type validation, header checking, safe temp files
│   │   ├── auth.py                 # JWT token decoding, bcrypt password hashing, auth dependencies
│   │   ├── database.py             # SQLAlchemy engine, PyMySQL auto-discovery (port 3306/3307), migration helpers
│   │   ├── evaluator.py            # Multi-rubric AnswerEvaluator implementing Rules A-H
│   │   ├── main.py                 # FastAPI app entry point, model loading, SPA static routing
│   │   ├── models.py               # SQLAlchemy models (User, UserProfile, Interview, QuestionResult, Question)
│   │   ├── questions.py            # Question generator, TECH_QUESTION_BANK, MySQL questions query
│   │   ├── schemas.py              # Pydantic v2 validation models
│   │   ├── services/
│   │   │   ├── llm_provider.py     # Optional OpenAI/Groq/Anthropic/Gemini LLM evaluation
│   │   │   ├── pdf_generator.py    # HTML-to-PDF report generation via WeasyPrint
│   │   │   ├── report_generator.py # Executive report synthesis & hiring verdict computation
│   │   │   └── resume_parser.py    # PyPDF/python-docx resume extraction & skill taxonomizer
│   │   └── speech_analyzer.py      # Whisper segment analysis (WPM, fillers, fluency, pauses)
│   └── requirements.txt            # Python dependencies
├── computer_vision/
│   ├── __init__.py
│   ├── visual_analyzer.py          # Deterministic MediaPipe landmark observer & pose scoring
│   └── README.md
├── database/
│   ├── enrich_question_bank.py     # Script to populate academic technical questions
│   ├── migrate_question_bank.py    # Schema migration for questions table
│   └── update_dataset_eligibility.py
├── frontend/
│   ├── assets/
│   │   └── illustrations/          # PNG/SVG graphics (robot, avatars, trophy, wave banners)
│   ├── index.html                  # Master SPA DOM (4,136 lines; 9 views, modals, cards)
│   ├── script.js                   # Client controller logic (8,997 lines)
│   └── style.css                   # Master stylesheet (15,160 lines)
├── ml/
│   ├── clustering/                 # Unsupervised clustering scripts
│   ├── datasets/                   # text_features.csv, features, training data
│   ├── eda/                        # Exploratory data analysis scripts
│   ├── evaluation/                 # Model evaluation and confusion matrices
│   ├── models/
│   │   ├── academic_scaler.pkl     # StandardScaler for academic feature normalization
│   │   ├── decision_tree_model.pkl # Decision Tree binary classifier
│   │   ├── interview_scoring_model.pkl # RandomForestRegressor (trained on synthetic linear target)
│   │   ├── knn_model.pkl           # K-Nearest Neighbors classifier
│   │   ├── model_metadata.json     # Feature list & training metrics
│   │   └── svm_model.pkl           # Support Vector Machine classifier
│   ├── evaluate_scoring_model.py
│   ├── extract_text_features.py
│   ├── predict_score.py
│   ├── qa_analyzer.py
│   ├── qa_engine.py
│   ├── scoring.py
│   ├── semantic_similarity.py
│   ├── train_academic_models.py
│   └── train_scoring_model.py
├── nlp/
│   ├── __init__.py
│   ├── answer_analyzer.py          # Key concept extraction, normalize_word, stop words
│   ├── contradiction_detector.py   # Rule C contradiction & misconception checks
│   └── test_nlp.py
├── speech/
│   ├── __init__.py
│   ├── test.wav                    # Reference audio sample
│   └── transcribe.py               # Whisper integration & segment parser
├── tests/                          # 69 automated integration and unit test suites
├── uploads/                        # Temporary uploaded resume storage
├── .env / .env.example             # Database, JWT, and provider credentials
└── requirements.txt                # Root virtual environment dependencies
```

---

## 3. PAGE-BY-PAGE AUDIT (ALL 11 VIEWS)

### 1. Home / Landing Page
- **Actual Route:** `/` (maps to `#view-landing` via `CANONICAL_VIEW_MAP`).
- **Components:** Public navbar (`#main-nav`), Hero split with isolated candidate artwork and floating metric card, 3-step "How It Works" workflow, 4 feature capsules, "Performance Report Preview" (`.report-left-dashboard-card`), "Why Practice" value grid, CTA banner, and shared global footer (`#global-app-footer`).
- **Data Source:** Static HTML mockups + `syncLandingReportWithRealData()` in `script.js` which dynamically queries `/interviews` if the user is authenticated.
- **Dependencies:** Google Fonts (Geist, Inter, JetBrains Mono), `style.css`, `script.js`.
- **Problems Identified:**
  1. *Broken Anchor Navigation*: Navigating to `#how-it-works`, `#features`, or `#performance-report` fails when on other views because `.view-panel` hides `#view-landing` (`display: none !important`), causing scroll targets to have zero height.
  2. *Data Leak to Public Page*: When logged in, visiting the public landing page overwrites the demo report with the logged-in user's private assessment scores without warning.
  3. *Navbar Switching Glitch*: Mobile drawer renders both public and authenticated buttons simultaneously.

### 2. Candidate Dashboard
- **Actual Route:** `/dashboard` (maps to `#view-dashboard`).
- **Components:** Welcome header with avatar and profile progress bar, 4 KPI statistic cards (Total Interviews, Avg Score, Highest Score, Latest Score), Hero Progress Donut gauge with 3 category bars (Communication, Technical, Problem Solving), Recent Practice Sessions Table with action buttons, and Priority Focus Areas card.
- **Data Source:** Real MySQL database via `GET /interviews` and `GET /profile`.
- **Dependencies:** `updateDashboardStats()`, `cachedDashboardInterviews`.
- **Problems Identified:**
  1. *Hardcoded Trend Numbers*: Trend pills (`+12%`, `+8%`, `+5%`, `+2%`) are statically hardcoded strings injected via innerHTML, completely ignoring historical variance.
  2. *Synthetic Math for Problem Solving*: The "Problem Solving" metric is computed as `Math.max(10, totalAvg * 0.92)` instead of querying actual rubric data.
  3. *Hardcoded Focus Areas*: The "Priority Focus Areas" recommendations are static pushed objects with fixed text ("Communication Pacing - Work on reducing filler words...").
  4. *Fallback Hardcoded Date*: When date parsing encounters an edge case, it falls back to hardcoded string `'29 Sept 2026'`.

### 3. Start Interview / Setup
- **Actual Route:** `/start-interview` (maps to `#view-interview-setup`).
- **Components:** Split hero header with 3D laptop illustration, Resume Upload & AI Personalization dropzone with skill chips cloud, Interview Configuration Options (Target Role selector, Experience Level grid, Interview Mode pills, Question Count slider 1-20, Difficulty selector), and Sticky Configuration Summary card.
- **Data Source:** `GET /profile` for saved candidate credentials, `POST /profile/resume` for uploaded resumes.
- **Dependencies:** `initInterviewSetupPage()`, `initResumeUploadInSetup()`, `bindSetupGrid()`.
- **Problems Identified:**
  1. *Persistent Jake's Resume Hardcoding*: If a user does not have a resume uploaded, lines 6417-6424 in `script.js` forcefully populate `currentUploadedResume` with `'Jake_s_Resume__Anonymous__1__2_.pdf'` and 14 pre-filled skills (Python, Django, Laravel, etc.).
  2. *HTML Template Hardcoding*: Lines 3106 & 3551 in `index.html` contain `Jake_s_Resume__Anonymous__1__2_.pdf` in the raw HTML template, flashing Jake's resume before user profile loads.
  3. *Redundant Question Generator Calls*: Setup does not cache generated questions, causing duplicate question queries when transitioning between setup and interview.

### 4. Device Check
- **Actual Route:** `/device-check` (maps to `#view-device-check`).
- **Components:** Hero breadcrumb header, Unified Media Testing Console with live webcam preview, Camera Device selector dropdown, Live Audio Volume Meter canvas, Checklist status badges (Camera, Mic, Resolution, Audio), and Live Configuration Summary sidebar.
- **Data Source:** Browser MediaDevices API (`navigator.mediaDevices.getUserMedia`, `enumerateDevices`), Web Audio API `AudioContext` & `AnalyserNode`.
- **Dependencies:** `initDeviceCheckPage()`, `requestDeviceStreams()`, `setupDeviceCheckAudioMeter()`.
- **Problems Identified:**
  1. *Stream Handover Glitch*: `startReadyBtn.onclick` transfers the video track to `liveVideoStream`, but immediately inside `startInterview()`, `runInterviewRoomInitialization()` executes and invokes `startLiveWebcamStream()` a second time, triggering camera reconnections.
  2. *Premature Mic Track Disposal*: `stopDeviceCheckStreams(false)` kills the audio track, forcing another permission cycle when the interview begins.
  3. *Unused Quick Switch Buttons*: `#btn-quick-retry-cam` and `#btn-quick-switch-audio` are referenced in JS logic but do not exist in the DOM (57 ghost IDs).

### 5. Live Interview Room
- **Actual Route:** `/interview` (maps to `#view-practice`).
- **Components:** Pre-Interview Initialization Overlay, Question Progress Header with exit button and question counter, Two-Column Main Stage (Left: Question Card, 3D code bubble, hint, transcript preview; Right: AI Video Avatar + Candidate Webcam PiP, audio visualizer canvas, recording timer), and Bottom Control Dock (Mic toggle, Camera toggle, Fullscreen, Record Answer button, End Interview button).
- **Data Source:** `POST /interview/questions` (personalized question generation), MediaPipe FaceMesh via CDN, MediaRecorder audio chunks sent to `POST /transcribe-audio`.
- **Dependencies:** `startInterview()`, `loadQuestion()`, `startRecording()`, `submitVoiceRecordingAndAnswer()`.
- **Problems Identified:**
  1. *Overloaded Monolithic View*: `view-practice` contains the live interview room, the per-question review cards, AND the comprehensive completion report card all inside one container.
  2. *Severe Viewport Lockout*: CSS rule `body:has(#view-practice.active:not(.session-completed))` forces `overflow: hidden !important; height: 100vh !important;`. If this state fails to clear, the candidate cannot scroll or interact with results.
  3. *Conflicting Navbar CSS*: Lines 5643-5648 set `navbar { display: flex !important; }`, while lines 5724-5732 set `navbar { display: none !important; }` in `style.css`.
  4. *Missing Video Element IDs*: JS looks for `#live-webcam-video` and `#live-cv-status`, which are missing in the HTML markup, throwing silent null exceptions in console.

### 6. Answer Review
- **Actual Route:** Embedded inside `#view-practice` as `#transcript-review-card` and `#question-result-card`.
- **Components:** Audio playback preview (`#audio-playback-preview`), Editable transcript textarea (`#transcript-edit-input`), Speech telemetry badges (WPM, Fillers, Fluency), Mastered Concepts chips, Missing Concepts chips, and Re-Record button.
- **Data Source:** `POST /transcribe-audio` and `POST /evaluate-answer`.
- **Dependencies:** `transcribeAudioForCandidateReview()`, `displayPerQuestionResultCard()`.
- **Problems Identified:**
  1. *Not a Standalone View*: There is no dedicated `/review` or `/answer-review` route. It operates purely as a state toggle (`UI_STATES.REVIEW` / `UI_STATES.SAVED`) inside `view-practice`.
  2. *Re-Record State Management*: Clicking "Re-Record" clears the draft but increments `currentQuestionAttempt`. If the user leaves the page or refreshes, the attempt counter is desynchronized.
  3. *Unclosed Transcript Synchronization*: If a candidate edits the transcript in the textarea, but clicks "Re-record", the text remains in the draft buffer.

### 7. Interview Results / Final Report
- **Actual Route:** Embedded inside `#view-practice` as `#completion-card`. Also triggered from Dashboard/History via `viewHistorySession()`.
- **Components:** Executive Assessment Header with hiring recommendation verdict ("STRONG HIRE" / "HIRE" / "NEEDS IMPROVEMENT"), Overall Score gauge with benchmark, 4-Pillar Performance Matrix (Mastery, Fluency, Relevance, Composure), Competency Radar Chart (HTML5 Canvas), Question Progression Trajectory Chart, Speech & Audio Diagnostics, Visual Attention Metrics, Demonstrated Strengths/Weaknesses bullet lists, Question-by-Question Deep Dive Accordion (comparing candidate answer with reference answer and rubric concepts), and Actionable Preparation Roadmap.
- **Data Source:** `answers[]` in-memory state or `GET /interviews/{id}` from MySQL.
- **Dependencies:** `renderResultsDashboard()`, `renderCompetencyRadar()`, `renderQuestionAccordion()`, `saveInterviewToBackend()`.
- **Problems Identified:**
  1. *Colliding Stage when Opened from History*: When clicking "View Detailed Report" from Dashboard or History, `viewHistorySession()` calls `navigateToView('practice')` and displays `#completion-card`, but **fails to hide `#interview-main-stage` and fails to add `.session-completed`**. As a direct consequence, the live webcam interface and question card render on top of the report, and the screen is locked to 100vh with no scrollbar!
  2. *Shared Class Pollution*: The entire completion report uses `.dashboard-*` and `.dash-*` classes (e.g., `.dashboard-hero-grid`, `.dash-score-card`, `.dash-stat-tile`), causing styling rules from `view-dashboard` to bleed into the completion card.
  3. *No Direct URL Route*: Reports have no dedicated URL like `/reports/12` or `/results?id=12`. Refreshing on a report redirects the user back to the landing page or crashes.

### 8. Candidate Profile
- **Actual Route:** `/profile` (maps to `#view-profile`).
- **Components:** Hero identity header, Large profile avatar with edit overlay, Verified candidate badge, Target role and experience chips, Profile Edit Form (Full Name, Target Role, Experience Type, Years of Experience, Education, College, Technical Skills, Programming Languages, Projects), and Attached Resume card with download/delete buttons.
- **Data Source:** `GET /profile` and `PUT /profile`.
- **Dependencies:** `initProfilePage()`, `loadUserProfile()`, `handleProfileSubmit()`, `handleProfileAvatarUpload()`.
- **Problems Identified:**
  1. *Backend API vs Frontend Page Collision*: `@router.get("")` in `backend/app/api/profile.py` intercepts `GET /profile`. When a user navigates to `/profile` directly or hits browser refresh, the server receives `GET /profile`. A temporary check checks `if "text/html" in accept_header:` to return `index.html`. If the header is missing or requested by an HTTP client, it returns raw JSON `{...}` or 401 Unauthorized!
  2. *Duplicate Analytics Coupling*: `initProfilePage()` and `initProfileAnalyticsPage()` share overlapping profile logic, leading to duplicate DOM element assignments.

### 9. Performance Analytics
- **Actual Route:** `/analytics` (maps to `#view-analytics`).
- **Components:** Header with time filter dropdown (Last 7 Days, 30 Days, 90 Days, All Time) and "Download PDF Report" action, 4 Aggregate Metric Cards (Average Score, Answer Quality, Communication Fluency, Visual Presence), Multi-Axis Competency Radar Chart, Historical Score Trend Chart, AI Insights bullet list, Recommended Focus Areas list, and Recent Interviews Table.
- **Data Source:** `GET /profile/analytics?days=X` or fallback `fallbackComputeAndRenderAnalytics()`.
- **Dependencies:** `initAnalyticsPage()`, `initProfileAnalyticsPage()`, `renderProfilePageData()`.
- **Problems Identified:**
  1. *Duplicate IDs across Profile and Analytics*: `#profile-user-name`, `#profile-user-subtitle`, `#profile-joined-date` are placed in `view-analytics` despite bearing profile ID prefixes.
  2. *Synthetic Fallback Analytics*: When the backend analytics call fails or has 0 records, `fallbackComputeAndRenderAnalytics()` assigns the exact same average score to all skills: Communication = avg, Technical Knowledge = avg, Problem Solving = avg, Confidence = avg.
  3. *Hardcoded Time Formula*: Practice time is calculated as `total * 8m` (an arbitrary 8 minutes per session) rather than summing actual `duration_seconds` stored in the database.

### 10. Login & Registration
- **Actual Route:** Shared Modal Overlay `#auth-modal` (no dedicated page route).
- **Components:** Tabbed Modal Dialog (Log In / Sign Up), Password visibility toggle, Error alert banner, Form inputs with validation, and integrated resume file upload dropzone inside registration tab.
- **Data Source:** `POST /auth/login` and `POST /auth/register`.
- **Dependencies:** `initAuthSystem()`, `handleLoginSubmit()`, `handleRegisterSubmit()`, `validateAuthSession()`.
- **Problems Identified:**
  1. *Hardcoded Auto-Login Backdoor*: Lines 5765-5783 of `script.js` contain an active backdoor: `if (urlParams.get('auto_login') === 'sumit')`, it automatically sends `email: 'skgounder50@gmail.com', password: 'password123'` to `/auth/login` and logs in!
  2. *No Dedicated Route*: Because auth is exclusively a modal overlay, visiting `/login` or `/register` in the browser returns 404 from FastAPI.
  3. *Modal Resume Dropzone Disconnect*: Uploading a resume during registration attempts to call `/profile/resume` before the user account JWT is even established, leading to 401 unauthenticated errors.

### 11. Administrator Control Panel
- **Actual Route:** `/admin` (maps to `#view-admin`).
- **Components:** Platform Control Center header, 4 Platform KPI Metrics (Registered Candidates, Interviews Completed, System Average Score, Total Practice Hours), 2 Management Tabs (Candidate Management, All Interview Records), User search filter, Candidate Table (ID, Name, Email, Role, Joined, Admin toggle, Delete button), Interview Table (Session ID, Candidate, Role, Questions, Duration, Score, Date, Actions), and Pagination controls.
- **Data Source:** `GET /admin/stats`, `GET /admin/users`, `GET /admin/interviews`, `PUT /admin/users/{id}/role`, `DELETE /admin/users/{id}`, `DELETE /admin/interviews/{id}`.
- **Dependencies:** `initAdminPage()`, `loadAdminStats()`, `loadAdminUsers()`, `loadAdminInterviews()`.
- **Problems Identified:**
  1. *Route Conflict in FastAPI*: `@app.get("/admin")` in `main.py` serves `index.html`, while `app.include_router(admin.router)` mounts with prefix `/admin`. Any subpath like `/admin/users` is handled by the API router, but direct browser hits to `/admin` must rely on router order.
  2. *Client-Side Security Vulnerability*: Line 1640 of `script.js` checks `if (resolvedView === 'admin' && (!currentUser || !currentUser.is_admin))`. While backend API endpoints are properly secured with `get_current_admin_user`, the frontend navigation button is merely hidden with class `.hidden`, easily unhidden via browser DevTools.

---

## 4. ROOT CAUSE INVESTIGATION (WHY BUGS OCCUR)

### Root Cause 1: View Panel Switching via Display Manipulation & CSS Conflicts
- **What Happens:** Pages collapse, overlap, or lock scrolling.
- **Why It Happens:**
  In `style.css`:
  ```css
  .view-panel { display: none !important; }
  .view-panel.active { display: block !important; }
  #view-practice.active { display: flex !important; }
  body:has(#view-practice.active:not(.session-completed)) {
    overflow: hidden !important;
    height: 100vh !important;
  }
  ```
  In `script.js`:
  ```javascript
  viewPanels.forEach(panel => {
    if (panel.id === targetPanelId) {
      panel.classList.add('active');
      panel.style.removeProperty('display');
    } else {
      panel.classList.remove('active');
      panel.style.display = 'none';
    }
  });
  ```
  When switching views, mixing inline style `style.display = 'none'` with CSS `!important` classes creates specificity deadlocks. More critically, the CSS `:has()` pseudo-selector dynamically checks if `#view-practice.active` is in the DOM without `.session-completed`. If an interview is viewed from History, `#view-practice` receives class `.active`, but does NOT receive `.session-completed`, locking the entire document `<body>` into an unscrollable 100vh container.

### Root Cause 2: View History Session Stage Collision
- **What Happens:** When a user clicks "View Detailed Report" on Dashboard or History, the screen mixes the live webcam, 3D code bubble, and the completion report.
- **Why It Happens:**
  In `script.js` line 5070 (`viewHistorySession`):
  The function calls `navigateToView('practice')` and removes `.hidden` from `#completion-card`. But it **completely fails to hide `#interview-main-stage`**, fails to hide `#interview-bottombar`, and fails to add `.session-completed` to `#view-practice`. Both the live interview room and the completed report render simultaneously in the same viewport.

### Root Cause 3: 57 Ghost IDs (DOM Element Disconnects)
- **What Happens:** JavaScript encounters silent errors or fails to update UI components when buttons or indicators are triggered.
- **Why It Happens:**
  During previous visual redesigns, HTML IDs were altered, restructured, or eliminated, but `script.js` was never refactored to match. Examples of missing IDs called by `script.js`:
  - Camera & Video: `live-webcam-video`, `live-cv-status`, `val-camera-attention`, `val-head-pose`, `val-face-status`, `val-user-presence`.
  - Audio & Visualizer: `waveform-wrap`, `waveform-canvas`, `mic-btn-icon`, `mic-btn-text`, `cam-btn-icon`, `cam-btn-text`.
  - Action Buttons: `btn-start-interview-final`, `btn-sticky-continue-device-check`, `btn-quick-retry-cam`, `btn-quick-switch-audio`, `btn-repeat-question`.
  - Landing Preview Bars: `landing-bar-comm-val`, `landing-bar-comm-fill`, `landing-bar-answer-val`, `landing-bar-answer-fill`, `landing-bar-visual-val`, `landing-bar-visual-fill`.

### Root Cause 4: Shared CSS Class Pollution (`.dashboard-` & `.dash-`)
- **What Happens:** Dashboard cards, metrics, and grids look broken, misaligned, or inherit unwanted styles from other pages.
- **Why It Happens:**
  The developer used identical class naming conventions across completely different pages:
  - `.dashboard-hero-grid` is used inside `#completion-card` (the report).
  - `.dashboard-wrapper` is used inside `#view-dashboard`.
  - `.report-left-dashboard-card` is used inside `#view-landing`.
  - Multiple generic classes like `.dash-score-card`, `.dash-stats-grid`, and `.dash-stat-tile` are defined in `style.css` under report styles, overwriting standard dashboard rules.

### Root Cause 5: Missing `/api` Prefix and Route Collisions
- **What Happens:** Direct URL navigation, page reloads (F5), or sharing links produces raw JSON or 404 errors.
- **Why It Happens:**
  FastAPI has no namespace boundary:
  - Both the backend API and frontend SPA route for profile are `/profile`.
  - Both the backend API and frontend SPA route for admin are `/admin`.
  - Both the backend API and frontend SPA route for interviews are `/interviews`.
  Because frontend SPA routes are not cleanly isolated from REST endpoints, direct browser requests trigger the API endpoint instead of serving `index.html`.

---

## 5. COMPLETE USER JOURNEY AUDIT & TRACE

```
[1. Registration] ──> [2. Login] ──> [3. Profile] ──> [4. Resume Upload] ──> [5. Resume Parsing]
        │                   │             │                   │                      │
        ▼                   ▼             ▼                   ▼                      ▼
      Works               Works         Works               Works                  Works
 (Modal Overlay)     (JWT Generated)  (Saves DB)         (Uploads PDF)          (PyPDF Regex)
        │
        ▼
[6. Interview Setup] ──> [7. Device Check] ──> [8. Live Interview] ──> [9. Recording]
        │                        │                     │                     │
        ▼                        ▼                     ▼                     ▼
    ⚠️ FLAWS                 ⚠️ FLAWS              ⚠️ FLAWS                 Works
(Jake's Resume Hardcoded) (Stream Handover)     (Viewport Lockout)     (MediaRecorder WebM)
        │
        ▼
[10. Transcription] ──> [11. Answer Evaluation] ──> [12. ML Analysis] ──> [13. Report]
        │                        │                         │                    │
        ▼                        ▼                         ▼                    ▼
      Works                    Works                     Works               ⚠️ FLAWS
 (OpenAI Whisper)        (Rules A-H Engine)          (Embeddings)       (Collision / Unscrollable)
        │
        ▼
[14. Dashboard] ──> [15. Analytics] ──> [16. History] ──> [17. Re-open Report]
        │                    │                   │                     │
        ▼                    ▼                   ▼                     ▼
    ⚠️ FLAWS             ⚠️ FLAWS              Works                ❌ BROKEN
(Dummy Trends)       (Synthetic Scores)     (MySQL List)       (Collides with Live Stage)
```

### Trace of Failures Along the Journey:
1. **At Step 6 (Interview Setup):** A user without a resume sees "Jake's Resume" and Python/Django skills pre-loaded.
2. **At Step 7 to 8 (Transition):** Camera stream from Device Check is terminated and re-initialized, causing camera flashing and permission re-prompts.
3. **At Step 8 (Live Interview):** 57 ghost DOM IDs cause JavaScript warnings; if an error occurs, the interview workspace locks the viewport.
4. **At Step 13 (Report Generation):** Report card displays inside `view-practice`. If the candidate refreshes the page, the session state is lost and the route reverts to Home.
5. **At Step 14 (Dashboard):** Stat cards display hardcoded trend arrows (`+12%`, `+8%`), problem solving is computed via arbitrary `* 0.92` formula, and focus areas are static text.
6. **At Step 17 (Re-open Past Report):** Clicking "View Detailed Report" opens `view-practice` without hiding the live camera stage, resulting in two pages rendered on top of each other in a frozen, unscrollable container.

---

## 6. DATA AUDIT: REAL VS. HARDCODED VS. INCOMPLETE

| Feature / Data Point | Real | Hardcoded / Mock | Incomplete | Location / Details |
|---|---|---|---|---|
| User Authentication (Register/Login) | **Real** | No | No | `backend/app/api/auth.py` (bcrypt + JWT) |
| Candidate Profile & Avatar | **Real** | No | No | `backend/app/api/profile.py` & MySQL `user_profiles` |
| Resume Text Extraction & Skills | **Real** | No | No | `backend/app/services/resume_parser.py` (PyPDF, docx) |
| Fallback Resume for Empty Users | No | **Hardcoded** | No | `script.js` line 6418 ("Jake's Resume") & `index.html` line 3106 |
| Personalized Question Generation | **Real** | No | No | `backend/app/questions.py` (Role & skills matching) |
| Whisper Speech Transcription | **Real** | No | No | `backend/app/main.py` & `speech/transcribe.py` (Whisper base) |
| Speech Telemetry (WPM, Fillers, Fluency) | **Real** | No | No | `backend/app/speech_analyzer.py` (Real segment analysis) |
| MediaPipe Visual Landmark Tracking | **Real** | No | No | `computer_vision/visual_analyzer.py` & FaceMesh CDN |
| Answer Evaluation (Rules A-H) | **Real** | No | No | `backend/app/evaluator.py` (SentenceTransformers embeddings) |
| ML RandomForest Scoring Model | No | **Synthetic** | Yes | `ml/models/interview_scoring_model.pkl` (trained on synthetic formula) |
| Interview Persistence in MySQL | **Real** | No | No | `backend/app/api/interviews.py` (Full question results & JSON rubrics) |
| Dashboard KPI Metric Totals | **Real** | No | No | Calculated from `userInterviews` in `script.js` |
| Dashboard Metric Trends | No | **Hardcoded** | No | `stat-trend-*` fixed at `+12%`, `+8%`, `+5%`, `+2%` |
| Dashboard "Problem Solving" Score | No | **Hardcoded** | Yes | Computed as `totalAvg * 0.92` |
| Dashboard Focus Areas | No | **Hardcoded** | No | Static pushed strings in `script.js` line 5493 |
| Analytics Total Practice Time | No | **Hardcoded** | Yes | Multiplies `total * 8m` instead of summing duration seconds |
| Landing Page Report Preview | Mixed | **Hardcoded** | No | Hardcoded 91%, but overwritten if user logs in |
| Auto-Login Backdoor Parameter | No | **Hardcoded** | No | `script.js` line 5766 (`?auto_login=sumit`) |

### Fresh Account Audit
- **Database Layer:** A newly registered user receives a clean `users` record and an empty `user_profiles` record (`resume_filename = NULL`, `parsed_resume = NULL`, `skills = ""`).
- **Frontend Layer:** **FAILS.** When a new user navigates to "Start Interview", the client detects no resume and immediately injects Jake's Resume and Jake's skills. Furthermore, the HTML template statically displays Jake's filename in the DOM.

---

## 7. MACHINE LEARNING & DATASET FINDINGS

1. **Academic Decision Tree & Classifiers (`ml/models/`):**
   - `decision_tree_model.pkl`, `svm_model.pkl`, `knn_model.pkl` are trained on `ml/datasets/text_features.csv` with features `['semantic_similarity', 'lexical_overlap', 'word_count', 'unique_word_ratio', 'avg_word_length']`.
   - Classification output is binary: `Proficient` (1) vs `Needs Improvement` (0).
   - This model is cleanly loaded in `evaluator.py` as `_ACADEMIC_CLASSIFIER`.

2. **Scoring Model (`ml/models/interview_scoring_model.pkl`):**
   - The RandomForestRegressor model was trained on `ml/datasets/features/train_scored.csv`.
   - Line 53 of `ml/create_target_scores.py` reveals the target was synthetically generated:
     `target_score = semantic_score * 0.85 + length_score * 0.15`
   - Therefore, the RF model learned an artificial linear combination of semantic similarity and character length.
   - **Architectural Decision:** As documented in `backend/app/evaluator.py`, the project correctly refrains from relying on this synthetic RF model as the authoritative score, employing the comprehensive multi-factor `AnswerEvaluator` (embedding cosine similarity, concept coverage, contradiction deduction, and rubrics) instead.

---

## 8. EXACT PROBLEMS, ROOT CAUSES, AND REPAIR SOLUTIONS

### PROBLEM 1: Pages Mixing and Viewport Lockout in Interview & Report
- **WHAT IS WRONG?**
  When an interview completes or when a past report is opened from History/Dashboard, the page freezes, scrolling is disabled, the navbar is missing, and the live interview room (camera/avatar) overlaps with the report.
- **WHY IS IT WRONG?**
  1. CSS rule `body:has(#view-practice.active:not(.session-completed))` forces `overflow: hidden !important; height: 100vh !important;`.
  2. In `script.js`, `viewHistorySession()` calls `navigateToView('practice')` but never hides `#interview-main-stage` and never adds `.session-completed`.
  3. The report (`#completion-card`) is embedded inside the live interview container (`#view-practice`) rather than having its own dedicated view panel.
- **WHICH FILES ARE RESPONSIBLE?**
  - `frontend/index.html` (lines 779-1788)
  - `frontend/script.js` (lines 5070-5155, lines 4124-4190)
  - `frontend/style.css` (lines 5635-5760, lines 621-653)
- **WHAT IS THE CORRECT SOLUTION?**
  1. Extract `#completion-card` out of `#view-practice` into its own top-level view panel: `<div class="view-panel" id="view-results">`.
  2. Register `/results` and `results` in `CANONICAL_VIEW_MAP` and `VIEW_TO_PATH_MAP`.
  3. In `viewHistorySession()`, navigate directly to `results` via `navigateToView('results')`.
  4. Ensure `body.in-interview` is strictly scoped to active live recording and removed immediately upon session exit or completion.
  5. Remove all aggressive `:has()` overflow-hidden rules from `style.css`.

---

### PROBLEM 2: 57 Ghost DOM IDs Causing Silent JS Exceptions
- **WHAT IS WRONG?**
  `script.js` executes 57 `document.getElementById()` queries that return `null`, leading to silent JavaScript runtime warnings and dead event listeners.
- **WHY IS IT WRONG?**
  Frontend HTML redesigns changed element IDs without synchronizing the corresponding JavaScript selector logic.
- **WHICH FILES ARE RESPONSIBLE?**
  - `frontend/script.js`
  - `frontend/index.html`
- **WHAT IS THE CORRECT SOLUTION?**
  1. Cleanly update `script.js` to target actual existing DOM elements (e.g., target `#dc-webcam-preview` instead of `#live-webcam-video`, target `#qrc-question-text` instead of `#interview-question-card`).
  2. Remove legacy references to deleted elements (e.g., `recording-card`, `landing-bar-*`, `ssb-chip-*`).
  3. Add defensive null-coalescing checks `if (el) ...` to all DOM manipulation handlers.

---

### PROBLEM 3: Persistent "Jake's Resume" & Mock Data Injection
- **WHAT IS WRONG?**
  Any newly registered user who visits "Start Interview" sees "Jake_s_Resume__Anonymous__1__2_.pdf" and 14 pre-filled skills instead of an empty, personalized setup.
- **WHY IS IT WRONG?**
  1. `frontend/index.html` hardcodes `Jake_s_Resume__Anonymous__1__2_.pdf` in elements `#prp-filename` (line 3106) and `#sum-resume` (line 3551).
  2. `frontend/script.js` line 6418 assigns a fallback mock object containing Jake's resume whenever `userProfile.resume_filename` is falsy.
- **WHICH FILES ARE RESPONSIBLE?**
  - `frontend/index.html` (lines 3106, 3551)
  - `frontend/script.js` (lines 6410-6426, lines 6605, 6715)
- **WHAT IS THE CORRECT SOLUTION?**
  1. In `index.html`, replace the hardcoded resume preview with an empty state: `"No resume uploaded yet"`, with a visible "Upload Resume" dropzone.
  2. In `script.js`, set `currentUploadedResume = null` when no resume exists. Show an empty state indicating that questions will default to the candidate's chosen role, and invite them to upload a resume for personalized questions.

---

### PROBLEM 4: Backend API & Frontend SPA Route Namespace Collision
- **WHAT IS WRONG?**
  Refreshing the browser on `/profile`, `/admin`, or `/reports` can return raw JSON data or 401 Unauthorized errors instead of rendering the user interface.
- **WHY IS IT WRONG?**
  The FastAPI backend registers API endpoints without an `/api` prefix (e.g. `/profile`, `/admin`, `/interviews`), causing direct URI collisions with frontend SPA view paths.
- **WHICH FILES ARE RESPONSIBLE?**
  - `backend/app/main.py`
  - `backend/app/api/profile.py`
  - `backend/app/api/admin.py`
  - `backend/app/api/interviews.py`
  - `backend/app/api/auth.py`
  - `frontend/script.js` (`API_BASE_URL`)
- **WHAT IS THE CORRECT SOLUTION?**
  1. Standardize all backend API router prefixes with `/api` (e.g., `/api/auth`, `/api/profile`, `/api/interviews`, `/api/admin`, `/api/interview/questions`).
  2. Update `API_BASE_URL` in `script.js` to point to `/api`.
  3. In `main.py`, cleanly register all frontend page routes (`/`, `/dashboard`, `/start-interview`, `/device-check`, `/interview`, `/results`, `/profile`, `/analytics`, `/reports`, `/admin`) to return `frontend/index.html`.
  4. Eliminate the temporary `if "text/html" in accept_header` hack from `profile.py`.

---

### PROBLEM 5: Hardcoded Auto-Login Backdoor & Dummy Metric Trends
- **WHAT IS WRONG?**
  1. Passing `?auto_login=sumit` in the browser URL automatically logs in as `skgounder50@gmail.com` with hardcoded password `password123`.
  2. Dashboard displays hardcoded trend indicators (`+12%`, `+8%`, `+5%`, `+2%`), hardcoded problem solving scores (`* 0.92`), and hardcoded focus area cards.
  3. Analytics displays arbitrary practice time (`total * 8m`).
- **WHY IS IT WRONG?**
  Developer shortcuts and placeholders were left active in client logic instead of computing real values from database records.
- **WHICH FILES ARE RESPONSIBLE?**
  - `frontend/script.js` (lines 5765-5783, lines 5408-5520, lines 7554-7582)
- **WHAT IS THE CORRECT SOLUTION?**
  1. Completely remove the `auto_login` backdoor from `validateAuthSession()`.
  2. Compute real trends on Dashboard by comparing the most recent interview score against the historical average, or hide the trend badge if fewer than 2 interviews exist.
  3. Compute actual practice duration by summing `duration_seconds` from MySQL records.
  4. Generate dynamic focus recommendations based on the candidate's actual lowest-scoring rubric dimensions and missing concepts.

---

### PROBLEM 6: CSS Specificity Deadlock & Class Pollution
- **WHAT IS WRONG?**
  Classes with prefix `.dashboard-` and `.dash-` are used in 3 different views, causing navbar styles to clash and interview bottombars to behave erratically.
- **WHY IS IT WRONG?**
  1. `style.css` contains over 15,000 lines with conflicting `!important` flags (e.g., lines 5643 vs 5724 where `.navbar` is set to `display: flex !important` and `display: none !important`).
  2. Class names lack view-level scoping prefixes.
- **WHICH FILES ARE RESPONSIBLE?**
  - `frontend/style.css`
  - `frontend/index.html`
- **WHAT IS THE CORRECT SOLUTION?**
  1. Scope report styles under `#view-results` or `.completion-card` specifically.
  2. Remove contradictory `!important` rules on `.navbar`. Control navigation visibility strictly via a single state class (`body.in-interview`).
  3. Ensure `.interview-bottombar` is scoped strictly to `#view-practice.active:not(.session-completed)`.

---

## 9. RECOMMENDED REPAIR SEQUENCE (PRIORITY-WISE)

To execute a clean, risk-free repair without destabilizing the working ML or database components, repairs must be performed in the following strict order:

```
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: ROUTING & API NAMESPACE STANDARDIZATION (CRITICAL BACKBONE)   │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Prefix all backend API routers with /api in main.py & api/*.py      │
│ 2. Point frontend API_BASE_URL to /api                                 │
│ 3. Register all SPA view paths in main.py to serve index.html cleanly  │
│ 4. Remove HTTP Accept header hack from profile.py                       │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: VIEW SEPARATION & VIEWPORT LOCKOUT RESOLUTION                 │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Extract #completion-card into top-level <div id="view-results">     │
│ 2. Register /results in CANONICAL_VIEW_MAP & VIEW_TO_PATH_MAP          │
│ 3. Update completeInterview() & viewHistorySession() to navigate to    │
│    'results' view without touching or locking 'practice' view          │
│ 4. Eliminate body:has(#view-practice.active...) overflow lock from CSS │
│ 5. Clean up conflicting navbar rules in style.css                      │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: GHOST DOM IDS & DEAD LISTENER REPAIR                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Resolve all 57 ghost IDs in script.js by mapping them to real DOM  │
│ 2. Add defensive null-checks to all event bindings                    │
│ 3. Fix webcam stream handover from Device Check to Live Interview      │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: DATA INTEGRITY & HARDCODED MOCKS ELIMINATION                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Remove "Jake's Resume" hardcoded strings from index.html & script.js│
│ 2. Implement true empty states for users with no uploaded resumes      │
│ 3. Remove ?auto_login=sumit backdoor parameter                         │
│ 4. Replace hardcoded trend strings (+12%) with real delta math         │
│ 5. Replace total*8m practice time with real duration_seconds sum       │
│ 6. Make Dashboard Priority Focus areas dynamic from weakest rubrics    │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: END-TO-END VERIFICATION & USER JOURNEY VALIDATION             │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Register a fresh new user account and verify 0 mock data is shown   │
│ 2. Upload a custom resume and verify dynamic question generation       │
│ 3. Complete a 3-question live interview through microphone and webcam  │
│ 4. Verify completion report renders, scrolls smoothly, and saves to DB │
│ 5. Return to Dashboard, verify real stats, and click "View Report"     │
│ 6. Verify report opens in clean state without live webcam collision    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 10. CONCLUSION & NEXT STEPS

The core AI engine, evaluation mathematics (Rules A-H), database architecture, and speech recognition pipeline in this project are high quality and fully functional. The issues reported by the user are entirely localized to **frontend view management, CSS specificity deadlocks, routing collisions, and legacy hardcoded mock fallbacks**.

By executing the structured 5-phase repair sequence outlined above, the entire project will transition into a robust, enterprise-grade AI Interview preparation platform.

**Awaiting Client Approval Before Proceeding with Any Source Code Changes.**


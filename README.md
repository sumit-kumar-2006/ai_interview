# AI Interview Analyzer — Production Platform

An AI-powered technical interview evaluation platform combining Whisper AI voice transcription, SentenceTransformers semantic similarity, RandomForestRegressor ML scoring (`ml/models/interview_scoring_model.pkl`), MediaPipe FaceMesh computer vision tracking, speech fluency analysis, candidate profile personalization, and XAMPP MySQL database persistence.

---

## Architecture Overview

```
                          ┌───────────────────────────┐
                          │   Frontend (Vanilla JS)   │
                          │   Stitch Design System    │
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │   FastAPI Backend Server  │
                          │  (Auth, Profile, Scoring) │
                          └─────────────┬─────────────┘
                                        │
       ┌────────────────────────────────┼────────────────────────────────┐
       │                                │                                │
       ▼                                ▼                                ▼
┌───────────────┐              ┌─────────────────┐             ┌───────────────────┐
│ Whisper AI    │              │ ML & NLP Engine │             │  MediaPipe Vision │
│ Audio Speech  │              │ (SentenceTrans- │             │ FaceMesh Landmark │
│ to Text       │              │ formers + RF)   │             │   Pose Tracking   │
└───────────────┘              └─────────────────┘             └───────────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │    XAMPP MySQL Server     │
                          │  (users, user_profiles,   │
                          │  interviews, results)     │
                          └───────────────────────────┘
```

---

## Key Features

1. **User Authentication & Authorization**:
   - `bcrypt` password hashing and PyJWT bearer token management.
   - User ownership isolation (`GET /interviews` returns only logged-in user's interviews).

2. **Candidate Profile & Personalization**:
   - Stores candidate target role, experience level, years of experience, technical skills, programming languages, projects, resume text, and target job description in MySQL.
   - Generates role-tailored technical questions dynamically.

3. **Multi-Modal AI Scoring Pipeline**:
   - **Speech-to-Text**: Whisper AI model transcribes spoken answers.
   - **Semantic Similarity**: `SentenceTransformer("all-MiniLM-L6-v2")` calculates cosine similarity against reference answers.
   - **ML Scoring Engine**: `ml/models/interview_scoring_model.pkl` (RandomForestRegressor 200 estimators) predicts answer scores using `semantic_similarity`, `question_length`, and `answer_length`.
   - **Speech Analysis**: Calculates words per minute (WPM), filler word breakdown, pause detection, and communication fluency.
   - **Computer Vision**: MediaPipe FaceMesh processes live webcam frames for face presence, head direction (Center/Left/Right/Up/Down), and camera visual attention percentage.

4. **Stitch Design UI**:
   - Deep Obsidian Slate theme (`#0b1326`) with Geist, Inter, and JetBrains Mono typography.
   - Translucent glassmorphism top navbar, browser frame webcam container, and interactive dashboard analytics.

---

## How to Run

### 1. Start XAMPP MySQL
Ensure XAMPP MySQL server is active on `localhost:3306` with database `ai_interview_analyzer`.

### 2. Start Backend API Server
```powershell
$env:PYTHONPATH="."
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Start Frontend Web Server
```powershell
python -m http.server 5500 --directory frontend
```

### 4. Open in Browser
Open `http://localhost:5500` or open `frontend/index.html` directly in your browser.

---

## Test Verification

Run the master automated verification suite:
```powershell
$env:PYTHONPATH="."
.\venv\Scripts\python.exe -u C:\Users\Sumit\.gemini\antigravity-ide\brain\d14a9669-ba8f-43e7-86fc-e777ba10b962\scratch\audit_and_test_all.py
```
# ai_interview
# ai_interview

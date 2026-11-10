# AI Interview Analyzer Architecture & Subsystem Guide

## System Components

### 1. ML Scoring Model (`ml/models/interview_scoring_model.pkl`)
- **Algorithm**: `RandomForestRegressor` (200 estimators).
- **Features**: `semantic_similarity`, `question_length`, `answer_length`.
- **Integration**: Loaded via `joblib` in `backend/app/evaluator.py` (`AnswerEvaluator`). Formats input features as `pandas.DataFrame` with exact column names to prevent `sklearn` feature name warnings.

### 2. NLP Semantic Analyzer (`nlp/answer_analyzer.py`)
- **Embeddings**: `SentenceTransformer("all-MiniLM-L6-v2")`.
- **Cosine Similarity**: Calculates semantic alignment between candidate response and reference answer.
- **Concept Coverage**: Extracts key technical terms and evaluates matched vs missing concepts.

### 3. Speech & Fluency Analyzer (`backend/app/speech_analyzer.py`)
- **Transcription**: OpenAI Whisper AI model.
- **Metrics**: Words per minute (WPM), filler word breakdown (`um`, `uh`, `like`, `you know`, `basically`, `actually`), pause duration detection, conciseness, and communication score.

### 4. Computer Vision Landmark Analyzer (`computer_vision/visual_analyzer.py`)
- **Webcam Feed**: Live WebRTC canvas processing.
- **MediaPipe FaceMesh**: Face presence percentage, camera attention percentage, head pose orientations (`Center`, `Left`, `Right`, `Up`, `Down`), and facial expression movement.

### 5. XAMPP MySQL Persistence & User Ownership
- **Database**: XAMPP MySQL `ai_interview_analyzer`.
- **Tables**: `users`, `user_profiles`, `interviews`, `question_results`.
- **Isolation**: JWT bearer token authentication ensures candidates can only access their own interviews and reports.

---

## Command Reference

### Start Backend API
```powershell
$env:PYTHONPATH="."
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Start Frontend Server
```powershell
python -m http.server 5500 --directory frontend
```

### Run Test Suite
```powershell
$env:PYTHONPATH="."
.\venv\Scripts\python.exe -u C:\Users\Sumit\.gemini\antigravity-ide\brain\d14a9669-ba8f-43e7-86fc-e777ba10b962\scratch\audit_and_test_all.py
```

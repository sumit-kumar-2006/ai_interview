from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query, Request
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import whisper
import tempfile
import os
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from typing import Optional
from sqlalchemy.orm import Session
from speech.transcribe import parse_whisper_result
from backend.app.evaluator import AnswerEvaluator
from nlp.answer_analyzer import extract_key_concepts
from backend.app.questions import get_interview_questions, generate_personalized_questions
from backend.app.speech_analyzer import SpeechAnalyzer
from computer_vision.visual_analyzer import process_visual_observations, VisualAnalysisRequest, VisualAnalysisResponse
from backend.app.database import create_database_if_not_exists, ensure_schema_updates, engine, Base, get_db
import backend.app.models  # Ensures all models (User, Interview, QuestionResult, UserProfile) are loaded into Base metadata
from backend.app.api import interviews, auth, profile
from backend.app.auth import get_current_user_optional
from backend.app.audio_validator import validate_audio_recording, SafeTemporaryAudioFile


MODEL_FILE = "ml/models/interview_scoring_model.pkl"

# ==============================
# APPLICATION LIFESPAN & INITIALIZATION
# ==============================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Ensuring MySQL database exists...")
    try:
        create_database_if_not_exists()
        print("Creating MySQL tables if they do not exist...")
        Base.metadata.create_all(bind=engine)
        ensure_schema_updates()
        print("Database startup initialization complete.")
    except Exception as e:
        print(f"Database initialization notice: {e}. Running API in stateless evaluation mode.")
    yield


app = FastAPI(
    title="AI Interview Analyzer API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Database API Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(interviews.router)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

if os.path.exists("frontend"):
    app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/")
def root_redirect(request: Request):
    qs = request.url.query
    target = f"/frontend/?{qs}" if qs else "/frontend/"
    return RedirectResponse(url=target)




# ==============================
# LOAD MODELS
# ==============================

print("Loading scoring model...")
scoring_model = joblib.load(MODEL_FILE)

print("Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Loading Whisper model...")
whisper_model = whisper.load_model("base")

print("All models loaded.")

print("Initializing AnswerEvaluator...")
evaluator = AnswerEvaluator(embedding_model)

print("Initializing SpeechAnalyzer...")
speech_analyzer = SpeechAnalyzer()


# ==============================
# REQUEST MODEL
# ==============================

class ScoreRequest(BaseModel):
    question: str
    candidate_answer: str
    reference_answer: str


# ==============================
# HEALTH
# ==============================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "AI Interview Analyzer"
    }


# ==============================
# INTERVIEW QUESTIONS
# ==============================

class QuestionsRequest(BaseModel):
    count: Optional[int] = 5
    difficulty: Optional[str] = None
    role: Optional[str] = None
    experience_level: Optional[str] = None
    interview_type: Optional[str] = None
    parsed_resume: Optional[dict] = None

@app.get("/interview/questions")
def get_questions(
    count: int = Query(default=5, ge=1, le=20),
    difficulty: Optional[str] = None,
    role: Optional[str] = None,
    experience_level: Optional[str] = None,
    interview_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[backend.app.models.User] = Depends(get_current_user_optional)
):
    profile_dict = None
    if current_user:
        user_prof = db.query(backend.app.models.UserProfile).filter(backend.app.models.UserProfile.user_id == current_user.id).first()
        if user_prof:
            profile_dict = {
                "name": user_prof.name,
                "education": user_prof.education,
                "college": user_prof.college,
                "experience_type": user_prof.experience_type,
                "years_of_experience": user_prof.years_of_experience,
                "target_role": role or user_prof.target_role,
                "skills": user_prof.skills,
                "programming_languages": user_prof.programming_languages,
                "projects": user_prof.projects,
                "resume_text": user_prof.resume_text,
                "resume_filename": user_prof.resume_filename,
                "parsed_resume": user_prof.parsed_resume,
                "job_description": user_prof.job_description,
                "interview_difficulty": difficulty or user_prof.interview_difficulty,
                "experience_level": experience_level,
                "interview_type": interview_type
            }
    elif role or difficulty:
        profile_dict = {
            "target_role": role or "Software Engineer",
            "interview_difficulty": difficulty or "Intermediate",
            "experience_level": experience_level or "Mid Level",
            "interview_type": interview_type or "Mixed Interview"
        }

    raw_questions = generate_personalized_questions(
        profile_data=profile_dict,
        num_questions=count,
        difficulty=difficulty,
        role=role,
        experience_level=experience_level,
        interview_type=interview_type,
        db=db
    )

    if not raw_questions:
        raise HTTPException(
            status_code=404,
            detail="No suitable academic interview questions found in active pool."
        )

    # Strictly serialize via QuestionPublic: NEVER expose reference_answer or evaluation_spec!
    public_questions = []
    for q in raw_questions:
        public_questions.append({
            "id": q["id"],
            "question": q["question"],
            "question_text": q.get("question_text", q["question"]),
            "source_id": q.get("source_id", ""),
            "category": q.get("category", "Academic Technical"),
            "difficulty": q.get("difficulty", difficulty or "Medium"),
            "role": q.get("role", role or "Software Engineer"),
            "skill": q.get("skill")
        })

    return {
        "status": "success",
        "personalized": profile_dict is not None,
        "count": len(public_questions),
        "questions": public_questions
    }


@app.post("/interview/questions")
def get_questions_post(
    req: QuestionsRequest,
    db: Session = Depends(get_db),
    current_user: Optional[backend.app.models.User] = Depends(get_current_user_optional)
):
    valid_count = max(1, min(int(req.count or 5), 20))

    profile_dict = None
    if current_user:
        user_prof = db.query(backend.app.models.UserProfile).filter(backend.app.models.UserProfile.user_id == current_user.id).first()
        if user_prof:
            profile_dict = {
                "name": user_prof.name,
                "education": user_prof.education,
                "college": user_prof.college,
                "experience_type": user_prof.experience_type,
                "years_of_experience": user_prof.years_of_experience,
                "target_role": req.role or user_prof.target_role,
                "skills": user_prof.skills,
                "programming_languages": user_prof.programming_languages,
                "projects": user_prof.projects,
                "resume_text": user_prof.resume_text,
                "resume_filename": user_prof.resume_filename,
                "parsed_resume": req.parsed_resume or user_prof.parsed_resume,
                "job_description": user_prof.job_description,
                "interview_difficulty": req.difficulty or user_prof.interview_difficulty,
                "experience_level": req.experience_level,
                "interview_type": req.interview_type
            }
    if not profile_dict:
        profile_dict = {
            "target_role": req.role or "Software Engineer",
            "interview_difficulty": req.difficulty or "Intermediate",
            "experience_level": req.experience_level or "Mid Level",
            "interview_type": req.interview_type or "Mixed Interview",
            "parsed_resume": req.parsed_resume
        }
    elif req.parsed_resume:
        profile_dict["parsed_resume"] = req.parsed_resume

    raw_questions = generate_personalized_questions(
        profile_data=profile_dict,
        num_questions=valid_count,
        difficulty=req.difficulty,
        role=req.role,
        experience_level=req.experience_level,
        interview_type=req.interview_type,
        db=db
    )

    if not raw_questions:
        raise HTTPException(
            status_code=404,
            detail="No suitable academic interview questions found in active pool."
        )

    # Strictly serialize via QuestionPublic: NEVER expose reference_answer or evaluation_spec!
    public_questions = []
    for q in raw_questions:
        public_questions.append({
            "id": q["id"],
            "question": q["question"],
            "question_text": q.get("question_text", q["question"]),
            "source_id": q.get("source_id", ""),
            "category": q.get("category", "Academic Technical"),
            "difficulty": q.get("difficulty", req.difficulty or "Medium"),
            "role": q.get("role", req.role or "Software Engineer"),
            "skill": q.get("skill")
        })

    return {
        "status": "success",
        "personalized": profile_dict is not None,
        "count": len(public_questions),
        "questions": public_questions
    }


# ==============================
# ENVIRONMENT & SECURITY CONFIGURATION
# ==============================

def is_legacy_scoring_enabled() -> bool:
    """
    Checks if legacy score prediction is permitted.
    In production (default), legacy evaluation endpoint is disabled to prevent
    bypassing canonical server-side database ground truth evaluation.
    Only enabled when ALLOW_LEGACY_SCORING='true' or APP_ENV='testing'.
    """
    env = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "production")).lower()
    return env == "testing" or os.getenv("ALLOW_LEGACY_SCORING", "false").lower() == "true"


def is_test_fallback_allowed() -> bool:
    """
    Checks if the standalone unit-test fallback is permitted on /evaluate-answer.
    In production (default), 'question_id' is strictly mandatory and all evaluations MUST
    retrieve canonical reference answers server-side from MySQL.
    The fallback is strictly restricted to isolated test runners when
    ALLOW_TEST_FALLBACK='true' or APP_ENV='testing'.
    """
    env = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "production")).lower()
    return env == "testing" or os.getenv("ALLOW_TEST_FALLBACK", "false").lower() == "true"


# ==============================
# LEGACY TEXT SCORE
# ==============================

@app.post("/predict-score")
def predict_score(request: ScoreRequest):
    if not is_legacy_scoring_enabled():
        raise HTTPException(
            status_code=403,
            detail="Legacy evaluation endpoint '/predict-score' is disabled in production. Use canonical '/evaluate-answer' with a valid question_id."
        )

    eval_result = evaluator.evaluate(
        question=request.question,
        candidate_answer=request.candidate_answer,
        reference_answer=request.reference_answer
    )

    answer_embedding = embedding_model.encode([request.candidate_answer])
    reference_embedding = embedding_model.encode([request.reference_answer])
    question_embedding = embedding_model.encode([request.question])

    question_similarity = float(cosine_similarity(question_embedding, answer_embedding)[0][0])
    reference_similarity = float(cosine_similarity(reference_embedding, answer_embedding)[0][0])

    sem_similarity_for_rf = reference_similarity if (request.reference_answer and request.reference_answer.strip()) else question_similarity
    features = pd.DataFrame([{
        "semantic_similarity": max(0.0, min(1.0, sem_similarity_for_rf)),
        "question_length": len(request.question),
        "answer_length": len(request.candidate_answer)
    }])

    try:
        rf_predicted = float(np.clip(scoring_model.predict(features)[0], 0, 100))
    except Exception:
        rf_predicted = eval_result["final_score"]

    return {
        "question_similarity": round(question_similarity, 4),
        "reference_similarity": round(reference_similarity, 4),
        "question_length": len(request.question),
        "answer_length": len(request.candidate_answer),
        "predicted_score": round(rf_predicted, 2),
        "rf_predicted_score": round(rf_predicted, 2),
        "evaluation": eval_result
    }


class EvaluateAnswerRequest(BaseModel):
    question_id: Optional[int] = None
    question: Optional[str] = ""
    candidate_answer: str
    reference_answer: Optional[str] = ""  # Client-supplied value is ignored for security
    evaluation_spec: Optional[dict] = None  # Client-supplied rubric is ignored for security
    speech_analysis: Optional[dict] = None
    visual_analysis: Optional[dict] = None
    attempt_number: Optional[int] = 1


# ==============================
# ANSWER EVALUATION (STAGE 2: SECURE MULTI-FACTOR EVALUATION)
# ==============================

@app.post("/evaluate-answer")
def evaluate_answer(
    req: EvaluateAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Stage 2: Evaluates the candidate's submitted answer with strict backend security:
    - Retrieves the true reference answer directly from the MySQL database.
    - Completely ignores any reference answer or rubric supplied by the client.
    - Validates empty answers, invalid question IDs, and inactive questions.
    - Strictly omits the reference answer and rubric from the returned JSON response.
    """
    cand_text = (req.candidate_answer or "").strip()

    # Rule E: Empty answer or whitespace detection
    if not cand_text:
        return {
            "status": "success",
            "question_id": req.question_id,
            "score": 0.0,
            "predicted_score": 0.0,
            "final_score": 0.0,
            "technical_score": 0.0,
            "relevance_score": 0.0,
            "concept_coverage": 0.0,
            "completeness": 0.0,
            "semantic_similarity": 0.0,
            "correct_concepts": [],
            "missing_concepts": [],
            "incorrect_claims": [],
            "strengths": [],
            "weaknesses": ["No answer provided. Please articulate your technical response to receive evaluation."],
            "areas_for_improvement": ["No answer provided."],
            "explanation": "No response was recorded for evaluation.",
            "ai_feedback": "Please speak or write your answer clearly before submitting.",
            "improvement_suggestions": ["Ensure your microphone is active and provide a substantive explanation."],
            "speech_analysis": req.speech_analysis or {},
            "visual_analysis": req.visual_analysis or {},
            "attempt_number": req.attempt_number or 1
        }

    actual_question = ""
    actual_ref_answer = ""
    actual_spec = None

    if req.question_id is not None:
        if req.question_id <= 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid question_id. Must be a positive integer."
            )

        # 1. Secure Server-Side Lookup by question_id
        q_obj = db.query(backend.app.models.Question).filter(
            backend.app.models.Question.id == req.question_id
        ).first()

        if not q_obj:
            raise HTTPException(
                status_code=404,
                detail=f"Question with ID {req.question_id} not found in question bank."
            )

        if q_obj.is_active != 1:
            raise HTTPException(
                status_code=400,
                detail=f"Question with ID {req.question_id} is inactive or quarantined and cannot be used for live evaluation."
            )

        actual_question = q_obj.question_text
        actual_ref_answer = q_obj.reference_answer
        key_concepts = extract_key_concepts(actual_ref_answer)
        actual_spec = {
            "expected_answer": actual_ref_answer,
            "required_concepts": key_concepts[:5],
            "rubric": {"accuracy": 60, "clarity": 40}
        }
    else:
        # question_id is missing: strictly forbidden in production
        if not is_test_fallback_allowed():
            raise HTTPException(
                status_code=400,
                detail="Field 'question_id' is mandatory. Answer evaluation must reference a verified academic question from the database."
            )

        # Standalone isolated unit-test fallback (strictly forbidden in production)
        if req.question and req.question.strip():
            # 2. Lookup by question text in active database pool
            q_match = db.query(backend.app.models.Question).filter(
                backend.app.models.Question.question_text == req.question.strip(),
                backend.app.models.Question.is_active == 1
            ).first() if db else None

            if q_match:
                actual_question = q_match.question_text
                actual_ref_answer = q_match.reference_answer
                key_concepts = extract_key_concepts(actual_ref_answer)
                actual_spec = {
                    "expected_answer": actual_ref_answer,
                    "required_concepts": key_concepts[:5],
                    "rubric": {"accuracy": 60, "clarity": 40}
                }
            else:
                # Fallback for standalone rule test harnesses with custom test strings
                actual_question = req.question.strip()
                actual_ref_answer = req.reference_answer or ""
                actual_spec = req.evaluation_spec
        else:
            raise HTTPException(
                status_code=400,
                detail="Field 'question_id' is mandatory for answer evaluation."
            )

    # Perform evaluation against verified reference answer
    eval_result = evaluator.evaluate(
        question=actual_question,
        candidate_answer=cand_text,
        reference_answer=actual_ref_answer,
        evaluation_spec=actual_spec
    )

    # Optional RF estimation for informational telemetry (computed securely by AnswerEvaluator)
    rf_score = eval_result.get("rf_predicted_score")

    # Secure Response: reference_answer, expected_answer, and confidential rubric are OMITTED!
    return {
        "status": "success",
        "question_id": req.question_id,
        "score": eval_result["final_score"],
        "predicted_score": eval_result["final_score"],
        "rf_predicted_score": rf_score,
        "academic_classification": eval_result.get("academic_classification"),
        "academic_confidence": eval_result.get("academic_confidence"),
        "final_score": eval_result["final_score"],
        "technical_score": eval_result["final_score"],
        "relevance_score": eval_result["relevance_score"],
        "concept_coverage": eval_result["concept_coverage"],
        "completeness": eval_result.get("completeness", eval_result.get("final_score", 0.0)),
        "semantic_similarity": eval_result["semantic_similarity"],
        "correct_concepts": eval_result.get("correct_concepts", []),
        "missing_concepts": eval_result.get("missing_concepts", []),
        "incorrect_claims": eval_result.get("incorrect_claims", []),
        "contradictions_detected": eval_result.get("contradictions_detected", []),
        "has_contradiction": eval_result.get("has_contradiction", False),
        "strengths": eval_result.get("strengths", []),
        "weaknesses": eval_result.get("weaknesses", []),
        "areas_for_improvement": eval_result.get("weaknesses", []),
        "explanation": eval_result.get("explanation", ""),
        "ai_feedback": eval_result.get("feedback", ""),
        "improvement_suggestions": eval_result.get("improvement_suggestions", []),
        "speech_analysis": req.speech_analysis or {},
        "visual_analysis": req.visual_analysis or {},
        "attempt_number": req.attempt_number or 1
    }


# ==============================
# AUDIO RECORDING VALIDATION & UPLOAD (PART B STEP 4)
# ==============================

@app.post("/interview/audio/upload")
async def upload_interview_audio(
    audio: UploadFile = File(...),
    question_id: Optional[int] = Form(None),
    duration_seconds: Optional[float] = Form(None),
    current_user: Optional[backend.app.models.User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Validates uploaded audio recording for interview questions.
    Performs server-side validation on MIME type, container magic bytes,
    file size (max 25MB), and duration (1.0s to 300.0s).
    Does NOT modify Whisper or perform STT (strictly reserved for Step 5).
    Does NOT leak reference answers, rubrics, or evaluation specifications.
    """
    # 1. Verify question_id if provided
    if question_id is not None:
        if question_id <= 0:
            raise HTTPException(
                status_code=400,
                detail="Field 'question_id' must be a positive integer."
            )
        q_obj = db.query(backend.app.models.Question).filter(
            backend.app.models.Question.id == question_id
        ).first()
        if not q_obj:
            raise HTTPException(
                status_code=404,
                detail=f"Question with ID {question_id} not found in question bank."
            )
        if q_obj.is_active != 1:
            raise HTTPException(
                status_code=400,
                detail=f"Question with ID {question_id} is inactive or quarantined and cannot be used."
            )

    # 2. Read content safely
    content = await audio.read()

    # 3. Server-side Audio Validation (MIME, magic bytes, size, duration)
    validation_info = validate_audio_recording(
        content=content,
        filename=audio.filename,
        content_type=audio.content_type,
        reported_duration=duration_seconds
    )

    # 4. Safe temporary lifecycle test
    with SafeTemporaryAudioFile(content, suffix=validation_info["format"]) as temp_audio_path:
        assert os.path.exists(temp_audio_path), "Temporary file must exist during active scope"

    # Temporary file is guaranteed to be deleted immediately after context exit
    return {
        "status": "valid",
        "message": "Audio recording validated successfully.",
        "filename": validation_info["sanitized_filename"],
        "format": validation_info["format"],
        "content_type": validation_info["content_type"],
        "size_bytes": validation_info["size_bytes"],
        "duration_seconds": validation_info["duration_seconds"],
        "question_id": question_id
    }


# ==============================
# AUDIO TRANSCRIPTION (PART B STEP 5 DECOUPLED STT)
# ==============================

@app.post("/transcribe-audio")
@app.post("/interview/audio/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    question_id: Optional[int] = Form(None),
    session_id: Optional[int] = Form(None),
    current_user: Optional[backend.app.models.User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Decoupled Speech-to-Text transcription endpoint.
    Performs server-side validation on audio format, magic bytes, and duration.
    Transcribes audio using Whisper AI without triggering immediate answer grading.
    Returns verbatim transcript and speech fluency metrics for candidate review and editing.
    """
    # 1. Validate question_id if provided
    if question_id is not None:
        if question_id <= 0:
            raise HTTPException(
                status_code=400,
                detail="Field 'question_id' must be a positive integer."
            )
        q_obj = db.query(backend.app.models.Question).filter(
            backend.app.models.Question.id == question_id
        ).first()
        if not q_obj:
            raise HTTPException(
                status_code=404,
                detail=f"Question with ID {question_id} not found in question bank."
            )

    # 2. Read audio content safely
    content = await audio.read()

    # 3. Server-side Audio Validation (MIME, magic bytes, size, duration)
    validation_info = validate_audio_recording(
        content=content,
        filename=audio.filename,
        content_type=audio.content_type
    )

    # 4. Transcribe safely within temporary file scope
    suffix = f".{validation_info['format']}"
    with SafeTemporaryAudioFile(content, suffix=suffix) as temp_audio_path:
        # Run Whisper STT in worker thread to prevent blocking FastAPI async event loop
        result = await run_in_threadpool(whisper_model.transcribe, temp_audio_path)
        candidate_answer, speech_detected = parse_whisper_result(result)
        speech_analysis = speech_analyzer.analyze(result, temp_audio_path)

    # 5. Handle empty or no-speech audio
    if not speech_detected or not candidate_answer:
        return {
            "status": "no_speech",
            "speech_detected": False,
            "transcript": "",
            "message": "No speech detected in audio recording. Please speak clearly into your microphone.",
            "speech_analysis": speech_analysis,
            "audio_metadata": validation_info
        }

    return {
        "status": "success",
        "speech_detected": True,
        "transcript": candidate_answer,
        "message": "Audio transcribed successfully.",
        "speech_analysis": speech_analysis,
        "language": result.get("language", "en"),
        "audio_metadata": validation_info
    }


# ==============================
# AUDIO → TRANSCRIPT → SCORE
# ==============================

@app.post("/transcribe-and-score")
async def transcribe_and_score(
    audio: UploadFile = File(...),
    question: str = Form(...),
    reference_answer: str = Form(...)
):

    temp_path = None

    try:
        content = await audio.read()

        # Validate uploaded audio payload before downstream processing
        validate_audio_recording(
            content=content,
            filename=audio.filename,
            content_type=audio.content_type
        )

        # Save uploaded audio temporarily
        suffix = os.path.splitext(
            audio.filename or ".wav"
        )[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_path = temp_file.name
            temp_file.write(content)

        # ==============================
        # WHISPER TRANSCRIPTION & NO-SPEECH CHECK
        # ==============================

        result = await run_in_threadpool(
            whisper_model.transcribe,
            temp_path
        )

        candidate_answer, speech_detected = parse_whisper_result(result)
        speech_analysis = speech_analyzer.analyze(result, temp_path)

        # 1. No speech detected or empty transcript
        if not speech_detected or not candidate_answer:
            empty_eval = {
                "relevance_score": 0.0,
                "semantic_similarity": 0.0,
                "answer_completeness": 0.0,
                "concept_coverage": 0.0,
                "final_score": 0.0,
                "strengths": [],
                "weaknesses": ["No speech or answer detected."],
                "feedback": "No answer detected. Please record your answer and try again."
            }
            return {
                "filename": audio.filename or "audio.wav",
                "transcript": "",
                "speech_detected": False,
                "question_similarity": 0,
                "reference_similarity": 0,
                "question_length": len(question),
                "answer_length": 0,
                "predicted_score": 0,
                "status": "no_answer",
                "message": "No answer detected. Please record your answer and try again.",
                "evaluation": empty_eval,
                "speech_analysis": speech_analysis
            }

        # 2. Fewer than 3 meaningful words validation
        words = [w for w in candidate_answer.split() if w.strip()]
        if len(words) < 3:
            short_eval = {
                "relevance_score": 0.0,
                "semantic_similarity": 0.0,
                "answer_completeness": 0.0,
                "concept_coverage": 0.0,
                "final_score": 0.0,
                "strengths": [],
                "weaknesses": ["Answer is too short to evaluate."],
                "feedback": "Answer too short. Please provide a more complete answer."
            }
            return {
                "filename": audio.filename or "audio.wav",
                "transcript": candidate_answer,
                "speech_detected": True,
                "question_similarity": 0,
                "reference_similarity": 0,
                "question_length": len(question),
                "answer_length": len(candidate_answer),
                "predicted_score": 0,
                "status": "answer_too_short",
                "message": "Answer too short. Please provide a more complete answer.",
                "evaluation": short_eval,
                "speech_analysis": speech_analysis
            }

        # ==============================
        # EVALUATE WITH ANSWER EVALUATOR
        # ==============================
        eval_result = evaluator.evaluate(
            question=question,
            candidate_answer=candidate_answer,
            reference_answer=reference_answer
        )

        return {
            "filename": audio.filename or "audio.wav",
            "transcript": candidate_answer,
            "speech_detected": True,
            "question_similarity": round(
                eval_result["relevance_score"] / 100.0, 4
            ),
            "reference_similarity": round(
                eval_result["semantic_similarity"] / 100.0, 4
            ),
            "question_length": len(question),
            "answer_length": len(candidate_answer),
            "predicted_score": eval_result["final_score"],
            "relevance_score": eval_result["relevance_score"],
            "concept_coverage": eval_result["concept_coverage"],
            "completeness": eval_result.get("completeness", eval_result.get("final_score", 0.0)),
            "strengths": eval_result["strengths"],
            "areas_for_improvement": eval_result["weaknesses"],
            "ai_feedback": eval_result["feedback"],
            "status": "success",
            "evaluation": eval_result,
            "speech_analysis": speech_analysis
        }

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/visual-analysis", response_model=VisualAnalysisResponse)
def analyze_visual_signals(req: VisualAnalysisRequest):
    """
    Endpoint for analyzing aggregated live webcam observations collected during an interview question answer.
    Does NOT alter /predict-score or ML models.
    """
    result = process_visual_observations(req.dict())
    return result


# ==============================
# STATIC FILES (FRONTEND)
# ==============================
from fastapi.staticfiles import StaticFiles

if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")




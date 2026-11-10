import math
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, field_validator, ConfigDict, EmailStr

def sanitize_float(v: Optional[float]) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (float, int)):
        if math.isnan(v) or math.isinf(v):
            return None
        return float(v)
    return None

# ==============================
# AUTH SCHEMAS
# ==============================

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ==============================
# PROFILE SCHEMAS
# ==============================

class UserProfileBase(BaseModel):
    name: Optional[str] = None
    education: Optional[str] = None
    college: Optional[str] = None
    experience_type: Optional[str] = "Fresher"
    years_of_experience: Optional[float] = 0.0
    target_role: Optional[str] = "Software Engineer"
    skills: Optional[str] = None
    programming_languages: Optional[str] = None
    projects: Optional[str] = None
    resume_text: Optional[str] = None
    resume_filename: Optional[str] = None
    parsed_resume: Optional[Dict[str, Any]] = None
    job_description: Optional[str] = None
    interview_difficulty: Optional[str] = "Intermediate"

    @field_validator("years_of_experience", mode="before")
    @classmethod
    def clean_floats(cls, v: Any) -> Optional[float]:
        return sanitize_float(v)

    @field_validator("skills", mode="before")
    @classmethod
    def clean_skills(cls, v: Any) -> Optional[str]:
        if isinstance(v, list):
            return ", ".join(str(s) for s in v if s)
        return str(v) if v is not None else None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ResumeUploadResponse(BaseModel):
    status: str
    message: str
    filename: str
    char_count: int
    word_count: int
    profile_summary: str
    parsed_resume: Dict[str, Any]
    profile: UserProfileResponse


# ==============================
# INTERVIEW SCHEMAS
# ==============================

class QuestionResultBase(BaseModel):
    question_number: int
    question: str
    reference_answer: Optional[str] = None
    transcript: Optional[str] = None
    final_score: Optional[float] = None
    semantic_similarity: Optional[float] = None
    relevance_score: Optional[float] = None
    concept_coverage: Optional[float] = None
    completeness: Optional[float] = None
    communication_score: Optional[float] = None
    ai_feedback: Optional[str] = None
    strengths: Optional[List[Any]] = None
    areas_for_improvement: Optional[List[Any]] = None
    speech_analysis: Optional[Dict[str, Any]] = None
    visual_analysis: Optional[Dict[str, Any]] = None
    evaluation_spec: Optional[Dict[str, Any]] = None
    correct_concepts: Optional[List[Any]] = None
    missing_concepts: Optional[List[Any]] = None
    incorrect_claims: Optional[List[Any]] = None
    rubric_scores: Optional[Dict[str, Any]] = None
    attempt_count: Optional[int] = 1

    @field_validator(
        "final_score",
        "semantic_similarity",
        "relevance_score",
        "concept_coverage",
        "completeness",
        "communication_score",
        mode="before"
    )
    @classmethod
    def clean_floats(cls, v: Any) -> Optional[float]:
        return sanitize_float(v)

class QuestionResultCreate(QuestionResultBase):
    pass

class QuestionResultResponse(QuestionResultBase):
    id: int
    interview_id: int

    model_config = ConfigDict(from_attributes=True)

class InterviewBase(BaseModel):
    duration_seconds: Optional[float] = None
    overall_score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    questions_answered: int = 0
    questions_skipped: int = 0
    completed_at: Optional[datetime] = None
    resume_filename: Optional[str] = None
    parsed_resume: Optional[Dict[str, Any]] = None

    @field_validator("duration_seconds", "overall_score", "technical_score", "communication_score", mode="before")
    @classmethod
    def clean_floats(cls, v: Any) -> Optional[float]:
        return sanitize_float(v)

class InterviewCreate(InterviewBase):
    question_results: List[QuestionResultCreate] = []

class InterviewResponse(InterviewBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    question_results: List[QuestionResultResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ==============================
# QUESTION BANK SCHEMAS
# ==============================

class QuestionPublic(BaseModel):
    """Public-facing question schema. Strictly omits reference_answer for candidate integrity."""
    id: int
    source_id: str
    question_text: str
    skill: Optional[str] = None
    role: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class QuestionInternal(QuestionPublic):
    """Backend-only question schema. Includes reference_answer and source provenance."""
    reference_answer: str
    source_dataset: str
    source_version: str
    is_active: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

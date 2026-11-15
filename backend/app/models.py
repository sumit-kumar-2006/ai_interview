from datetime import datetime
from sqlalchemy import Column, Integer, Float, Text, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    interviews = relationship(
        "Interview",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Interview.created_at.desc()"
    )

    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    name = Column(String(255), nullable=True)
    education = Column(String(255), nullable=True)
    college = Column(String(255), nullable=True)
    experience_type = Column(String(100), default="Fresher", nullable=True)
    years_of_experience = Column(Float, default=0.0, nullable=True)
    target_role = Column(String(255), default="Software Engineer", nullable=True)
    skills = Column(Text, nullable=True)
    programming_languages = Column(Text, nullable=True)
    projects = Column(Text, nullable=True)
    resume_text = Column(Text, nullable=True)
    resume_filename = Column(String(255), nullable=True)
    parsed_resume = Column(JSON, nullable=True)
    job_description = Column(Text, nullable=True)
    interview_difficulty = Column(String(50), default="Intermediate", nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="profile")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    resume_filename = Column(String(255), nullable=True)
    parsed_resume = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    questions_answered = Column(Integer, default=0, nullable=False)
    questions_skipped = Column(Integer, default=0, nullable=False)

    target_role = Column(String(255), nullable=True)
    experience_level = Column(String(100), nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)

    user = relationship("User", back_populates="interviews")

    question_results = relationship(
        "QuestionResult",
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="QuestionResult.question_number"
    )

class QuestionResult(Base):
    __tablename__ = "question_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interview_id = Column(
        Integer,
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question_number = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    reference_answer = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    final_score = Column(Float, nullable=True)
    semantic_similarity = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    concept_coverage = Column(Float, nullable=True)
    completeness = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    
    # MySQL JSON columns
    strengths = Column(JSON, nullable=True)
    areas_for_improvement = Column(JSON, nullable=True)
    speech_analysis = Column(JSON, nullable=True)
    visual_analysis = Column(JSON, nullable=True)
    evaluation_spec = Column(JSON, nullable=True)
    correct_concepts = Column(JSON, nullable=True)
    missing_concepts = Column(JSON, nullable=True)
    incorrect_claims = Column(JSON, nullable=True)
    rubric_scores = Column(JSON, nullable=True)
    attempt_count = Column(Integer, default=1, nullable=True)

    interview = relationship("Interview", back_populates="question_results")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_id = Column(String(64), unique=True, index=True, nullable=False)
    question_text = Column(Text, nullable=False)
    reference_answer = Column(Text, nullable=False)
    skill = Column(String(100), nullable=True, index=True)
    role = Column(String(100), nullable=True, index=True)
    difficulty = Column(String(50), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    source_dataset = Column(String(100), nullable=False)
    source_version = Column(String(50), default="1.0", nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)



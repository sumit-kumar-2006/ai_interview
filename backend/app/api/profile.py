from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Response
from sqlalchemy.orm import Session, joinedload
import os

from backend.app.database import get_db
from backend.app.models import User, UserProfile, Interview, QuestionResult
from backend.app.schemas import UserProfileUpdate, UserProfileResponse, ResumeUploadResponse
from backend.app.auth import get_current_user, get_current_user_optional
from backend.app.services.resume_parser import (
    parse_resume,
    ALLOWED_RESUME_EXTENSIONS,
    MAX_RESUME_FILE_SIZE_BYTES,
    sanitize_filename
)
from backend.app.services.pdf_generator import render_profile_analytics_pdf

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("", response_model=UserProfileResponse)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve current candidate's profile. Creates default profile if missing."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        profile = UserProfile(
            user_id=current_user.id,
            name=current_user.full_name or current_user.email.split('@')[0],
            education="",
            college="",
            experience_type="Fresher",
            years_of_experience=0.0,
            target_role="Software Engineer",
            skills="Python, JavaScript, SQL",
            programming_languages="Python, JavaScript",
            projects="",
            resume_text="",
            resume_filename=None,
            parsed_resume=None,
            job_description="",
            interview_difficulty="Intermediate"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
    return profile

@router.put("", response_model=UserProfileResponse)
def update_user_profile(
    profile_in: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update current candidate's profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    update_data = profile_in.model_dump(exclude_unset=True)

    if not profile:
        profile = UserProfile(
            user_id=current_user.id,
            **update_data
        )
        db.add(profile)
    else:
        for field, value in update_data.items():
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Upload and intelligently analyze candidate resume (PDF, DOCX, TXT).
    Extracts skills, projects, experience, education, certifications, and updates candidate profile.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename must not be empty."
        )

    ext = os.path.splitext(file.filename.lower())[1]
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Please upload a .pdf, .docx, or .txt file."
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_RESUME_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file exceeds the maximum 10MB size limit."
        )

    if len(file_bytes) < 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty or corrupted."
        )

    try:
        parsed_data = parse_resume(file_bytes, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unable to parse resume: {str(e)}"
        )

    safe_name = sanitize_filename(file.filename)
    skills_str = parsed_data.get("skills_text") or (", ".join(parsed_data["skills"]) if isinstance(parsed_data.get("skills"), list) else str(parsed_data.get("skills") or ""))

    # Persist to database if authenticated
    if current_user:
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            profile = UserProfile(
                user_id=current_user.id,
                name=parsed_data.get("candidate_name") or current_user.full_name or current_user.email.split('@')[0],
                target_role=parsed_data.get("target_role") or "Software Engineer",
                experience_type=parsed_data.get("experience_type") or "Fresher",
                years_of_experience=parsed_data.get("years_of_experience") or 0.0,
                skills=skills_str,
                programming_languages=parsed_data.get("programming_languages"),
                projects=parsed_data.get("projects_summary"),
                education=parsed_data.get("education_summary"),
                resume_text=parsed_data.get("raw_text"),
                resume_filename=safe_name,
                parsed_resume=parsed_data,
                interview_difficulty="Intermediate"
            )
            db.add(profile)
        else:
            if parsed_data.get("candidate_name") and (not profile.name or profile.name == "Candidate"):
                profile.name = parsed_data.get("candidate_name")
            if parsed_data.get("target_role"):
                profile.target_role = parsed_data.get("target_role")
            if skills_str:
                profile.skills = skills_str
            if parsed_data.get("programming_languages"):
                profile.programming_languages = parsed_data.get("programming_languages")
            if parsed_data.get("projects_summary"):
                profile.projects = parsed_data.get("projects_summary")
            if parsed_data.get("education_summary"):
                profile.education = parsed_data.get("education_summary")
            if parsed_data.get("experience_type"):
                profile.experience_type = parsed_data.get("experience_type")
            if parsed_data.get("years_of_experience") is not None:
                profile.years_of_experience = parsed_data.get("years_of_experience")
            profile.resume_text = parsed_data.get("raw_text")
            profile.resume_filename = safe_name
            profile.parsed_resume = parsed_data

        db.commit()
        db.refresh(profile)
    else:
        # Ephemeral profile for guest user
        from datetime import datetime
        profile = UserProfile(
            id=0,
            user_id=0,
            name=parsed_data.get("candidate_name") or "Candidate",
            target_role=parsed_data.get("target_role") or "Software Engineer",
            experience_type=parsed_data.get("experience_type") or "Fresher",
            years_of_experience=parsed_data.get("years_of_experience") or 0.0,
            skills=skills_str,
            programming_languages=parsed_data.get("programming_languages"),
            projects=parsed_data.get("projects_summary"),
            education=parsed_data.get("education_summary"),
            resume_text=parsed_data.get("raw_text"),
            resume_filename=safe_name,
            parsed_resume=parsed_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    return {
        "status": "success",
        "message": "Resume uploaded and analyzed successfully.",
        "filename": safe_name,
        "char_count": parsed_data.get("char_count", 0),
        "word_count": parsed_data.get("word_count", 0),
        "profile_summary": parsed_data.get("profile_summary", ""),
        "parsed_resume": parsed_data,
        "profile": profile
    }


def _build_analytics_payload(current_user: User, profile: Optional[UserProfile], interviews: List[Interview], days: Optional[int] = None) -> Dict[str, Any]:
    """Helper to assemble structured analytics response for JSON API and PDF export."""
    total_count = len(interviews)
    total_seconds = sum(i.duration_seconds or 0 for i in interviews)
    hours = int(total_seconds // 3600)
    mins = int((total_seconds % 3600) // 60)
    duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

    scores = [float(i.overall_score) for i in interviews if i.overall_score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    best_score = round(max(scores), 1) if scores else 0.0
    latest_score = round(scores[0], 1) if scores else 0.0

    # Overall score derived from genuine completed interviews (matching Dashboard & Reports)
    overall_score = avg_score if total_count > 0 else 0.0

    # Extract metrics from actual QuestionResults across user's sessions
    comm_scores = []
    rel_scores = []
    tech_scores = []
    for inv in interviews:
        if inv.technical_score is not None:
            tech_scores.append(float(inv.technical_score))
        if inv.communication_score is not None:
            comm_scores.append(float(inv.communication_score))
        for qr in (getattr(inv, "question_results", None) or []):
            if qr.communication_score is not None:
                comm_scores.append(float(qr.communication_score))
            if qr.relevance_score is not None:
                rel_scores.append(float(qr.relevance_score))
            if qr.concept_coverage is not None:
                rel_scores.append(float(qr.concept_coverage))
            if qr.final_score is not None:
                tech_scores.append(float(qr.final_score))

    if total_count > 0:
        answer_quality = round(sum(rel_scores) / len(rel_scores), 1) if rel_scores else avg_score
        communication = round(sum(comm_scores) / len(comm_scores), 1) if comm_scores else avg_score
        question_perf = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else avg_score
        confidence = round(max(0.0, min(100.0, (communication * 0.55 + answer_quality * 0.45))), 1)
        visual_presence = round(max(0.0, min(100.0, communication * 0.92)), 1)
    else:
        answer_quality = 0.0
        communication = 0.0
        question_perf = 0.0
        confidence = 0.0
        visual_presence = 0.0

    # Chronological Trend Chart from real interview records
    chronological = sorted(
        [i for i in interviews if i.overall_score is not None],
        key=lambda x: x.completed_at or x.created_at or datetime.min
    )
    if chronological:
        sample = chronological[-7:] if len(chronological) > 7 else chronological
        trend_labels = [(i.completed_at or i.created_at).strftime("%b %d") for i in sample]
        trend_scores = [round(float(i.overall_score), 1) for i in sample]
        trend_avg_benchmarks = [75.0] * len(trend_scores)
    else:
        trend_labels = []
        trend_scores = []
        trend_avg_benchmarks = []

    joined_dt = current_user.created_at
    joined_str = joined_dt.strftime("%b %Y") if joined_dt else "Recent"

    recent_sessions = []
    for inv in interviews[:10]:
        dt = inv.completed_at or inv.created_at
        if dt:
            d_str = dt.strftime("%b ") + str(dt.day) + dt.strftime(", %Y • %I:%M %p").replace(" 0", " ")
        else:
            d_str = "Recent Session"
        recent_sessions.append({
            "id": inv.id,
            "target_role": inv.target_role or "Interview Session",
            "completed_at": dt.isoformat() if dt else None,
            "completed_at_str": d_str,
            "overall_score": round(float(inv.overall_score or 0.0), 1),
            "duration_seconds": inv.duration_seconds or 0,
            "questions_answered": inv.questions_answered or 1
        })

    # Actionable insights tailored to actual performance
    if total_count == 0:
        insights = [
            "Complete your first technical mock interview to unlock AI-powered speech, visual, and answer analysis.",
            "Upload your updated resume to receive personalized questions matching your actual projects and skills.",
            "Prepare your webcam and microphone in Device Check for optimal simulation."
        ]
        recommendations = [
            "Start with an Easy or Medium interview in your target role to establish a baseline score.",
            "Speak clearly into your microphone and articulate your architectural thought process.",
            "Review key data structures, algorithms, and system design patterns for your domain."
        ]
    elif avg_score >= 80:
        insights = [
            "Excellent overall technical fluency and conceptual clarity across your completed sessions.",
            "Your answers demonstrate strong grasp of core engineering principles and architectural trade-offs.",
            "Consistent pacing and minimal fillers reflect high interview confidence."
        ]
        recommendations = [
            "Practice advanced System Design and distributed scalability scenarios.",
            "Provide quantitative metrics from your production projects (e.g., latency reduction, throughput).",
            "Keep answers concise and prioritize the most impactful technical decisions first."
        ]
    elif avg_score >= 60:
        insights = [
            "Solid technical understanding with good engagement on foundational concepts.",
            "Some technical answers could benefit from greater depth and concrete implementation examples.",
            "Communication delivery is steady; continuing practice will reduce pause intervals."
        ]
        recommendations = [
            "Explicitly define required architectural terms and concepts before deep diving into details.",
            "Incorporate the STAR framework (Situation, Task, Action, Result) for scenario-based responses.",
            "Review domain-specific concepts flagged in your individual interview feedback reports."
        ]
    else:
        insights = [
            "Active practice engagement recorded. Technical accuracy requires additional reinforcement.",
            "Ensure answers directly target the question's core concepts rather than tangential topics.",
            "Focus on speaking at a steady, measured pace without rushing."
        ]
        recommendations = [
            "Review the reference concepts and rubric breakdowns provided in your detailed reports.",
            "Practice vocalizing your explanations out loud to improve fluency and conceptual recall.",
            "Retake sessions in specific topics until achieving 75%+ score consistency."
        ]

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name or (profile.name if profile else "Candidate"),
            "is_admin": bool(getattr(current_user, "is_admin", False))
        },
        "profile": {
            "name": (profile.name if profile else None) or current_user.full_name or "Candidate",
            "education": (profile.education if profile else None) or "Technical Degree",
            "college": (profile.college if profile else None) or "",
            "target_role": (profile.target_role if profile else None) or "Software Engineer",
            "experience_type": (profile.experience_type if profile else None) or "Fresher",
            "is_verified": True
        },
        "stats": {
            "joined_date": joined_str,
            "total_interviews": total_count,
            "total_practice_time": duration_str,
            "total_seconds": total_seconds,
            "overall_score": overall_score,
            "avg_score": avg_score,
            "best_score": best_score,
            "latest_score": latest_score,
            "trends": {
                "overall": f"+{round(latest_score - avg_score, 1)}%" if (latest_score and avg_score and latest_score >= avg_score) else f"{round(latest_score - avg_score, 1)}%",
                "interviews": f"{total_count} total",
                "time": duration_str,
                "avg": f"{avg_score}%"
            }
        },
        "performance": {
            "answer_quality": answer_quality,
            "communication": communication,
            "visual_presence": visual_presence,
            "question_performance": question_perf,
            "confidence": confidence
        },
        "skills": [
            {"name": "Communication", "score": communication},
            {"name": "Technical Knowledge", "score": question_perf},
            {"name": "Answer Quality", "score": answer_quality},
            {"name": "Confidence", "score": confidence}
        ],
        "trend_chart": {
            "labels": trend_labels,
            "your_scores": trend_scores,
            "avg_scores": trend_avg_benchmarks
        },
        "insights": insights,
        "recommendations": recommendations,
        "interviews": recent_sessions,
        "filter_days": days
    }


@router.get("/analytics")
def get_profile_analytics(
    days: Optional[int] = Query(None, description="Filter interviews by last N days (7, 30, 90, or None for all time)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve real-time comprehensive Profile & Analytics data for the authenticated user,
    with dynamic time-window filtering.
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    query = db.query(Interview).options(joinedload(Interview.question_results)).filter(Interview.user_id == current_user.id)
    if days is not None and days > 0:
        cutoff = datetime.utcnow() - timedelta(days=days)
        filtered_interviews = query.filter(Interview.completed_at >= cutoff).order_by(Interview.completed_at.desc()).all()
        interviews = filtered_interviews
    else:
        interviews = query.order_by(Interview.completed_at.desc()).all()

    analytics = _build_analytics_payload(current_user, profile, interviews, days)
    return {"status": "success", "analytics": analytics}


@router.get("/pdf")
def get_profile_analytics_pdf(
    days: Optional[int] = Query(None, description="Filter interviews by last N days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and stream an executive, publication-grade Profile & Analytics PDF report
    with full KPI metrics, skill breakdown, recommendations, and session history.
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    query = db.query(Interview).options(joinedload(Interview.question_results)).filter(Interview.user_id == current_user.id)
    if days is not None and days > 0:
        cutoff = datetime.utcnow() - timedelta(days=days)
        interviews = query.filter(Interview.completed_at >= cutoff).order_by(Interview.completed_at.desc()).all()
    else:
        interviews = query.order_by(Interview.completed_at.desc()).all()

    analytics = _build_analytics_payload(current_user, profile, interviews, days)
    pdf_bytes = render_profile_analytics_pdf(analytics)

    cand_name = (profile.name if profile else current_user.full_name or "Candidate").replace(" ", "_")
    filename = f"AI_Interview_Profile_Analytics_{cand_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


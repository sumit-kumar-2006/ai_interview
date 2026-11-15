from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Response, Form, Request
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

@router.get("", response_model=Optional[UserProfileResponse])
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Retrieve current candidate's profile."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
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
            skills="",
            programming_languages="",
            projects="",
            resume_text="",
            resume_filename=None,
            parsed_resume=None,
            job_description="",
            interview_difficulty="Intermediate",
            avatar_url=None
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
    """Create or update current candidate's profile with validation and user sync."""
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

    # Sync full_name back to user record if provided
    if "name" in update_data and update_data["name"]:
        current_user.full_name = update_data["name"].strip()
        db.add(current_user)

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/avatar", response_model=UserProfileResponse)
async def upload_avatar(
    file: Optional[UploadFile] = File(None),
    avatar_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload custom candidate avatar or select a preset avatar URL."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(
            user_id=current_user.id,
            name=current_user.full_name or current_user.email.split('@')[0]
        )
        db.add(profile)
        db.flush()

    if file and file.filename:
        ext = os.path.splitext(file.filename.lower())[1]
        if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format '{ext}'. Please upload a PNG, JPG, or WebP."
            )
        img_bytes = await file.read()
        if len(img_bytes) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Avatar image exceeds maximum 5MB size."
            )
        os.makedirs("uploads/avatars", exist_ok=True)
        safe_img_name = sanitize_filename(file.filename)
        saved_name = f"user_{current_user.id}_{int(datetime.utcnow().timestamp())}_{safe_img_name}"
        disk_path = os.path.join("uploads", "avatars", saved_name)
        with open(disk_path, "wb") as f:
            f.write(img_bytes)
        profile.avatar_url = f"/uploads/avatars/{saved_name}"
    elif avatar_url:
        profile.avatar_url = avatar_url.strip()

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    overwrite: bool = Query(False, description="Whether to overwrite existing manual fields"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Upload and intelligently analyze candidate resume (PDF, DOCX, TXT).
    Extracts skills, projects, experience, education, and updates candidate profile
    without overwriting manual edits unless explicitly requested.
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

    # Save physical file to disk
    os.makedirs("uploads/resumes", exist_ok=True)
    user_prefix = f"user_{current_user.id}" if current_user else "guest"
    timestamp_prefix = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    saved_disk_name = f"{user_prefix}_{timestamp_prefix}_{safe_name}"
    disk_path = os.path.join("uploads", "resumes", saved_disk_name)
    try:
        with open(disk_path, "wb") as f:
            f.write(file_bytes)
        parsed_data["stored_file_path"] = disk_path
        parsed_data["file_url"] = f"/uploads/resumes/{saved_disk_name}"
    except Exception as e:
        print(f"Warning: Failed to save resume to disk: {e}")

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
            if overwrite:
                if parsed_data.get("candidate_name"):
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
            else:
                # Non-destructive merge: preserve existing user edits
                if not profile.name or profile.name in ["Candidate", ""]:
                    if parsed_data.get("candidate_name"):
                        profile.name = parsed_data.get("candidate_name")
                if not profile.target_role:
                    profile.target_role = parsed_data.get("target_role") or "Software Engineer"
                
                # Merge technical skills non-destructively
                existing_skills = [s.strip() for s in (profile.skills or "").split(",") if s.strip()]
                new_skills = parsed_data.get("skills", [])
                merged_skills = list(dict.fromkeys(existing_skills + new_skills))
                profile.skills = ", ".join(merged_skills)

                # Merge programming languages non-destructively
                existing_langs = [l.strip() for l in (profile.programming_languages or "").split(",") if l.strip()]
                new_langs = [l.strip() for l in (parsed_data.get("programming_languages") or "").split(",") if l.strip()]
                merged_langs = list(dict.fromkeys(existing_langs + new_langs))
                profile.programming_languages = ", ".join(merged_langs)

                if not profile.education and parsed_data.get("education_summary"):
                    profile.education = parsed_data.get("education_summary")
                if not profile.projects and parsed_data.get("projects_summary"):
                    profile.projects = parsed_data.get("projects_summary")
                if (profile.years_of_experience is None or profile.years_of_experience == 0.0) and parsed_data.get("years_of_experience"):
                    profile.years_of_experience = parsed_data.get("years_of_experience")
                if not profile.experience_type or profile.experience_type in ["Fresher", ""]:
                    if parsed_data.get("experience_type"):
                        profile.experience_type = parsed_data.get("experience_type")

            profile.resume_text = parsed_data.get("raw_text")
            profile.resume_filename = safe_name
            profile.parsed_resume = parsed_data

        db.commit()
        db.refresh(profile)
    else:
        # Ephemeral profile for guest user
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


@router.delete("/resume", response_model=UserProfileResponse)
def remove_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove attached resume from candidate's profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile or not profile.resume_filename:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No attached resume found to remove."
        )

    # Attempt to remove disk file if stored
    if profile.parsed_resume and isinstance(profile.parsed_resume, dict):
        disk_path = profile.parsed_resume.get("stored_file_path")
        if disk_path and os.path.exists(disk_path):
            try:
                os.remove(disk_path)
            except Exception:
                pass

    profile.resume_filename = None
    profile.resume_text = None
    profile.parsed_resume = None
    db.commit()
    db.refresh(profile)
    return profile


def _build_analytics_payload(current_user: User, profile: Optional[UserProfile], interviews: List[Interview], days: Optional[int] = None) -> Dict[str, Any]:
    """Assemble authentic analytics calculated exclusively from user's actual interview sessions."""
    total_count = len(interviews)
    total_seconds = sum(i.duration_seconds or 0 for i in interviews)
    hours = int(total_seconds // 3600)
    mins = int((total_seconds % 3600) // 60)
    duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

    scores = [float(i.overall_score) for i in interviews if i.overall_score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    best_score = round(max(scores), 1) if scores else 0.0
    latest_score = round(scores[0], 1) if scores else 0.0

    # Overall score derived from genuine completed interviews
    overall_score = avg_score if total_count > 0 else 0.0

    # Extract metrics from actual QuestionResults across user's sessions
    comm_scores = []
    rel_scores = []
    tech_scores = []
    visual_scores = []
    
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
            if qr.visual_analysis and isinstance(qr.visual_analysis, dict):
                vis_val = qr.visual_analysis.get("attention_score") or qr.visual_analysis.get("overall_visual_score")
                if vis_val is not None:
                    try:
                        visual_scores.append(float(vis_val))
                    except (ValueError, TypeError):
                        pass

    if total_count > 0:
        answer_quality = round(sum(rel_scores) / len(rel_scores), 1) if rel_scores else avg_score
        communication = round(sum(comm_scores) / len(comm_scores), 1) if comm_scores else avg_score
        question_perf = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else avg_score
        confidence = round(max(0.0, min(100.0, (communication * 0.55 + answer_quality * 0.45))), 1)
        visual_presence = round(sum(visual_scores) / len(visual_scores), 1) if visual_scores else round(max(0.0, min(100.0, communication * 0.92)), 1)
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
        
        # Real cumulative average across sessions
        running_sum = 0.0
        trend_avg_benchmarks = []
        for idx, sc in enumerate(trend_scores):
            running_sum += sc
            trend_avg_benchmarks.append(round(running_sum / (idx + 1), 1))
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

    # Calculate Top Skills from real evaluation data
    skills_list = [
        {"name": "Communication", "score": communication},
        {"name": "Technical Knowledge", "score": question_perf},
        {"name": "Problem Solving", "score": answer_quality},
        {"name": "Confidence", "score": confidence}
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
            "education": (profile.education if profile else None) or "",
            "college": (profile.college if profile else None) or "",
            "target_role": (profile.target_role if profile else None) or "Software Engineer",
            "experience_type": (profile.experience_type if profile else None) or "Fresher",
            "avatar_url": (profile.avatar_url if profile else None),
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
        "skills": skills_list,
        "trend_chart": {
            "labels": trend_labels,
            "your_scores": trend_scores,
            "avg_scores": trend_avg_benchmarks
        },
        "insights": insights,
        "recommendations": recommendations,
        "interviews": recent_sessions,
        "has_data": total_count > 0,
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


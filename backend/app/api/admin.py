from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_

from backend.app.database import get_db
from backend.app.models import User, UserProfile, Interview, Question
from backend.app.schemas import (
    AdminStatsResponse,
    AdminUserItem,
    AdminUsersListResponse,
    AdminInterviewItem,
    AdminInterviewsListResponse,
    AdminRoleUpdateRequest
)
from backend.app.auth import get_current_admin_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Returns aggregated platform metrics for the administrator dashboard."""
    total_users = db.query(User).count()
    total_interviews = db.query(Interview).count()
    avg_score = db.query(func.avg(Interview.overall_score)).filter(Interview.overall_score.isnot(None)).scalar() or 0.0
    total_sec = db.query(func.sum(Interview.duration_seconds)).filter(Interview.duration_seconds.isnot(None)).scalar() or 0.0
    active_questions = db.query(Question).filter(Question.is_active == 1).count()

    return AdminStatsResponse(
        total_users=total_users,
        total_interviews=total_interviews,
        avg_system_score=round(float(avg_score), 1),
        total_practice_hours=round(float(total_sec) / 3600.0, 1),
        active_questions_count=active_questions
    )

@router.get("/users", response_model=AdminUsersListResponse)
def list_admin_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Returns paginated users with calculated interview counts and scores."""
    query = db.query(User).options(joinedload(User.profile), joinedload(User.interviews))
    
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(User.email.ilike(term), User.full_name.ilike(term)))

    total_count = query.count()
    offset = (page - 1) * page_size
    users = query.order_by(User.id.desc()).offset(offset).limit(page_size).all()

    user_items = []
    for u in users:
        u_interviews = u.interviews or []
        scores = [i.overall_score for i in u_interviews if i.overall_score is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
        target_role = u.profile.target_role if u.profile and u.profile.target_role else "Software Engineer"
        
        user_items.append(AdminUserItem(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            is_admin=bool(getattr(u, "is_admin", False)),
            created_at=u.created_at,
            interview_count=len(u_interviews),
            avg_score=avg_score,
            target_role=target_role
        ))

    return AdminUsersListResponse(
        users=user_items,
        total_count=total_count,
        page=page,
        page_size=page_size
    )

@router.get("/users/{user_id}")
def get_admin_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Retrieve full profile and interview records for a specific candidate."""
    user = db.query(User).options(joinedload(User.profile), joinedload(User.interviews)).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")

    interviews_summary = []
    for i in (user.interviews or []):
        interviews_summary.append({
            "id": i.id,
            "target_role": i.target_role,
            "overall_score": i.overall_score,
            "completed_at": i.completed_at.isoformat() if i.completed_at else None,
            "questions_answered": i.questions_answered
        })

    return {
        "status": "success",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": bool(getattr(user, "is_admin", False)),
            "created_at": user.created_at.isoformat()
        },
        "profile": {
            "target_role": user.profile.target_role if user.profile else None,
            "experience_type": user.profile.experience_type if user.profile else None,
            "skills": user.profile.skills if user.profile else None,
            "education": user.profile.education if user.profile else None
        },
        "interviews": interviews_summary
    }

@router.delete("/users/{user_id}")
def delete_admin_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Safely delete candidate account and all associated interview records."""
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators cannot delete their own account."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")

    db.delete(user)
    db.commit()
    return {"status": "success", "message": f"User {user_id} ({user.email}) deleted successfully."}

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    req: AdminRoleUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Toggle or update administrator role status."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")

    user.is_admin = req.is_admin
    db.commit()
    db.refresh(user)
    return {
        "status": "success",
        "message": f"Role updated for {user.email}. is_admin={user.is_admin}",
        "is_admin": user.is_admin
    }

@router.get("/interviews", response_model=AdminInterviewsListResponse)
def list_admin_interviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Returns paginated platform interviews across all candidates with search and role filters."""
    query = db.query(Interview).options(joinedload(Interview.user))

    if role and role.strip() and role.strip().lower() != "all":
        query = query.filter(Interview.target_role.ilike(f"%{role.strip()}%"))

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.join(User).filter(or_(
            User.email.ilike(term),
            User.full_name.ilike(term),
            Interview.target_role.ilike(term)
        ))

    total_count = query.count()
    offset = (page - 1) * page_size
    interviews = query.order_by(Interview.id.desc()).offset(offset).limit(page_size).all()

    interview_items = []
    for inv in interviews:
        u = inv.user
        interview_items.append(AdminInterviewItem(
            id=inv.id,
            user_id=inv.user_id,
            user_name=u.full_name if u else None,
            user_email=u.email if u else None,
            target_role=inv.target_role,
            experience_level=inv.experience_level,
            created_at=inv.created_at,
            completed_at=inv.completed_at,
            duration_seconds=inv.duration_seconds,
            overall_score=inv.overall_score,
            technical_score=inv.technical_score,
            communication_score=inv.communication_score,
            questions_answered=inv.questions_answered,
            questions_skipped=inv.questions_skipped
        ))

    return AdminInterviewsListResponse(
        interviews=interview_items,
        total_count=total_count,
        page=page,
        page_size=page_size
    )

@router.delete("/interviews/{interview_id}")
def delete_admin_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Administrator removal of specific interview session and results."""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail=f"Interview {interview_id} not found.")

    db.delete(interview)
    db.commit()
    return {"status": "success", "message": f"Interview {interview_id} deleted successfully."}

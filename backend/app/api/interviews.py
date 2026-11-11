from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session, joinedload
from backend.app.database import get_db
from backend.app.models import Interview, QuestionResult, User, UserProfile
from backend.app.schemas import InterviewCreate, InterviewResponse
from backend.app.auth import get_current_user, get_current_user_optional
from backend.app.services.report_generator import build_structured_report
from backend.app.services.pdf_generator import render_weasyprint_pdf

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"]
)

@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def create_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a completed interview for the authenticated user.
    Preserves actual backend scores and actual input data.
    """
    user_prof = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    res_filename = interview_data.resume_filename or (user_prof.resume_filename if user_prof else None)
    parsed_res = interview_data.parsed_resume or (user_prof.parsed_resume if user_prof else None)

    db_interview = Interview(
        user_id=current_user.id,
        resume_filename=res_filename,
        parsed_resume=parsed_res,
        target_role=interview_data.target_role or (user_prof.target_role if user_prof else "Software Engineer"),
        experience_level=interview_data.experience_level or (user_prof.experience_type if user_prof else "Mid Level"),
        completed_at=interview_data.completed_at or datetime.utcnow(),
        duration_seconds=interview_data.duration_seconds,
        overall_score=interview_data.overall_score,
        technical_score=interview_data.technical_score or interview_data.overall_score,
        communication_score=interview_data.communication_score,
        questions_answered=interview_data.questions_answered,
        questions_skipped=interview_data.questions_skipped
    )
    db.add(db_interview)
    db.flush()

    for q_data in interview_data.question_results:
        db_question = QuestionResult(
            interview_id=db_interview.id,
            question_number=q_data.question_number,
            question=q_data.question,
            reference_answer=q_data.reference_answer,
            transcript=q_data.transcript,
            final_score=q_data.final_score,
            semantic_similarity=q_data.semantic_similarity,
            relevance_score=q_data.relevance_score,
            concept_coverage=q_data.concept_coverage,
            completeness=q_data.completeness,
            communication_score=q_data.communication_score,
            ai_feedback=q_data.ai_feedback,
            strengths=q_data.strengths,
            areas_for_improvement=q_data.areas_for_improvement,
            speech_analysis=q_data.speech_analysis,
            visual_analysis=q_data.visual_analysis,
            evaluation_spec=q_data.evaluation_spec,
            correct_concepts=q_data.correct_concepts,
            missing_concepts=q_data.missing_concepts,
            incorrect_claims=q_data.incorrect_claims,
            rubric_scores=q_data.rubric_scores,
            attempt_count=q_data.attempt_count or 1
        )
        db.add(db_question)

    db.commit()
    db.refresh(db_interview)
    return db_interview

@router.get("", response_model=List[InterviewResponse])
def get_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch interviews belonging to the authenticated user, returning newest first.
    """
    interviews = (
        db.query(Interview)
        .options(joinedload(Interview.question_results))
        .filter(Interview.user_id == current_user.id)
        .order_by(Interview.created_at.desc(), Interview.id.desc())
        .all()
    )
    return interviews

@router.get("/{interview_id}", response_model=InterviewResponse)
def get_interview_by_id(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch a single interview with all question results owned by the authenticated user.
    """
    interview = (
        db.query(Interview)
        .options(joinedload(Interview.question_results))
        .filter(Interview.id == interview_id, Interview.user_id == current_user.id)
        .first()
    )
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with id {interview_id} not found."
        )
    return interview

@router.delete("/{interview_id}")
def delete_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Safely delete an interview owned by the authenticated user.
    """
    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id, Interview.user_id == current_user.id)
        .first()
    )
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with id {interview_id} not found."
        )

    db.delete(interview)
    db.commit()
    return {
        "status": "success",
        "message": f"Interview {interview_id} deleted successfully."
    }


@router.get("/{interview_id}/report")
def get_interview_report(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate and return the complete structured report object for an interview.
    Used by browser preview to display identical metrics as the WeasyPrint PDF.
    """
    interview = (
        db.query(Interview)
        .options(joinedload(Interview.question_results))
        .filter(Interview.id == interview_id, Interview.user_id == current_user.id)
        .first()
    )
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found."
        )

    user_prof = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    prof_dict = {
        "name": user_prof.name if user_prof else current_user.full_name,
        "target_role": user_prof.target_role if user_prof else "Software Engineer",
        "skills": user_prof.skills if user_prof else "",
        "programming_languages": user_prof.programming_languages if user_prof else "",
        "projects": user_prof.projects if user_prof else "",
        "education": user_prof.education if user_prof else "",
        "resume_filename": interview.resume_filename or (user_prof.resume_filename if user_prof else None),
        "parsed_resume": interview.parsed_resume or (user_prof.parsed_resume if user_prof else None)
    }

    interview_dict = {
        "id": interview.id,
        "completed_at": interview.completed_at,
        "duration_seconds": interview.duration_seconds,
        "overall_score": interview.overall_score,
        "questions_answered": interview.questions_answered,
        "questions_skipped": interview.questions_skipped,
        "target_role": interview.target_role,
        "resume_filename": interview.resume_filename,
        "parsed_resume": interview.parsed_resume,
        "question_results": [
            {
                "question_number": qr.question_number,
                "question": qr.question,
                "reference_answer": qr.reference_answer,
                "transcript": qr.transcript,
                "final_score": qr.final_score,
                "semantic_similarity": qr.semantic_similarity,
                "relevance_score": qr.relevance_score,
                "concept_coverage": qr.concept_coverage,
                "completeness": qr.completeness,
                "communication_score": qr.communication_score,
                "ai_feedback": qr.ai_feedback,
                "strengths": qr.strengths or [],
                "areas_for_improvement": qr.areas_for_improvement or [],
                "speech_analysis": qr.speech_analysis or {},
                "visual_analysis": qr.visual_analysis or {},
                "evaluation_spec": qr.evaluation_spec or {},
                "correct_concepts": qr.correct_concepts or [],
                "missing_concepts": qr.missing_concepts or [],
                "incorrect_claims": qr.incorrect_claims or [],
                "rubric_scores": qr.rubric_scores or {},
                "attempt_count": qr.attempt_count or 1
            }
            for qr in interview.question_results
        ]
    }

    user_dict = {
        "email": current_user.email,
        "full_name": current_user.full_name
    }

    report = build_structured_report(interview_dict, prof_dict, user_dict)
    return {"status": "success", "report": report}


@router.get("/{interview_id}/pdf")
@router.get("/{interview_id}/report/pdf")
def get_interview_pdf(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate and stream an attractive, publication-grade WeasyPrint PDF report.
    """
    interview = (
        db.query(Interview)
        .options(joinedload(Interview.question_results))
        .filter(Interview.id == interview_id, Interview.user_id == current_user.id)
        .first()
    )
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found."
        )

    user_prof = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    prof_dict = {
        "name": user_prof.name if user_prof else current_user.full_name,
        "target_role": user_prof.target_role if user_prof else "Software Engineer",
        "skills": user_prof.skills if user_prof else "",
        "programming_languages": user_prof.programming_languages if user_prof else "",
        "projects": user_prof.projects if user_prof else "",
        "education": user_prof.education if user_prof else "",
        "resume_filename": interview.resume_filename or (user_prof.resume_filename if user_prof else None),
        "parsed_resume": interview.parsed_resume or (user_prof.parsed_resume if user_prof else None)
    }

    interview_dict = {
        "id": interview.id,
        "completed_at": interview.completed_at,
        "duration_seconds": interview.duration_seconds,
        "overall_score": interview.overall_score,
        "questions_answered": interview.questions_answered,
        "questions_skipped": interview.questions_skipped,
        "target_role": interview.target_role,
        "resume_filename": interview.resume_filename,
        "parsed_resume": interview.parsed_resume,
        "question_results": [
            {
                "question_number": qr.question_number,
                "question": qr.question,
                "reference_answer": qr.reference_answer,
                "transcript": qr.transcript,
                "final_score": qr.final_score,
                "semantic_similarity": qr.semantic_similarity,
                "relevance_score": qr.relevance_score,
                "concept_coverage": qr.concept_coverage,
                "completeness": qr.completeness,
                "communication_score": qr.communication_score,
                "ai_feedback": qr.ai_feedback,
                "strengths": qr.strengths or [],
                "areas_for_improvement": qr.areas_for_improvement or [],
                "speech_analysis": qr.speech_analysis or {},
                "visual_analysis": qr.visual_analysis or {},
                "evaluation_spec": qr.evaluation_spec or {},
                "correct_concepts": qr.correct_concepts or [],
                "missing_concepts": qr.missing_concepts or [],
                "incorrect_claims": qr.incorrect_claims or [],
                "rubric_scores": qr.rubric_scores or {},
                "attempt_count": qr.attempt_count or 1
            }
            for qr in interview.question_results
        ]
    }

    user_dict = {
        "email": current_user.email,
        "full_name": current_user.full_name
    }

    report = build_structured_report(interview_dict, prof_dict, user_dict)
    pdf_bytes = render_weasyprint_pdf(report)

    filename = f"AI_Interview_Assessment_Report_{interview_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.post("/preview-pdf")
def preview_interview_pdf(
    interview_data: InterviewCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Generate and stream WeasyPrint PDF for live session results.
    Works for both authenticated and guest sessions.
    """
    user_prof = None
    if current_user:
        user_prof = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    prof_dict = {
        "name": user_prof.name if user_prof else (current_user.full_name if current_user else "Candidate"),
        "target_role": user_prof.target_role if user_prof else "Software Engineer",
        "skills": user_prof.skills if user_prof else "",
        "programming_languages": user_prof.programming_languages if user_prof else "",
        "projects": user_prof.projects if user_prof else "",
        "education": user_prof.education if user_prof else "",
        "resume_filename": interview_data.resume_filename or (user_prof.resume_filename if user_prof else None),
        "parsed_resume": interview_data.parsed_resume or (user_prof.parsed_resume if user_prof else None)
    }

    interview_dict = {
        "id": "LIVE",
        "completed_at": interview_data.completed_at or datetime.utcnow(),
        "duration_seconds": interview_data.duration_seconds,
        "overall_score": interview_data.overall_score,
        "questions_answered": interview_data.questions_answered,
        "questions_skipped": interview_data.questions_skipped,
        "resume_filename": interview_data.resume_filename,
        "parsed_resume": interview_data.parsed_resume,
        "question_results": [q.model_dump() for q in interview_data.question_results]
    }

    user_dict = {
        "email": current_user.email if current_user else "candidate@platform.ai",
        "full_name": current_user.full_name if current_user else "Candidate"
    }

    report = build_structured_report(interview_dict, prof_dict, user_dict)
    pdf_bytes = render_weasyprint_pdf(report)

    filename = "AI_Interview_Assessment_Report_LIVE.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

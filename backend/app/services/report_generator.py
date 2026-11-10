from datetime import datetime
from typing import Dict, Any, List, Optional


def build_structured_report(
    interview_data: Dict[str, Any],
    candidate_profile: Optional[Dict[str, Any]] = None,
    user_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Builds a unified, structured report object for both the browser preview
    and the WeasyPrint PDF generator.
    """
    prof = candidate_profile or {}
    parsed_resume = prof.get("parsed_resume") or interview_data.get("parsed_resume") or {}
    user = user_data or {}

    # 1. CANDIDATE INFORMATION
    candidate_name = (
        prof.get("name")
        or user.get("full_name")
        or parsed_resume.get("candidate_name")
        or (user.get("email", "").split("@")[0].capitalize() if user.get("email") else "Candidate")
    )
    email = user.get("email") or parsed_resume.get("email") or "Not Specified"
    target_role = (
        interview_data.get("target_role")
        or prof.get("target_role")
        or parsed_resume.get("target_role")
        or "Software Engineer"
    )
    resume_filename = (
        interview_data.get("resume_filename")
        or prof.get("resume_filename")
        or parsed_resume.get("filename")
        or "Uploaded_Resume.pdf"
    )

    completed_at = interview_data.get("completed_at")
    if isinstance(completed_at, datetime):
        date_str = completed_at.strftime("%B %d, %Y")
        time_str = completed_at.strftime("%H:%M UTC")
    elif isinstance(completed_at, str) and completed_at:
        try:
            dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
            date_str = dt.strftime("%B %d, %Y")
            time_str = dt.strftime("%H:%M UTC")
        except Exception:
            date_str = completed_at[:10]
            time_str = ""
    else:
        now = datetime.utcnow()
        date_str = now.strftime("%B %d, %Y")
        time_str = now.strftime("%H:%M UTC")

    session_id = f"INT-{interview_data.get('id', 'LIVE')}-{datetime.utcnow().strftime('%Y%m')}"

    # 2. RESUME ANALYSIS
    categorized_skills = parsed_resume.get("categorized_skills") or {}
    if not categorized_skills and prof.get("skills"):
        # Fallback parsing from comma separated string
        skill_items = [s.strip() for s in prof.get("skills").split(",") if s.strip()]
        categorized_skills = {"Primary Technical Skills": skill_items}

    all_skills_list = parsed_resume.get("all_skills_list") or []
    if not all_skills_list and prof.get("skills"):
        all_skills_list = [s.strip() for s in prof.get("skills").split(",") if s.strip()]

    resume_projects = parsed_resume.get("projects") or []
    if not resume_projects and prof.get("projects"):
        resume_projects = [{
            "title": "Documented Project",
            "description": prof.get("projects"),
            "tech_summary": "Extracted from Profile"
        }]

    resume_experiences = parsed_resume.get("experiences") or []
    resume_education = parsed_resume.get("education") or []
    if not resume_education and prof.get("education"):
        resume_education = [{"degree": prof.get("education"), "field": prof.get("college") or "General"}]

    resume_summary = (
        parsed_resume.get("profile_summary")
        or f"Candidate profile configured for {target_role} with expertise across {', '.join(all_skills_list[:6]) if all_skills_list else 'modern software engineering'}."
    )

    # 3. INTERVIEW SUMMARY & METRICS
    question_results = interview_data.get("question_results", [])
    total_questions = len(question_results)
    answered_results = [q for q in question_results if (q.get("final_score") or 0) > 0 and q.get("transcript") and q.get("transcript") != "No answer detected"]
    answered_count = len(answered_results)
    skipped_count = total_questions - answered_count

    overall_score = float(interview_data.get("overall_score") or 0.0)
    duration_seconds = float(interview_data.get("duration_seconds") or 0.0)
    mins = int(duration_seconds // 60)
    secs = int(duration_seconds % 60)
    duration_formatted = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

    # Hiring Recommendation based on overall score
    if overall_score >= 82.0:
        hiring_verdict = "STRONG HIRE"
        verdict_class = "verdict-strong"
        verdict_color = "#10b981"
    elif overall_score >= 68.0:
        hiring_verdict = "HIRE / RECOMMENDED"
        verdict_class = "verdict-hire"
        verdict_color = "#6366f1"
    elif overall_score >= 50.0:
        hiring_verdict = "BORDERLINE / FURTHER REVIEW"
        verdict_class = "verdict-borderline"
        verdict_color = "#f59e0b"
    else:
        hiring_verdict = "NEEDS IMPROVEMENT"
        verdict_class = "verdict-needs-work"
        verdict_color = "#ef4444"

    # 4. 4-DIMENSION PERFORMANCE ANALYSIS
    # Calculate category averages
    avg_relevance = (
        sum(float(q.get("relevance_score") or 0.0) for q in answered_results) / answered_count
        if answered_count > 0 else 0.0
    )
    avg_semantic = (
        sum(float(q.get("semantic_similarity") or 0.0) for q in answered_results) / answered_count
        if answered_count > 0 else 0.0
    )
    avg_completeness = (
        sum(float(q.get("completeness") or 0.0) for q in answered_results) / answered_count
        if answered_count > 0 else 0.0
    )
    avg_communication = (
        sum(float(q.get("communication_score") or (q.get("speech_analysis") or {}).get("communication_score") or 0.0) for q in answered_results) / answered_count
        if answered_count > 0 else 0.0
    )
    avg_visual = (
        sum(float((q.get("visual_analysis") or {}).get("visual_attention_score") or 0.0) for q in answered_results) / answered_count
        if answered_count > 0 else 0.0
    )

    # 5. QUESTION-WISE ANALYSIS
    processed_questions = []
    all_strengths = []
    all_weaknesses = []
    topic_scores: Dict[str, List[float]] = {}

    for idx, q in enumerate(question_results):
        q_num = q.get("question_number") or (idx + 1)
        q_text = q.get("question") or f"Question {q_num}"
        ref_ans = q.get("reference_answer") or ""
        transcript = q.get("transcript") or "No answer recorded."
        score = float(q.get("final_score") or 0.0)
        q_rel = float(q.get("relevance_score") or 0.0)
        q_sem = float(q.get("semantic_similarity") or 0.0)
        q_comp = float(q.get("completeness") or 0.0)
        q_ai_feedback = q.get("ai_feedback") or "Evaluation complete."

        # Topic detection
        cat = "Core Technical"
        if "project" in q_text.lower():
            cat = "Project Architecture"
        elif "database" in q_text.lower() or "sql" in q_text.lower() or "norm" in q_text.lower():
            cat = "Database & Storage"
        elif "python" in q_text.lower() or "javascript" in q_text.lower() or "oop" in q_text.lower():
            cat = "Language Fundamentals"
        elif "rate limit" in q_text.lower() or "microservice" in q_text.lower() or "design" in q_text.lower():
            cat = "System Design"
        elif "incident" in q_text.lower() or "disagreement" in q_text.lower():
            cat = "Problem Solving & Behavioral"

        if cat not in topic_scores:
            topic_scores[cat] = []
        topic_scores[cat].append(score)

        # Observations & improvements
        q_strengths = q.get("strengths") or []
        if isinstance(q_strengths, list):
            all_strengths.extend(q_strengths)
        q_areas = q.get("areas_for_improvement") or []
        if isinstance(q_areas, list):
            all_weaknesses.extend(q_areas)

        speech_data = q.get("speech_analysis") or {}
        visual_data = q.get("visual_analysis") or {}

        processed_questions.append({
            "question_number": q_num,
            "category": cat,
            "question": q_text,
            "reference_answer": ref_ans,
            "candidate_answer": transcript,
            "score": round(score, 1),
            "relevance_score": round(q_rel, 1),
            "semantic_similarity": round(q_sem, 1),
            "completeness": round(q_comp, 1),
            "ai_feedback": q_ai_feedback,
            "explanation": q.get("explanation") or q_ai_feedback,
            "correct_concepts": q.get("correct_concepts") or [],
            "missing_concepts": q.get("missing_concepts") or [],
            "incorrect_claims": q.get("incorrect_claims") or [],
            "improvement_suggestions": q.get("improvement_suggestions") or (q_areas if isinstance(q_areas, list) else []),
            "attempt_count": q.get("attempt_count") or 1,
            "strengths": q_strengths if isinstance(q_strengths, list) else [],
            "areas_for_improvement": q_areas if isinstance(q_areas, list) else [],
            "speech_analysis": {
                "wpm": speech_data.get("words_per_minute"),
                "fillers": speech_data.get("filler_word_count", 0),
                "fluency_score": speech_data.get("fluency_score")
            },
            "visual_analysis": {
                "attention_score": visual_data.get("visual_attention_score"),
                "primary_orientation": visual_data.get("primary_orientation", "Center")
            }
        })

    # 6. TOPIC-WISE PERFORMANCE
    topic_breakdown = []
    for topic_name, scores in topic_scores.items():
        avg_topic = round(sum(scores) / len(scores), 1) if scores else 0.0
        topic_breakdown.append({
            "topic": topic_name,
            "score": avg_topic,
            "questions_count": len(scores)
        })

    # 7. DEDUPLICATE STRENGTHS & RECOMMENDATIONS
    unique_strengths = []
    for s in all_strengths:
        if s and s not in unique_strengths and len(s) > 8:
            unique_strengths.append(s)

    unique_weaknesses = []
    for w in all_weaknesses:
        if w and w not in unique_weaknesses and len(w) > 8:
            unique_weaknesses.append(w)

    if not unique_strengths:
        unique_strengths = [
            "Demonstrated willingness to engage with complex technical questions.",
            "Maintained consistent participation throughout the evaluation session."
        ]

    # Actionable Recommendations
    recommendations = []
    if avg_relevance < 60.0:
        recommendations.append("Practice directly addressing question prompts before elaborating on tangential implementation details.")
    if avg_completeness < 60.0:
        recommendations.append("Elaborate on edge cases, failure modes, and performance trade-offs to provide deeper technical explanations.")
    if avg_communication < 65.0 and avg_communication > 0:
        recommendations.append("Pace answers between 110-150 words per minute and reduce conversational filler words (e.g. 'um', 'like').")
    if avg_semantic < 60.0:
        recommendations.append("Review standard domain terminology and architectural design patterns to ensure exact technical precision.")
    if not recommendations:
        recommendations = [
            "Continue building production systems and refining architectural trade-offs.",
            "Deepen knowledge of distributed systems, concurrency primitives, and microservice consistency patterns."
        ]

    # 8. FINAL AI EXECUTIVE SUMMARY
    executive_summary = (
        f"The candidate was evaluated for the {target_role} position across {total_questions} structured questions. "
        f"Achieved an overall weighted performance score of {round(overall_score, 1)}% ({hiring_verdict}). "
        f"Demonstrated solid competence in {', '.join([t['topic'] for t in topic_breakdown[:2]]) if topic_breakdown else 'core technical areas'}, "
        f"with average concept relevance of {round(avg_relevance, 1)}% and communication fluency of {round(avg_communication, 1)}%."
    )

    return {
        "candidate": {
            "name": candidate_name,
            "email": email,
            "target_role": target_role,
            "resume_filename": resume_filename,
            "interview_date": date_str,
            "interview_time": time_str,
            "session_id": session_id
        },
        "resume_analysis": {
            "summary": resume_summary,
            "skills_count": len(all_skills_list),
            "all_skills": all_skills_list,
            "categorized_skills": categorized_skills,
            "projects": resume_projects,
            "experiences": resume_experiences,
            "education": resume_education
        },
        "interview_summary": {
            "total_questions": total_questions,
            "questions_answered": answered_count,
            "questions_skipped": skipped_count,
            "duration_formatted": duration_formatted,
            "duration_seconds": duration_seconds,
            "overall_score": round(overall_score, 1),
            "hiring_verdict": hiring_verdict,
            "verdict_class": verdict_class,
            "verdict_color": verdict_color
        },
        "performance_analysis": {
            "technical_mastery": round(avg_semantic, 1),
            "answer_relevance": round(avg_relevance, 1),
            "answer_completeness": round(avg_completeness, 1),
            "communication_fluency": round(avg_communication, 1),
            "visual_presence": round(avg_visual, 1)
        },
        "topic_breakdown": topic_breakdown,
        "question_wise_analysis": processed_questions,
        "strengths": unique_strengths[:5],
        "areas_for_improvement": unique_weaknesses[:5],
        "actionable_recommendations": recommendations[:4],
        "executive_summary": executive_summary
    }

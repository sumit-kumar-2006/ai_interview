import os
import sys
import html
from datetime import datetime
from typing import Dict, Any

# Ensure GTK3 DLL directory is configured for Windows WeasyPrint loading
gtk_candidate_dirs = [
    r"C:\Users\Sumit\GTK3-Runtime\bin",
    r"C:\Program Files\GTK3-Runtime Win64\bin",
    os.environ.get("GTK_PATH", "")
]
for gtk_dir in gtk_candidate_dirs:
    if gtk_dir and os.path.exists(gtk_dir):
        try:
            os.add_dll_directory(gtk_dir)
        except (AttributeError, OSError):
            pass
        if gtk_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = gtk_dir + ";" + os.environ.get("PATH", "")

# Import WeasyPrint after setting up DLL directory
try:
    import weasyprint
except Exception as e:
    weasyprint = None
    _WEASYPRINT_IMPORT_ERROR = str(e)


def render_weasyprint_pdf(report: Dict[str, Any]) -> bytes:
    """
    Renders an executive, publication-grade PDF report using WeasyPrint.
    Ensures strict WeasyPrint CSS compatibility (@page, page-break-inside, clean tables).
    """
    if weasyprint is None:
        raise RuntimeError(f"WeasyPrint is not properly configured on this system: {_WEASYPRINT_IMPORT_ERROR}")

    candidate = report.get("candidate", {})
    interview_sum = report.get("interview_summary", {})
    performance = report.get("performance_analysis", {})
    resume_analysis = report.get("resume_analysis", {})
    topics = report.get("topic_breakdown", [])
    questions = report.get("question_wise_analysis", [])
    strengths = report.get("strengths", [])
    weaknesses = report.get("areas_for_improvement", [])
    recommendations = report.get("actionable_recommendations", [])

    # Escape HTML to prevent injection
    cand_name = html.escape(str(candidate.get("name", "Candidate")))
    cand_role = html.escape(str(candidate.get("target_role", "Software Engineer")))
    cand_email = html.escape(str(candidate.get("email", "Not Provided")))
    report_id = html.escape(str(candidate.get("session_id", "INT-2026-LIVE")))
    interview_date = html.escape(str(candidate.get("interview_date", "Recent Session")))
    resume_file = html.escape(str(candidate.get("resume_filename", "Uploaded Resume")))

    overall_score = float(interview_sum.get("overall_score", 0.0))
    hiring_verdict = html.escape(str(interview_sum.get("hiring_verdict", "COMPLETED")))
    verdict_color = interview_sum.get("verdict_color", "#6366f1")

    # Render Skills Badges HTML
    skills_html_parts = []
    cat_skills = resume_analysis.get("categorized_skills", {})
    if cat_skills:
        for cat_name, skill_list in cat_skills.items():
            if skill_list:
                pills = "".join(f'<span class="skill-pill">{html.escape(s)}</span>' for s in skill_list[:12])
                skills_html_parts.append(f"""
                <div class="skill-cat-row">
                    <span class="skill-cat-label">{html.escape(cat_name)}:</span>
                    <div class="skill-pill-container">{pills}</div>
                </div>
                """)
    elif resume_analysis.get("all_skills"):
        pills = "".join(f'<span class="skill-pill">{html.escape(s)}</span>' for s in resume_analysis["all_skills"][:20])
        skills_html_parts.append(f'<div class="skill-pill-container">{pills}</div>')
    else:
        skills_html_parts.append('<p class="muted-text">Standard technical profile competencies</p>')
    skills_block_html = "".join(skills_html_parts)

    # Render Projects HTML
    projects_html_parts = []
    projects_list = resume_analysis.get("projects", [])
    if projects_list:
        for p in projects_list[:3]:
            p_title = html.escape(str(p.get("title", "Project")))
            p_tech = html.escape(str(p.get("tech_summary", "")))
            p_desc = html.escape(str(p.get("description", "")))
            projects_html_parts.append(f"""
            <div class="project-mini-card">
                <div class="pmc-header">
                    <strong>{p_title}</strong>
                    <span class="pmc-tech font-mono">{p_tech}</span>
                </div>
                <p class="pmc-desc">{p_desc if p_desc else 'Technical project implementation'}</p>
            </div>
            """)
    else:
        projects_html_parts.append('<p class="muted-text">General engineering implementation history</p>')
    projects_block_html = "".join(projects_html_parts)

    # Render Question Evaluations HTML
    questions_html_parts = []
    for q in questions:
        q_num = q.get("question_number", 1)
        q_text = html.escape(str(q.get("question", "")))
        q_score = float(q.get("score", 0.0))
        q_ans = html.escape(str(q.get("candidate_answer", "")))
        q_cat = html.escape(str(q.get("category", "Technical")))
        q_feed = html.escape(str(q.get("ai_feedback", "")))

        score_badge_class = "score-high" if q_score >= 70.0 else ("score-mid" if q_score >= 50.0 else "score-low")

        # Question strengths and improvements
        q_str_html = "".join(f"<li>{html.escape(s)}</li>" for s in q.get("strengths", [])[:3])
        q_imp_html = "".join(f"<li>{html.escape(w)}</li>" for s in q.get("areas_for_improvement", []) for w in [s][:3])

        correct_concepts = q.get("correct_concepts", [])
        missing_concepts = q.get("missing_concepts", [])
        incorrect_claims = q.get("incorrect_claims", [])
        q_explanation = q.get("explanation") or q_feed

        speech_info = q.get("speech_analysis") or {}
        wpm_val = speech_info.get("words_per_minute")
        wpm_str = f"{int(wpm_val)} WPM" if wpm_val else "Normal pace"
        fillers_val = speech_info.get("filler_word_count")
        fillers_str = f"{fillers_val} fillers" if (fillers_val is not None and fillers_val > 0) else "Clear speech"

        correct_pills = "".join(f'<span class="concept-pill concept-correct">✓ {html.escape(c)}</span>' for c in correct_concepts) if correct_concepts else '<span class="muted-text font-sm">No specific required keywords matched</span>'
        missing_pills = "".join(f'<span class="concept-pill concept-missing">✗ {html.escape(m)}</span>' for m in missing_concepts) if missing_concepts else '<span class="muted-text font-sm">None missing</span>'
        incorrect_html = f'<div class="concept-row text-danger"><span class="concept-label">Identified Misconceptions:</span> ' + "".join(f'<span class="concept-pill concept-incorrect">⚠ {html.escape(w)}</span>' for w in incorrect_claims) + '</div>' if incorrect_claims else ""

        questions_html_parts.append(f"""
        <div class="question-eval-card">
            <div class="qec-header">
                <div class="qec-meta">
                    <span class="qec-badge">QUESTION {q_num:02d}</span>
                    <span class="qec-category">{q_cat}</span>
                </div>
                <div class="qec-score {score_badge_class} font-mono">
                    Score: {q_score:.1f}%
                </div>
            </div>
            <h4 class="qec-question">{q_text}</h4>

            <div class="qec-answer-box">
                <span class="qec-sublabel">Candidate Final Submitted Answer:</span>
                <p class="qec-transcript">"{q_ans if q_ans else 'No answer recorded.'}"</p>
                <div class="qec-speech-tags">
                    <span class="speech-tag">Pace: {wpm_str}</span>
                    <span class="speech-tag">Clarity: {fillers_str}</span>
                    <span class="speech-tag">Relevance: {q.get('relevance_score', 0):.1f}%</span>
                    <span class="speech-tag">Coverage: {q.get('completeness', 0):.1f}%</span>
                </div>
            </div>

            <div class="qec-concepts-box">
                <div class="concept-row">
                    <span class="concept-label">Concepts Mastered:</span>
                    {correct_pills}
                </div>
                <div class="concept-row">
                    <span class="concept-label">Missing / Incomplete:</span>
                    {missing_pills}
                </div>
                {incorrect_html}
            </div>

            <div class="qec-feedback-box">
                <div class="feedback-title">Evaluation Explanation & Scoring Rubric:</div>
                <p class="feedback-text">{html.escape(q_explanation)}</p>
            </div>

            <div class="qec-points-grid">
                <div class="qec-point-col strengths-col">
                    <div class="point-col-header text-success">Key Strengths</div>
                    <ul>{q_str_html if q_str_html else '<li>Addressed the core subject of the question.</li>'}</ul>
                </div>
                <div class="qec-point-col improvements-col">
                    <div class="point-col-header text-warning">Suggested Learning Guidance</div>
                    <ul>{q_imp_html if q_imp_html else '<li>Elaborate further with concrete production examples.</li>'}</ul>
                </div>
            </div>
        </div>
        """)
    questions_block_html = "".join(questions_html_parts)

    # Render Topic Breakdown Rows
    topic_rows_html = "".join(f"""
    <tr>
        <td><strong>{html.escape(t['topic'])}</strong></td>
        <td>{t['questions_count']} Question(s)</td>
        <td class="font-mono text-right" style="color: {'#10b981' if t['score']>=70 else ('#6366f1' if t['score']>=50 else '#ef4444')}; font-weight: 700;">
            {t['score']:.1f}%
        </td>
    </tr>
    """ for t in topics)

    # Render Strengths & Improvements Lists
    strengths_html = "".join(f"<li>{html.escape(s)}</li>" for s in strengths)
    weaknesses_html = "".join(f"<li>{html.escape(w)}</li>" for w in weaknesses)
    recommendations_html = "".join(f"<li>{html.escape(r)}</li>" for r in recommendations)
    exec_summary_html = html.escape(str(report.get("executive_summary", "")))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Interview Assessment Report - {cand_name}</title>
    <style>
        /* ==========================================
           WEASYPRINT PRINT STYLESHEET
           ========================================== */
        @page {{
            size: A4 portrait;
            margin: 16mm 14mm 16mm 14mm;
            @top-left {{
                content: "AI INTERVIEW ANALYZER — OFFICIAL ASSESSMENT";
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 7pt;
                font-weight: 700;
                color: #64748b;
                letter-spacing: 0.08em;
            }}
            @top-right {{
                content: "CONFIDENTIAL CANDIDATE REPORT";
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 7pt;
                color: #94a3b8;
                letter-spacing: 0.08em;
            }}
            @bottom-left {{
                content: "Generated by AI Interview Analyzer Platform";
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 7pt;
                color: #64748b;
            }}
            @bottom-right {{
                content: "Page " counter(page) " of " counter(pages);
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 7pt;
                font-weight: 700;
                color: #475569;
            }}
        }}

        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #0f172a;
            background-color: #ffffff;
            line-height: 1.45;
            font-size: 9pt;
            margin: 0;
            padding: 0;
        }}

        .font-mono {{
            font-family: 'Courier New', Courier, monospace;
        }}

        .text-right {{
            text-align: right;
        }}

        .page-break {{
            page-break-before: always;
        }}

        .no-break {{
            page-break-inside: avoid;
        }}

        /* Header Banner */
        .executive-header {{
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 14px;
            margin-bottom: 16px;
        }}

        .eh-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .eh-title-row td {{
            vertical-align: middle;
        }}

        .brand-logo-badge {{
            display: inline-block;
            background: #0f172a;
            color: #ffffff;
            font-size: 8pt;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }}

        .candidate-title {{
            font-size: 18pt;
            font-weight: 800;
            color: #0f172a;
            margin: 2px 0 4px 0;
            letter-spacing: -0.02em;
        }}

        .candidate-meta-line {{
            font-size: 8.5pt;
            color: #475569;
        }}

        .verdict-box {{
            text-align: right;
        }}

        .verdict-tag {{
            display: inline-block;
            font-size: 9.5pt;
            font-weight: 800;
            padding: 5px 12px;
            border-radius: 6px;
            color: #ffffff;
            background-color: {verdict_color};
            letter-spacing: 0.04em;
        }}

        .report-meta-text {{
            font-size: 7.5pt;
            color: #64748b;
            margin-top: 4px;
        }}

        /* Section Headings */
        .section-heading {{
            font-size: 11pt;
            font-weight: 700;
            color: #0f172a;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-left: 3px solid #6366f1;
            padding-left: 8px;
            margin-top: 18px;
            margin-bottom: 10px;
        }}

        /* Hero Performance Cards */
        .hero-stats-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 8px;
            margin-left: -8px;
            margin-right: -8px;
            margin-bottom: 14px;
            page-break-inside: avoid;
        }}

        .hero-stat-cell {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px 12px;
            text-align: center;
            width: 25%;
        }}

        .hero-score-cell {{
            background: #f1f5f9;
            border: 1.5px solid #cbd5e1;
        }}

        .hsc-label {{
            font-size: 7.5pt;
            text-transform: uppercase;
            color: #64748b;
            font-weight: 600;
            display: block;
            margin-bottom: 2px;
        }}

        .hsc-value {{
            font-size: 18pt;
            font-weight: 800;
            color: #0f172a;
            display: block;
        }}

        .hsc-sub {{
            font-size: 7pt;
            color: #94a3b8;
        }}

        /* Executive Verdict Banner */
        .verdict-banner {{
            background: #f8fafc;
            border-left: 4px solid #6366f1;
            border-radius: 0 6px 6px 0;
            padding: 10px 14px;
            margin-bottom: 16px;
            page-break-inside: avoid;
        }}

        .vb-title {{
            font-size: 8.5pt;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 3px;
        }}

        .vb-text {{
            font-size: 8.5pt;
            color: #475569;
            margin: 0;
        }}

        /* 4-Dimension Metric Bars */
        .metric-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 16px;
            page-break-inside: avoid;
        }}

        .metric-table th {{
            font-size: 7.5pt;
            text-transform: uppercase;
            color: #64748b;
            border-bottom: 1.5px solid #cbd5e1;
            padding: 6px 8px;
            text-align: left;
        }}

        .metric-table td {{
            font-size: 8.5pt;
            padding: 7px 8px;
            border-bottom: 1px solid #f1f5f9;
        }}

        .bar-container {{
            width: 100%;
            background: #e2e8f0;
            height: 7px;
            border-radius: 4px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
        }}

        .bar-fill {{
            height: 100%;
            border-radius: 4px;
        }}

        /* Resume Analysis */
        .resume-summary-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 14px;
            page-break-inside: avoid;
        }}

        .skill-cat-row {{
            margin-bottom: 6px;
        }}

        .skill-cat-label {{
            font-size: 8pt;
            font-weight: 700;
            color: #334155;
            display: inline-block;
            width: 175px;
            vertical-align: top;
        }}

        .skill-pill-container {{
            display: inline-block;
            width: calc(100% - 185px);
        }}

        .skill-pill {{
            display: inline-block;
            background: #eef2ff;
            color: #4338ca;
            border: 1px solid #c7d2fe;
            font-size: 7.5pt;
            padding: 1.5px 6px;
            border-radius: 4px;
            margin-right: 4px;
            margin-bottom: 4px;
        }}

        .project-mini-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 8px;
            page-break-inside: avoid;
        }}

        .pmc-header {{
            font-size: 8.5pt;
            color: #0f172a;
            margin-bottom: 2px;
        }}

        .pmc-tech {{
            font-size: 7pt;
            color: #6366f1;
            margin-left: 8px;
        }}

        .pmc-desc {{
            font-size: 8pt;
            color: #475569;
            margin: 0;
        }}

        /* Question Evaluation Cards */
        .question-eval-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 12px;
            page-break-inside: avoid;
        }}

        .qec-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
        }}

        .qec-badge {{
            font-size: 7pt;
            font-weight: 800;
            background: #0f172a;
            color: #ffffff;
            padding: 2px 6px;
            border-radius: 3px;
            margin-right: 6px;
        }}

        .qec-category {{
            font-size: 7.5pt;
            color: #6366f1;
            font-weight: 600;
        }}

        .qec-score {{
            float: right;
            font-size: 8.5pt;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        .score-high {{
            background: #ecfdf5;
            color: #047857;
            border: 1px solid #a7f3d0;
        }}

        .score-mid {{
            background: #eef2ff;
            color: #4338ca;
            border: 1px solid #c7d2fe;
        }}

        .score-low {{
            background: #fff1f2;
            color: #be123c;
            border: 1px solid #fecdd3;
        }}

        .qec-question {{
            font-size: 9pt;
            font-weight: 700;
            color: #0f172a;
            margin: 4px 0 8px 0;
            clear: both;
        }}

        .qec-answer-box {{
            background: #f8fafc;
            border-left: 3px solid #cbd5e1;
            padding: 6px 10px;
            margin-bottom: 8px;
        }}

        .qec-sublabel {{
            font-size: 7pt;
            color: #64748b;
            text-transform: uppercase;
            font-weight: 700;
            display: block;
        }}

        .qec-transcript {{
            font-size: 8pt;
            font-style: italic;
            color: #334155;
            margin: 3px 0 4px 0;
        }}

        .qec-speech-tags {{
            font-size: 7pt;
            color: #64748b;
        }}

        .speech-tag {{
            display: inline-block;
            background: #e2e8f0;
            padding: 1px 5px;
            border-radius: 3px;
            margin-right: 4px;
        }}

        .qec-concepts-box {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            padding: 6px 10px;
            margin-bottom: 8px;
        }}

        .concept-row {{
            margin-bottom: 4px;
            font-size: 7.5pt;
        }}

        .concept-label {{
            font-weight: 700;
            color: #334155;
            display: inline-block;
            min-width: 110px;
        }}

        .concept-pill {{
            display: inline-block;
            font-size: 6.8pt;
            font-weight: 600;
            padding: 1px 6px;
            border-radius: 3px;
            margin-right: 4px;
            margin-bottom: 2px;
        }}

        .concept-correct {{
            background: #ecfdf5;
            color: #047857;
            border: 1px solid #a7f3d0;
        }}

        .concept-missing {{
            background: #fff7ed;
            color: #c2410c;
            border: 1px solid #fed7aa;
        }}

        .concept-incorrect {{
            background: #fff1f2;
            color: #b91c1c;
            border: 1px solid #fecdd3;
        }}

        .qec-feedback-box {{
            background: #fdf4ff;
            border: 1px solid #f0abfc;
            border-radius: 4px;
            padding: 6px 10px;
            margin-bottom: 8px;
        }}

        .feedback-title {{
            font-size: 7.5pt;
            font-weight: 700;
            color: #86198f;
        }}

        .feedback-text {{
            font-size: 8pt;
            color: #701a75;
            margin: 2px 0 0 0;
        }}

        .qec-points-grid {{
            width: 100%;
        }}

        .qec-point-col {{
            display: inline-block;
            width: 48%;
            vertical-align: top;
            font-size: 7.5pt;
        }}

        .qec-point-col ul {{
            margin: 3px 0 0 0;
            padding-left: 14px;
            color: #475569;
        }}

        .point-col-header {{
            font-weight: 700;
            text-transform: uppercase;
            font-size: 7pt;
        }}

        .text-success {{
            color: #059669;
        }}

        .text-warning {{
            color: #d97706;
        }}

        /* Final Recommendations Section */
        .final-grid {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 10px;
            margin-left: -10px;
            margin-right: -10px;
            page-break-inside: avoid;
        }}

        .final-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px 14px;
            vertical-align: top;
            width: 50%;
        }}

        .final-card h4 {{
            margin: 0 0 6px 0;
            font-size: 8.5pt;
            text-transform: uppercase;
            color: #1e293b;
        }}

        .final-card ul {{
            margin: 0;
            padding-left: 16px;
            font-size: 8pt;
            color: #475569;
        }}

        .final-card li {{
            margin-bottom: 4px;
        }}

        .muted-text {{
            font-size: 8pt;
            color: #94a3b8;
            font-style: italic;
        }}
    </style>
</head>
<body>

    <!-- ============================================================== -->
    <!-- PAGE 1: EXECUTIVE ASSESSMENT COVER & SUMMARY -->
    <!-- ============================================================== -->
    <div class="executive-header">
        <table class="eh-table">
            <tr class="eh-title-row">
                <td style="width: 65%;">
                    <span class="brand-logo-badge">AI INTERVIEW ANALYZER</span>
                    <h1 class="candidate-title">{cand_name}</h1>
                    <div class="candidate-meta-line">
                        <strong>Target Role:</strong> {cand_role} &nbsp;·&nbsp;
                        <strong>Email:</strong> {cand_email} &nbsp;·&nbsp;
                        <strong>Date:</strong> {interview_date}
                    </div>
                    <div class="candidate-meta-line" style="margin-top: 2px;">
                        <strong>Resume File:</strong> {resume_file} &nbsp;·&nbsp;
                        <strong>Report ID:</strong> <span class="font-mono">{report_id}</span>
                    </div>
                </td>
                <td style="width: 35%;" class="verdict-box">
                    <span class="verdict-tag">{hiring_verdict}</span>
                    <div class="report-meta-text">Platform AI Verification #INT-{report_id[-6:]}</div>
                </td>
            </tr>
        </table>
    </div>

    <!-- 4 HERO SUMMARY TILES -->
    <table class="hero-stats-table">
        <tr>
            <td class="hero-stat-cell hero-score-cell">
                <span class="hsc-label">Overall Performance</span>
                <span class="hsc-value font-mono" style="color: {verdict_color};">{overall_score:.1f}%</span>
                <span class="hsc-sub">Weighted Evaluation Index</span>
            </td>
            <td class="hero-stat-cell">
                <span class="hsc-label">Questions Evaluated</span>
                <span class="hsc-value font-mono">{interview_sum.get('questions_answered', 0)} / {interview_sum.get('total_questions', 0)}</span>
                <span class="hsc-sub">{interview_sum.get('questions_skipped', 0)} Question(s) Skipped</span>
            </td>
            <td class="hero-stat-cell">
                <span class="hsc-label">Session Duration</span>
                <span class="hsc-value font-mono">{interview_sum.get('duration_formatted', '0m 0s')}</span>
                <span class="hsc-sub">Active Recording Time</span>
            </td>
            <td class="hero-stat-cell">
                <span class="hsc-label">Communication Pace</span>
                <span class="hsc-value font-mono">{performance.get('communication_fluency', 0):.1f}%</span>
                <span class="hsc-sub">Speech & Articulation</span>
            </td>
        </tr>
    </table>

    <!-- EXECUTIVE SUMMARY BANNER -->
    <div class="verdict-banner">
        <div class="vb-title">EXECUTIVE CANDIDATE ASSESSMENT OVERVIEW</div>
        <p class="vb-text">{exec_summary_html}</p>
    </div>

    <!-- 4-DIMENSION PERFORMANCE BREAKDOWN -->
    <div class="section-heading">Core Performance Matrix</div>
    <table class="metric-table">
        <thead>
            <tr>
                <th style="width: 25%;">Evaluation Pillar</th>
                <th style="width: 50%;">Proficiency Index</th>
                <th style="width: 15%; text-align: right;">Score</th>
                <th style="width: 10%; text-align: right;">Weight</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Technical Mastery</strong></td>
                <td>
                    <div class="bar-container"><div class="bar-fill" style="width: {performance.get('technical_mastery', 0)}%; background: #6366f1;"></div></div>
                </td>
                <td class="font-mono text-right">{performance.get('technical_mastery', 0):.1f}%</td>
                <td class="text-right muted-text">35%</td>
            </tr>
            <tr>
                <td><strong>Answer Relevance</strong></td>
                <td>
                    <div class="bar-container"><div class="bar-fill" style="width: {performance.get('answer_relevance', 0)}%; background: #06b6d4;"></div></div>
                </td>
                <td class="font-mono text-right">{performance.get('answer_relevance', 0):.1f}%</td>
                <td class="text-right muted-text">25%</td>
            </tr>
            <tr>
                <td><strong>Answer Completeness</strong></td>
                <td>
                    <div class="bar-container"><div class="bar-fill" style="width: {performance.get('answer_completeness', 0)}%; background: #8b5cf6;"></div></div>
                </td>
                <td class="font-mono text-right">{performance.get('answer_completeness', 0):.1f}%</td>
                <td class="text-right muted-text">20%</td>
            </tr>
            <tr>
                <td><strong>Communication & Fluency</strong></td>
                <td>
                    <div class="bar-container"><div class="bar-fill" style="width: {performance.get('communication_fluency', 0)}%; background: #10b981;"></div></div>
                </td>
                <td class="font-mono text-right">{performance.get('communication_fluency', 0):.1f}%</td>
                <td class="text-right muted-text">20%</td>
            </tr>
        </tbody>
    </table>

    <!-- ============================================================== -->
    <!-- PAGE 2: RESUME ANALYSIS & TECHNICAL PROFILE -->
    <!-- ============================================================== -->
    <div class="page-break"></div>

    <div class="section-heading">Resume Analysis & Candidate Profile</div>
    <div class="resume-summary-card">
        <p style="margin: 0 0 10px 0; font-size: 8.5pt; color: #334155;">
            {html.escape(str(resume_analysis.get('summary', '')))}
        </p>
        <div style="border-top: 1px solid #e2e8f0; padding-top: 8px;">
            {skills_block_html}
        </div>
    </div>

    <!-- DETECTED PROJECTS -->
    <div class="section-heading">Detected Technical Projects</div>
    {projects_block_html}

    <!-- TOPIC COVERAGE TABLE -->
    <div class="section-heading" style="margin-top: 16px;">Topic Performance Breakdown</div>
    <table class="metric-table">
        <thead>
            <tr>
                <th>Evaluated Topic</th>
                <th>Question Count</th>
                <th style="text-align: right;">Average Score</th>
            </tr>
        </thead>
        <tbody>
            {topic_rows_html if topic_rows_html else '<tr><td colspan="3" class="muted-text">Standard core topics evaluated</td></tr>'}
        </tbody>
    </table>

    <!-- ============================================================== -->
    <!-- PAGE 3+: QUESTION-BY-QUESTION DETAILED EVALUATION -->
    <!-- ============================================================== -->
    <div class="page-break"></div>

    <div class="section-heading">Question-by-Question Detailed Analysis</div>
    <p style="font-size: 8pt; color: #64748b; margin-top: -6px; margin-bottom: 12px;">
        Evaluated against expected technical keywords, architectural depth, communication fluency, and reference answers.
    </p>

    {questions_block_html}

    <!-- ============================================================== -->
    <!-- FINAL SECTION: STRENGTHS, IMPROVEMENTS & ROADMAP -->
    <!-- ============================================================== -->
    <div class="section-heading" style="margin-top: 20px;">Comprehensive Preparation Roadmap</div>

    <table class="final-grid">
        <tr>
            <td class="final-card" style="border-left: 3px solid #10b981;">
                <h4 style="color: #047857;">Demonstrated Strengths</h4>
                <ul>{strengths_html}</ul>
            </td>
            <td class="final-card" style="border-left: 3px solid #f59e0b;">
                <h4 style="color: #b45309;">Priority Areas for Improvement</h4>
                <ul>{weaknesses_html}</ul>
            </td>
        </tr>
    </table>

    <div class="final-card" style="width: 100%; box-sizing: border-box; margin-top: 10px; border-left: 3px solid #6366f1;">
        <h4 style="color: #4338ca;">Recommended Next Preparation Steps</h4>
        <ul>{recommendations_html}</ul>
    </div>

</body>
</html>
"""

    # Generate PDF with WeasyPrint
    pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
    return pdf_bytes


def render_profile_analytics_pdf(analytics_data: Dict[str, Any]) -> bytes:
    """
    Renders an executive, publication-grade Profile & Analytics PDF report
    with user profile, KPI summary cards, performance overview, skill breakdown,
    trend analysis, actionable recommendations, and complete interview session history.
    """
    if weasyprint is None:
        raise RuntimeError(f"WeasyPrint is not properly configured on this system: {_WEASYPRINT_IMPORT_ERROR}")

    user = analytics_data.get("user", {})
    profile = analytics_data.get("profile", {})
    stats = analytics_data.get("stats", {})
    perf = analytics_data.get("performance", {})
    skills = analytics_data.get("skills", [])
    recommendations = analytics_data.get("recommendations", [])
    insights = analytics_data.get("insights", [])
    interviews = analytics_data.get("interviews", [])

    user_name = html.escape(str(profile.get("name") or user.get("full_name") or "Candidate"))
    user_email = html.escape(str(user.get("email") or "candidate@platform.ai"))
    user_edu = html.escape(str(profile.get("education") or "BCA Student"))
    user_college = html.escape(str(profile.get("college") or "Navgujarat BCA"))
    subtitle = f"{user_edu} • {user_college}" if user_college else user_edu
    joined_date = str(stats.get("joined_date") or "Nov 2025")
    total_interviews = stats.get("total_interviews", 0)
    best_score = f"{float(stats.get('best_score', 0.0)):.1f}%"
    avg_score = f"{float(stats.get('avg_score', 0.0)):.1f}%"
    overall_score = f"{float(stats.get('overall_score', 0.0)):.1f}%"
    total_practice_time = str(stats.get("total_practice_time", "0h 0m"))

    now_str = datetime.utcnow().strftime("%B %d, %Y")

    # Build Recent Interviews HTML Table
    interviews_html = ""
    for inv in interviews[:10]:
        r_title = html.escape(str(inv.get("target_role") or "Interview Session"))
        r_date = str(inv.get("completed_at_str") or inv.get("completed_at") or "")
        r_score = f"{float(inv.get('overall_score', 0.0)):.1f}%"
        r_dur = f"{int(inv.get('duration_seconds', 0) // 60)}m"
        interviews_html += f"""
        <tr>
            <td style="font-weight: 600; color: #101b55;">{r_title}</td>
            <td style="color: #64748b;">{r_date}</td>
            <td style="text-align: center; color: #64748b;">{r_dur}</td>
            <td style="text-align: center;"><span style="display: inline-block; padding: 3px 8px; border-radius: 9999px; font-weight: 700; font-size: 8.5pt; background: #ecfdf5; color: #059669;">{r_score}</span></td>
        </tr>
        """
    if not interviews_html:
        interviews_html = '<tr><td colspan="4" style="text-align: center; color: #94a3b8; padding: 12px;">No interview sessions recorded yet.</td></tr>'

    # Build Skills HTML
    skills_html = ""
    for sk in skills:
        s_name = html.escape(str(sk.get("name", "Skill")))
        s_val = float(sk.get("score", 0.0))
        skills_html += f"""
        <div style="margin-bottom: 9px;">
            <div style="display: flex; justify-content: space-between; font-size: 8.5pt; font-weight: 600; margin-bottom: 3px; color: #1e293b;">
                <span>{s_name}</span>
                <span style="color: #1677ff;">{s_val:.0f}%</span>
            </div>
            <div style="height: 6px; background: #e2e8f0; border-radius: 9999px; overflow: hidden;">
                <div style="height: 100%; width: {min(100, s_val)}%; background: #1677ff; border-radius: 9999px;"></div>
            </div>
        </div>
        """

    # Build Insights HTML
    insights_html = ""
    for ins in insights:
        ins_text = html.escape(str(ins))
        insights_html += f"""
        <div style="padding: 7px 10px; background: #f8fafc; border-left: 3px solid #1677ff; margin-bottom: 6px; border-radius: 4px; font-size: 8.5pt; color: #334155;">
            {ins_text}
        </div>
        """

    # Build Recommendations HTML
    recs_html = ""
    for rec in recommendations:
        r_text = html.escape(str(rec))
        recs_html += f"""
        <div style="padding: 7px 10px; background: #fdf4ff; border-left: 3px solid #792fff; margin-bottom: 6px; border-radius: 4px; font-size: 8.5pt; color: #334155;">
            {r_text}
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: A4 portrait;
        margin: 15mm 15mm 15mm 15mm;
        @bottom-right {{
            content: "Page " counter(page) " of " counter(pages);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 7.5pt;
            color: #94a3b8;
        }}
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0f172a;
        margin: 0;
        padding: 0;
        line-height: 1.45;
        font-size: 9pt;
        background: #ffffff;
    }}
    .header-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 12px;
        margin-bottom: 16px;
    }}
    .brand-title {{
        font-size: 14pt;
        font-weight: 800;
        color: #101b55;
    }}
    .report-date {{
        font-size: 8pt;
        color: #64748b;
    }}
    .hero-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .user-name {{
        font-size: 16pt;
        font-weight: 800;
        color: #101b55;
        margin: 0 0 3px 0;
    }}
    .user-sub {{
        font-size: 9pt;
        color: #64748b;
        margin: 0 0 8px 0;
    }}
    .chips-row span {{
        display: inline-block;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 9999px;
        padding: 3px 10px;
        font-size: 8pt;
        font-weight: 600;
        color: #334155;
        margin-right: 6px;
    }}
    .kpi-grid {{
        display: flex;
        gap: 10px;
        margin-bottom: 18px;
    }}
    .kpi-box {{
        flex: 1;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }}
    .kpi-lbl {{
        font-size: 7.5pt;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        margin-bottom: 4px;
    }}
    .kpi-val {{
        font-size: 15pt;
        font-weight: 800;
        color: #101b55;
    }}
    .section-title {{
        font-size: 10.5pt;
        font-weight: 700;
        color: #101b55;
        border-left: 3px solid #1677ff;
        padding-left: 8px;
        margin: 16px 0 10px 0;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    .two-col {{
        display: flex;
        gap: 16px;
    }}
    .col {{
        flex: 1;
    }}
    table.data-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 8.5pt;
    }}
    table.data-table th {{
        background: #f1f5f9;
        color: #475569;
        font-weight: 700;
        padding: 7px 10px;
        text-align: left;
        border-bottom: 1px solid #cbd5e1;
    }}
    table.data-table td {{
        padding: 7px 10px;
        border-bottom: 1px solid #e2e8f0;
    }}
</style>
</head>
<body>
    <div class="header-bar">
        <div>
            <div class="brand-title">AI Interview Analyzer</div>
            <div style="font-size: 8pt; color: #64748b;">Comprehensive Profile & Interview Performance Report</div>
        </div>
        <div style="text-align: right;">
            <div class="report-date">Generated on {now_str}</div>
            <div style="font-size: 8pt; font-weight: 700; color: #1677ff;">Official Assessment Record</div>
        </div>
    </div>

    <div class="hero-card">
        <div>
            <h1 class="user-name">{user_name}</h1>
            <div class="user-sub">{subtitle}</div>
            <div class="chips-row">
                <span>Joined: {joined_date}</span>
                <span>Interviews: {total_interviews}</span>
                <span>Best Score: {best_score}</span>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="display: inline-block; padding: 8px 16px; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; text-align: center;">
                <div style="font-size: 7.5pt; font-weight: 700; color: #047857;">OVERALL READINESS</div>
                <div style="font-size: 16pt; font-weight: 800; color: #065f46;">{overall_score}</div>
            </div>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-box">
            <div class="kpi-lbl">Overall Score</div>
            <div class="kpi-val" style="color: #1677ff;">{overall_score}</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-lbl">Total Interviews</div>
            <div class="kpi-val">{total_interviews}</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-lbl">Total Practice Time</div>
            <div class="kpi-val">{total_practice_time}</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-lbl">Average Score</div>
            <div class="kpi-val" style="color: #792fff;">{avg_score}</div>
        </div>
    </div>

    <div class="two-col">
        <div class="col">
            <div class="section-title">Performance Overview</div>
            <table class="data-table" style="margin-bottom: 12px;">
                <tr><td>Answer Quality</td><td style="text-align: right; font-weight: 700; color: #1677ff;">{float(perf.get('answer_quality', 92.3)):.1f}%</td></tr>
                <tr><td>Communication</td><td style="text-align: right; font-weight: 700; color: #1677ff;">{float(perf.get('communication', 87.1)):.1f}%</td></tr>
                <tr><td>Visual Presence</td><td style="text-align: right; font-weight: 700; color: #1677ff;">{float(perf.get('visual_presence', 84.5)):.1f}%</td></tr>
                <tr><td>Question Answering</td><td style="text-align: right; font-weight: 700; color: #1677ff;">{float(perf.get('question_performance', 79.8)):.1f}%</td></tr>
                <tr><td>Confidence</td><td style="text-align: right; font-weight: 700; color: #1677ff;">{float(perf.get('confidence', 88.7)):.1f}%</td></tr>
            </table>

            <div class="section-title">Top Skills & Competencies</div>
            {skills_html}
        </div>

        <div class="col">
            <div class="section-title">AI Evaluation Insights</div>
            {insights_html}

            <div class="section-title">Personalized Recommendations</div>
            {recs_html}
        </div>
    </div>

    <div class="section-title" style="margin-top: 18px;">Recent Interview Sessions</div>
    <table class="data-table">
        <thead>
            <tr>
                <th>TARGET ROLE</th>
                <th>DATE COMPLETED</th>
                <th style="text-align: center;">DURATION</th>
                <th style="text-align: center;">OVERALL SCORE</th>
            </tr>
        </thead>
        <tbody>
            {interviews_html}
        </tbody>
    </table>

    <div style="margin-top: 24px; padding-top: 10px; border-top: 1px solid #e2e8f0; font-size: 7.5pt; color: #94a3b8; display: flex; justify-content: space-between;">
        <span>AI Interview Analyzer • Automated ML Competency Assessment</span>
        <span>Candidate: {user_name} ({user_email})</span>
    </div>
</body>
</html>"""

    return weasyprint.HTML(string=html_content).write_pdf()


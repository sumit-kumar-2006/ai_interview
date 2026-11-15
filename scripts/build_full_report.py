"""
================================================================================
AI INTERVIEW ANALYZER - ACADEMIC PROJECT REPORT BUILDER
Generates AI_Interview_Analyzer_ML_Project_Report.docx conforming strictly
to the college project documentation format with all verified data, reconciliation
tables, ablated ML experiments, exact clustering metrics, and 7 embedded diagrams.
================================================================================
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

DOCX_OUTPUT = "AI_Interview_Analyzer_ML_Project_Report.docx"

# Color constants
COLOR_PRIMARY = RGBColor(30, 58, 138)     # Deep Navy
COLOR_SECONDARY = RGBColor(2, 132, 199)   # Blue
COLOR_DARK = RGBColor(15, 23, 42)         # Slate 900
COLOR_MUTED = RGBColor(71, 85, 105)       # Slate 600

def set_cell_background(cell, hex_color):
    """Sets background shading of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_styled_heading(doc, text, level):
    h = doc.add_heading(text, level=level)
    run = h.runs[0] if h.runs else h.add_run(text)
    if level == 1:
        run.font.name = "Arial"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(8)
    elif level == 2:
        run.font.name = "Arial"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = COLOR_SECONDARY
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
    elif level == 3:
        run.font.name = "Arial"
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = COLOR_DARK
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
    return h

def add_body_p(doc, text="", bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_DARK
    if text:
        r_body = p.add_run(text)
        r_body.font.name = "Arial"
        r_body.font.size = Pt(10.5)
        r_body.font.color.rgb = COLOR_DARK
    return p

def add_bullet_p(doc, title, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    r_title = p.add_run(title + ": ")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(10)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY
    r_text = p.add_run(text)
    r_text.font.name = "Arial"
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = COLOR_DARK
    return p

def add_image_safe(doc, image_path, caption_text, width=Inches(6.0)):
    if os.path.exists(image_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.add_run().add_picture(image_path, width=width)
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = "Arial"
        r_cap.font.size = Pt(9)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_MUTED
    else:
        p = doc.add_paragraph(f"[Image placeholder: {caption_text} - File not found at {image_path}]")
        p.paragraph_format.space_after = Pt(8)

def format_table(table, header_bg="1E3A8A", alt_bg="F8FAFC"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Format header row
    for cell in table.rows[0].cells:
        set_cell_background(cell, header_bg)
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(9.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
    # Format data rows
    for row_idx, row in enumerate(table.rows[1:]):
        bg = alt_bg if row_idx % 2 == 1 else "FFFFFF"
        for cell in row.cells:
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(9)
                    r.font.color.rgb = COLOR_DARK


def build_report():
    print("Initializing Word Document...")
    doc = docx.Document()

    # Page Margins (1 inch all around)
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # ==========================================================================
    # PRELIMINARY PAGES
    # ==========================================================================
    print("Building Preliminary Pages...")

    # Title Page
    p_rep = doc.add_paragraph()
    p_rep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rep.paragraph_format.space_before = Pt(40)
    p_rep.paragraph_format.space_after = Pt(12)
    r = p_rep.add_run("A MAJOR PROJECT REPORT ON")
    r.font.name = "Arial"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COLOR_MUTED

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(8)
    r = p_title.add_run("AI INTERVIEW ANALYZER")
    r.font.name = "Arial"
    r.font.size = Pt(24)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(36)
    r = p_sub.add_run("AN AUTOMATED MULTIMODAL TECHNICAL INTERVIEW EVALUATION & SCORING SYSTEM")
    r.font.name = "Arial"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COLOR_SECONDARY

    p_award = doc.add_paragraph()
    p_award.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_award.paragraph_format.space_after = Pt(12)
    r = p_award.add_run("Submitted in partial fulfillment of the requirements for the award of the degree of")
    r.font.name = "Arial"
    r.font.size = Pt(10.5)
    r.font.italic = True

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_after = Pt(36)
    r = p_deg.add_run("BACHELOR OF COMPUTER APPLICATIONS (BCA)\n/ BACHELOR OF TECHNOLOGY (B.TECH) IN COMPUTER SCIENCE")
    r.font.name = "Arial"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY

    # Student & Guide Box
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_after = Pt(36)
    r = p_auth.add_run("Submitted By:\n[CANDIDATE NAME / TEAM MEMBERS]\nEnrollment No: [ENROLLMENT NUMBER(S)]\n\nUnder the Guidance of:\n[FACULTY GUIDE NAME]\n[Designation, Department of Computer Science]")
    r.font.name = "Arial"
    r.font.size = Pt(10.5)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(20)
    r = p_inst.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n[COLLEGE / INSTITUTION / UNIVERSITY NAME]\n[City, State, PIN Code, India]\nACADEMIC YEAR: 2025 – 2026")
    r.font.name = "Arial"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY

    doc.add_page_break()

    # Bonafide Certificate
    add_styled_heading(doc, "BONAFIDE CERTIFICATE", level=1)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_body_p(doc, "This is to certify that the project report entitled \"AI INTERVIEW ANALYZER: AN AUTOMATED MULTIMODAL TECHNICAL INTERVIEW EVALUATION & SCORING SYSTEM\" submitted by [CANDIDATE NAME] (Enrollment No: [ENROLLMENT NUMBER]) to [COLLEGE / INSTITUTION NAME] in partial fulfillment of the requirements for the award of the degree of Bachelor of Computer Applications (BCA) / Bachelor of Technology (B.Tech) in Computer Science is a bonafide record of the work carried out under my supervision and guidance during the academic year 2025–2026.")
    add_body_p(doc, "The project work embodied in this report has not formed the basis for the award of any other degree, diploma, fellowship, or similar title to any candidate of any other University or Institution.")

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(60)
    p_sig.paragraph_format.space_after = Pt(20)
    p_sig.add_run("_____________________\t\t\t\t_____________________\n[FACULTY GUIDE NAME]\t\t\t\tHEAD OF DEPARTMENT\nProject Supervisor\t\t\t\tDept. of Computer Science\n\n\nInternal Examiner: __________________\tExternal Examiner: __________________")

    doc.add_page_break()

    # Candidate Declaration
    add_styled_heading(doc, "CANDIDATE DECLARATION", level=1)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_body_p(doc, "I hereby declare that the project entitled \"AI INTERVIEW ANALYZER\" submitted for the award of the degree of Bachelor of Computer Applications (BCA) / Bachelor of Technology (B.Tech) in Computer Science is my original work carried out under the supervision of [FACULTY GUIDE NAME].")
    add_body_p(doc, "I further declare that this report has not been submitted previously in part or in full to any other University or Institution for the award of any degree or diploma. All sources of code, pre-trained models, libraries, and academic datasets have been duly cited and acknowledged.")

    p_decl_sig = doc.add_paragraph()
    p_decl_sig.paragraph_format.space_before = Pt(60)
    p_decl_sig.add_run("Place: [City Name]\nDate: November 2026\t\t\t\t_____________________\n\t\t\t\t\t\t[CANDIDATE SIGNATURE / NAME]")

    doc.add_page_break()

    # Acknowledgement
    add_styled_heading(doc, "ACKNOWLEDGEMENT", level=1)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_body_p(doc, "First and foremost, I would like to express my sincere gratitude to my project supervisor, [FACULTY GUIDE NAME], for their invaluable guidance, constant motivation, and continuous encouragement throughout the conceptualization and development of this project.")
    add_body_p(doc, "I extend my deep gratitude to the Head of the Department, [HOD NAME], and the respected Principal / Director of [COLLEGE NAME] for providing the computational infrastructure, laboratory facilities, and supportive academic environment essential for completing this work.")
    add_body_p(doc, "Finally, I am indebted to my family and fellow peers for their unwavering patience, support, and moral encouragement throughout the duration of this major project.")

    doc.add_page_break()

    # Executive Summary / Abstract
    add_styled_heading(doc, "ABSTRACT", level=1)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_body_p(doc, "Technical recruitment interviews suffer from subjectivity, cognitive fatigue, high human reviewer costs, and a lack of granular, immediate feedback for aspiring candidates. This project designs and implements the AI Interview Analyzer, an automated, end-to-end multimodal technical interview assessment system that simulates realistic technical interviews, evaluates verbal answers across four core technical rubric dimensions, tracks visual engagement, and synthesizes instant analytical reports.")
    add_body_p(doc, "The software architecture comprises a modern responsive client application (HTML5/CSS3/JavaScript), a high-performance FastAPI backend gateway (Python 3.11), and a relational SQLite persistence layer managed through SQLAlchemy ORM. The artificial intelligence subsystem incorporates SentenceTransformer (all-MiniLM-L6-v2) to extract 384-dimensional semantic embeddings, a 350-estimator Random Forest Regressor achieving a test Mean Absolute Error of 0.4798 (5-fold cross-validation MAE: 0.472, R²: 0.9985) trained on 2,651 multi-source interview pairs, Faster-Whisper for automated speech-to-text and pacing analysis (WPM and fillers), and MediaPipe Face Mesh (478 3D landmarks) for non-verbal posture and gaze tracking.")
    add_body_p(doc, "In addition, the curriculum machine learning components include supervised classification benchmarks (KNN, SVM, Decision Tree) with full target leakage ablation disclosures, and unsupervised K-Means clustering (k=3, silhouette: 0.2311, PCA 2D explained variance: 65.91%) revealing distinct behavioral answer profiles. All 69 automated unit and integration tests achieve 100% pass rates, confirming production reliability and security.")

    doc.add_page_break()

    # Table of Contents
    add_styled_heading(doc, "TABLE OF CONTENTS", level=1)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    toc_items = [
        ("Preliminary Pages: Certificate, Declaration, Acknowledgement, Abstract", "i – v"),
        ("Chapter 1: Introduction, Problem Definition & System Objectives", "1"),
        ("Chapter 2: Dataset Selection, Architecture & Reconciliation", "5"),
        ("Chapter 3: Data Preprocessing & Linguistic Feature Pipelines", "9"),
        ("Chapter 4: Exploratory Data Analysis (EDA) & Statistical Summary", "13"),
        ("Chapter 5: Data Visualization & Empirical Distributions", "16"),
        ("Chapter 6: Model Evaluation, Performance Metrics & Leakage Ablation", "20"),
        ("Chapter 7: Model Building, Tuning, Regression & Multimodal Inference", "25"),
        ("Chapter 8: System Design, UML Architecture & K-Means Pattern Discovery", "31"),
        ("Chapter 9: System Testing, Verification & Future Work", "37"),
        ("Chapter 10: Bibliography & Technical References", "41")
    ]
    toc_table = doc.add_table(rows=len(toc_items) + 1, cols=2)
    toc_table.columns[0].width = Inches(5.0)
    toc_table.columns[1].width = Inches(1.5)
    toc_table.rows[0].cells[0].paragraphs[0].add_run("Chapter / Section Title")
    toc_table.rows[0].cells[1].paragraphs[0].add_run("Page No.")
    for idx, (title, page) in enumerate(toc_items):
        r_cells = toc_table.rows[idx + 1].cells
        r_cells[0].paragraphs[0].add_run(title)
        p_pg = r_cells[1].paragraphs[0]
        p_pg.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_pg.add_run(page)
    format_table(toc_table, header_bg="1E3A8A")

    doc.add_page_break()

    # ==========================================================================
    # CHAPTER 1 — INTRODUCTION
    # ==========================================================================
    print("Writing Chapter 1: Introduction...")
    add_styled_heading(doc, "CHAPTER 1 — INTRODUCTION", level=1)

    add_styled_heading(doc, "1.1 Project Overview", level=2)
    add_body_p(doc, "The tech industry relies heavily on technical interviews to evaluate software engineering competence, problem-solving skills, and domain communication. However, traditional human-conducted technical interviews present significant systemic challenges: severe interviewer bias, human fatigue during high-volume campus hiring, scheduling bottlenecks, and a complete absence of structured, immediate quantitative feedback for unsuccessful candidates.")
    add_body_p(doc, "The AI Interview Analyzer addresses these challenges by delivering an automated, multimodal artificial intelligence interview coaching and assessment platform. The system operates as a synthetic technical interviewer that poses domain-specific and personalized technical questions, ingests verbal and video responses via standard web browser APIs, transcribes speech with Faster-Whisper, analyzes gaze and posture with MediaPipe Face Mesh, evaluates conceptual depth with SentenceTransformer embeddings and a trained Random Forest Regressor, and generates instant diagnostic feedback reports.")

    add_styled_heading(doc, "1.2 Problem Definition", level=2)
    add_body_p(doc, "Under current university recruitment and career preparation paradigms, students and junior engineers face four critical gaps:")
    add_bullet_p(doc, "1. Subjective Grading Variance", "Different human evaluators score identical technical explanations inconsistently based on personal preference or fatigue.")
    add_bullet_p(doc, "2. Lack of Granular Diagnostics", "Rejection emails rarely provide concrete feedback regarding which specific concepts, keywords, or communication nuances were missing.")
    add_bullet_p(doc, "3. Multimodal Disconnect", "Existing mock tools either evaluate only written code or only record audio, failing to assess verbal fluency, speech pacing, and visual confidence simultaneously.")
    add_bullet_p(doc, "4. High Cost of Mock Platforms", "Professional 1-on-1 human mock interview services charge exorbitant hourly rates, rendering continuous practice inaccessible to most college students.")

    add_styled_heading(doc, "1.3 System Objectives", level=2)
    add_body_p(doc, "To resolve these deficiencies, the AI Interview Analyzer system accomplishes five core objectives:")
    add_bullet_p(doc, "Objective 1", "Develop a high-accuracy, multi-rubric Machine Learning Scoring Engine evaluating Semantic Similarity (25%), Concept Coverage (30%), Technical Depth (25%), and Keyword Alignment (20%).")
    add_bullet_p(doc, "Objective 2", "Incorporate decoupled Speech Processing via Faster-Whisper to transcribe verbal responses and calculate speaking rate (Target: 110–160 WPM) and filler word distribution.")
    add_bullet_p(doc, "Objective 3", "Integrate Computer Vision via MediaPipe Face Mesh (478 3D landmarks) to track eye gaze stability and head posture (pitch, yaw, roll).")
    add_bullet_p(doc, "Objective 4", "Construct a responsive Single-Page Application (SPA) frontend with real-time audio/video feedback, resume parsing, and interactive PDF report generation.")
    add_bullet_p(doc, "Objective 5", "Satisfy all academic university practical requirements including classification benchmarking (KNN, SVM, Decision Tree), feature ablation to address target leakage, and unsupervised K-Means clustering.")

    add_styled_heading(doc, "1.4 System Architecture Overview", level=2)
    add_body_p(doc, "The system follows a decoupled, three-tier modular architecture spanning the Presentation Layer (HTML5/CSS3/JavaScript SPA), Application Gateway (FastAPI in Python 3.11), and Data & Model Execution Layer (SQLite, SentenceTransformer, Random Forest, Faster-Whisper, and MediaPipe).")
    
    # Diagram 1: System Architecture
    add_image_safe(doc, "docs/diagrams/01_system_architecture.png", "Figure 1.1: AI Interview Analyzer — Overall System Architecture Diagram", width=Inches(6.2))

    add_styled_heading(doc, "1.5 End-to-End Interview Workflow", level=2)
    add_body_p(doc, "The candidate journey flows sequentially through candidate setup and resume parsing, hardware device checking (microphone and webcam), dynamic question generation, live recording with simultaneous visual tracking, transcription, ML multi-rubric grading, and comprehensive report delivery.")

    # Diagram 2: Interview Workflow
    add_image_safe(doc, "docs/diagrams/02_interview_workflow.png", "Figure 1.2: End-to-End Candidate Interview Lifecycle Workflow", width=Inches(6.2))

    doc.add_page_break()

    # ==========================================================================
    # CHAPTER 2 — DATASET SELECTION & RECONCILIATION
    # ==========================================================================
    print("Writing Chapter 2: Dataset Selection...")
    add_styled_heading(doc, "CHAPTER 2 — DATASET SELECTION & RECONCILIATION", level=1)

    add_styled_heading(doc, "2.1 Multi-Source Dataset Architecture", level=2)
    add_body_p(doc, "To construct an objective, resilient technical interview evaluation system, training cannot rely solely on brief textbook definitions. Natural candidate answers exhibit varying lengths, speech filler artifacts, colloquial phrasing, and occasional off-topic evasions. Therefore, the training corpus was curated from three distinct data streams totaling 3,193 raw records:")
    add_bullet_p(doc, "1. Academic Technical QA Corpus", "1,806 verified question-answer pairs spanning core computer science disciplines: Object-Oriented Programming, Data Structures, Algorithms, Databases, and Software Engineering principles.")
    add_bullet_p(doc, "2. Conversational Technical Interview Corpus", "1,227 records sourced from the Hugging Face Technical Interview Coach repository (hf_train.jsonl: 1,104, hf_val.jsonl: 123), capturing realistic conversational explanations and varied technical depth.")
    add_bullet_p(doc, "3. Curated Adversarial Hard Negatives", "160 adversarial instances representing evasive responses ('I don't know', 'skip'), gibberish, one-word answers, and irrelevant statements to train zero-floor penalty heuristics.")

    add_styled_heading(doc, "2.2 Mathematical Dataset Reconciliation", level=2)
    add_body_p(doc, "A critical requirement of academic validation is reconciling how the 3,193 total available records relate to the 2,651 production training records used by the Random Forest model. To preserve strict empirical integrity and avoid data snooping, the Academic Corpus validation partition (270 records) and held-out test partition (272 records) were strictly excluded from model fitting:")
    add_body_p(doc, "Grand Multi-Source Corpus: 1,806 (Academic) + 1,227 (Conversational) + 160 (Hard Negatives) = 3,193 Total Records.")
    add_body_p(doc, "Reserved Held-Out Evaluation Partitions: 270 (Validation Split) + 272 (Test Split) = 542 Records.")
    add_body_p(doc, "Production Training Dataset: 3,193 – 542 = 2,651 Records (comprising 1,264 Academic Train + 1,227 Conversational + 160 Hard Negatives).")

    # Table 2.1: Dataset Reconciliation Table
    add_styled_heading(doc, "2.3 Dataset Reconciliation Table", level=2)
    rec_headers = ["Dataset Partition", "File Location", "Record Count", "Role in Pipeline", "Nulls", "Duplicates"]
    rec_rows = [
        ["Academic QA (Train)", "ml/datasets/processed/train_processed.csv", "1,264", "Supervised Training & Fitting", "0", "0"],
        ["Academic QA (Val)", "ml/datasets/processed/val_processed.csv", "270", "Hyperparameter Validation (Held-Out)", "0", "0"],
        ["Academic QA (Test)", "ml/datasets/processed/test_processed.csv", "272", "Independent Benchmark (Held-Out)", "0", "0"],
        ["Conversational QA", "ml/datasets/qa/hf_train.jsonl + val", "1,227", "Conversational Training Corpus", "0", "0"],
        ["Hard Negatives", "Domain-Curated Adversarial Pool", "160", "Zero-Floor Penalty Robustness", "0", "0"],
        ["Grand Ingested Corpus", "All Combined Sources", "3,193", "Total Ingested Data Stream", "0", "0"],
        ["Held-Out Partitions", "val_scored.csv + test_scored.csv", "542", "Strictly Reserved for Evaluation", "0", "0"],
        ["Production Training Set", "ml/datasets/features/train_scored.csv", "2,651", "Final Random Forest Regressor Fit", "0", "0"]
    ]
    t_rec = doc.add_table(rows=len(rec_rows) + 1, cols=len(rec_headers))
    for c_idx, h in enumerate(rec_headers):
        t_rec.rows[0].cells[c_idx].paragraphs[0].add_run(h)
    for r_idx, row in enumerate(rec_rows):
        for c_idx, val in enumerate(row):
            t_rec.rows[r_idx + 1].cells[c_idx].paragraphs[0].add_run(val)
    format_table(t_rec, header_bg="1E3A8A")

    add_body_p(doc, "Table 2.1: Complete Multi-Source Dataset Reconciliation & Partition Accounting.")

    add_styled_heading(doc, "2.4 Dataset Provenance, Sources & Licenses", level=2)
    add_body_p(doc, "All datasets utilize open, documented academic sources:")
    add_bullet_p(doc, "Academic Technical Question Bank", "Curated from standard computer science curriculum problem sets covering Python, OOP, DSA, and databases (Non-commercial Academic Research Use).")
    add_bullet_p(doc, "Hugging Face Interview Coach", "Open-source interview question-answer dataset hosted on Hugging Face Hub (Apache 2.0 License).")
    add_bullet_p(doc, "SentenceTransformer Weights", "Pre-trained all-MiniLM-L6-v2 model weights trained on 1B+ sentence pairs (Apache 2.0 License).")
    add_bullet_p(doc, "Faster-Whisper STT", "OpenAI Whisper weights converted to CTranslate2 format (MIT License).")

    doc.add_page_break()

    # ==========================================================================
    # CHAPTER 3 — DATA PREPROCESSING & NLP FEATURE PIPELINES
    # ==========================================================================
    print("Writing Chapter 3: Preprocessing & Features...")
    add_styled_heading(doc, "CHAPTER 3 — DATA PREPROCESSING & NLP FEATURE PIPELINES", level=1)

    add_styled_heading(doc, "3.1 Data Cleaning & Normalization Pipeline", level=2)
    add_body_p(doc, "Raw candidate text exhibits irregular line breaks, multiple whitespace characters, and punctuation artifacts. The automated preprocessing pipeline (ml/prepare_academic_dataset.py) executes the following sequence:")
    add_bullet_p(doc, "1. Whitespace Collapse", "All tabs, carriage returns (\\r\\n), and consecutive spaces are collapsed into single space delimiters while preserving technical syntax (e.g., C++, O(n log n)).")
    add_bullet_p(doc, "2. Null & Integrity Audit", "Every record is verified to contain non-empty question and answer fields. Exactly zero null records exist across all final processed splits.")
    add_bullet_p(doc, "3. Exact Deduplication", "No duplicate question-answer pairs exist within any partition or across the train-test boundary.")

    add_styled_heading(doc, "3.2 Extracted Linguistic & Semantic Features", level=2)
    add_body_p(doc, "For every technical Q&A pair, six continuous features are extracted for machine learning evaluation:")
    add_bullet_p(doc, "1. semantic_similarity", "Cosine similarity between 384-dimensional question and candidate answer embeddings via SentenceTransformer('all-MiniLM-L6-v2'). Mathematically ranges in [-1.0, 1.0].")
    add_bullet_p(doc, "2. lexical_overlap", "Jaccard similarity index measuring word token intersection between question and answer: J(Q, A) = |Q ∩ A| / |Q ∪ A|.")
    add_bullet_p(doc, "3. word_count", "Total count of alphanumeric word tokens in the candidate answer.")
    add_bullet_p(doc, "4. unique_word_ratio", "Type-Token Ratio (TTR) measuring vocabulary richness: |unique tokens| / |total tokens|.")
    add_bullet_p(doc, "5. avg_word_length", "Mean character length per word token, serving as a proxy for technical nomenclature complexity.")
    add_bullet_p(doc, "6. *_scaled Features", "Z-score standardized features computed via StandardScaler fitted strictly on the training partition.")

    add_styled_heading(doc, "3.3 Feature Scaling Isolation Guarantee", level=2)
    add_body_p(doc, "To ensure rigorous scientific validity, the StandardScaler was fitted strictly on the 1,264 training records of the Academic Corpus:")
    add_body_p(doc, "Fitted Scaler Parameters (ml/models/academic_scaler.pkl):")
    add_bullet_p(doc, "semantic_similarity", "Mean = 0.6481, Std = 0.1534")
    add_bullet_p(doc, "lexical_overlap", "Mean = 0.1171, Std = 0.0480")
    add_bullet_p(doc, "word_count", "Mean = 17.4367, Std = 3.1162")
    add_bullet_p(doc, "unique_word_ratio", "Mean = 0.9405, Std = 0.0673")
    add_bullet_p(doc, "avg_word_length", "Mean = 6.3168, Std = 0.9963")
    add_body_p(doc, "These fitted parameters were saved to disk and used to transform the validation and test splits without refitting, eliminating lookahead bias.")

    doc.add_page_break()

    # ==========================================================================
    # CHAPTER 4 — EXPLORATORY DATA ANALYSIS (EDA)
    # ==========================================================================
    print("Writing Chapter 4: EDA...")
    add_styled_heading(doc, "CHAPTER 4 — EXPLORATORY DATA ANALYSIS (EDA) & STATISTICS", level=1)

    add_styled_heading(doc, "4.1 Statistical Summary of Training Corpus", level=2)
    add_body_p(doc, "The training dataset of 1,264 records was analyzed across all numerical dimensions. Table 4.1 summarizes the descriptive statistics.")

    # Table 4.1: Statistical Summary Table
    eda_headers = ["Metric", "semantic_similarity", "lexical_overlap", "word_count", "unique_word_ratio", "avg_word_length"]
    eda_rows = [
        ["Count", "1,264", "1,264", "1,264", "1,264", "1,264"],
        ["Mean", "0.6481", "0.1171", "17.44", "0.9405", "6.32"],
        ["Std Dev", "0.1535", "0.0480", "3.12", "0.0674", "1.00"],
        ["Min", "-0.0043", "0.0000", "12.00", "0.6800", "3.92"],
        ["25% (Q1)", "0.5518", "0.0833", "15.00", "0.9091", "5.65"],
        ["50% (Median)", "0.6723", "0.1176", "17.00", "0.9444", "6.18"],
        ["75% (Q3)", "0.7634", "0.1500", "19.00", "1.0000", "6.83"],
        ["Max", "0.9128", "0.3200", "35.00", "1.0000", "12.71"]
    ]
    t_eda = doc.add_table(rows=len(eda_rows) + 1, cols=len(eda_headers))
    for c_idx, h in enumerate(eda_headers):
        t_eda.rows[0].cells[c_idx].paragraphs[0].add_run(h)
    for r_idx, row in enumerate(eda_rows):
        for c_idx, val in enumerate(row):
            t_eda.rows[r_idx + 1].cells[c_idx].paragraphs[0].add_run(val)
    format_table(t_eda, header_bg="1E3A8A")

    add_body_p(doc, "Table 4.1: Parametric Summary Statistics for the Training Split (N = 1,264).")

    add_styled_heading(doc, "4.2 Key Findings from Exploratory Analysis", level=2)
    add_bullet_p(doc, "1. Normal Distribution of Semantic Similarity", "Median similarity is 0.6723 with IQR [0.5518, 0.7634], demonstrating robust separation between accurate and weak answers.")
    add_bullet_p(doc, "2. Negative Cosine Similarity Outlier (-0.0043)", "The minimum similarity is -0.0043, confirming that raw cosine similarity mathematically spans [-1.0, 1.0]. Unrelated answers occasionally yield near-orthogonal or slightly obtuse embedding angles.")
    add_bullet_p(doc, "3. High Vocabulary Richness (TTR = 0.94)", "Candidate answers exhibit minimal repetitiveness, with an average unique word ratio of 94.05%.")
    add_bullet_p(doc, "4. Low Inter-Feature Multicollinearity", "Variance Inflation Factor (VIF) analysis confirms all VIF values are below 2.5 (well below the conservative threshold of 5.0), ensuring numerical stability during model training.")

    doc.add_page_break()

    # ==========================================================================
    # CHAPTER 5 — DATA VISUALIZATION
    # ==========================================================================
    print("Writing Chapter 5: Visualizations...")
    add_styled_heading(doc, "CHAPTER 5 — DATA VISUALIZATION & DISTRIBUTIONS", level=1)

    add_styled_heading(doc, "5.1 Feature Correlation Analysis", level=2)
    add_body_p(doc, "Figure 5.1 illustrates the Pearson correlation heatmap across all extracted text features. Semantic similarity shows moderate positive correlation with lexical overlap (r = +0.42), indicating that candidates who use relevant domain keywords also achieve higher conceptual alignment.")

    add_image_safe(doc, "ml/eda/plots/feature_correlation_heatmap.png", "Figure 5.1: Pearson Correlation Heatmap across Extracted NLP Features", width=Inches(5.5))

    add_styled_heading(doc, "5.2 Target Class & Similarity Distributions", level=2)
    add_body_p(doc, "The provisional binary quality target distribution shows approximately 84.5% of responses categorized as Needs Improvement (Class 0) and 15.5% as Proficient (Class 1), representing a natural class imbalance of ~5.45:1.")

    add_image_safe(doc, "ml/eda/plots/target_distribution.png", "Figure 5.2: Provisional Target Class Distribution (Imbalance Ratio: ~5.45 : 1)", width=Inches(5.0))

    add_styled_heading(doc, "5.3 Semantic Similarity Density Curve", level=2)
    add_body_p(doc, "The empirical distribution of SentenceTransformer semantic similarity demonstrates a smooth, unimodal curve centered around 0.65.")

    add_image_safe(doc, "ml/eda/plots/semantic_similarity_distribution.png", "Figure 5.3: Semantic Similarity Density Distribution (Empirical Min: -0.0043, Max: 0.9128)", width=Inches(5.0))

    doc.add_page_break()

    # ==========================================================================
    # CHAPTER 6 — MODEL EVALUATION & PERFORMANCE METRICS
    # ==========================================================================
    print("Writing Chapter 6: Evaluation & Leakage...")
    add_styled_heading(doc, "CHAPTER 6 — MODEL EVALUATION, METRICS & LEAKAGE ABLATION", level=1)

    add_styled_heading(doc, "6.1 Academic Classification: Target Leakage Diagnosis", level=2)
    add_body_p(doc, "In the university syllabus practicals, a provisional binary classification target was established to distinguish Proficient answers from those Needing Improvement:")
    add_body_p(doc, "Class 1 (Proficient): semantic_similarity >= 0.70 AND word_count >= 20. Class 0: Otherwise.")
    add_body_p(doc, "Target Leakage Finding: When semantic_similarity and word_count were included as input features in Experiment A, the Decision Tree achieved 100% Accuracy, Precision, Recall, and ROC-AUC. This occurred because the decision tree isolated the exact mathematical hypercube [>= 0.70, >= 20]. While demonstrating rule learning, this constitutes target leakage if presented as an independent scoring model.")

    add_styled_heading(doc, "6.2 Experiment A (Proxy) vs. Experiment B (Ablated) Results", level=2)
    add_body_p(doc, "To provide academic transparency, Experiment B was conducted by strictly ablating semantic_similarity and word_count from the feature set. The models were retrained exclusively on lexical_overlap, unique_word_ratio, and avg_word_length. Table 6.1 compares both experiments on the held-out test partition (N = 272).")

    # Table 6.1: Model Comparison Table
    m_headers = ["Experiment", "Algorithm", "Accuracy", "Precision", "Recall", "Macro F1", "ROC-AUC", "PR-AUC"]
    m_rows = [
        ["Baseline", "Dummy (Majority)", "0.8493", "0.0000", "0.0000", "0.4592", "0.5000", "0.1507"],
        ["Exp A (Proxy)", "KNN (k=5)", "0.9596", "0.8750", "0.8537", "0.9202", "0.9906", "0.9341"],
        ["Exp A (Proxy)", "SVM (RBF, C=10)", "0.9706", "1.0000", "0.8049", "0.9374", "0.9984", "0.9907"],
        ["Exp A (Proxy)", "Decision Tree", "1.0000", "1.0000", "1.0000", "1.0000", "1.0000", "1.0000"],
        ["Exp B (Ablated)", "KNN (k=5)", "0.8309", "0.3333", "0.1220", "0.5422", "0.6603", "0.2310"],
        ["Exp B (Ablated)", "SVM (RBF, C=10)", "0.6471", "0.2477", "0.6585", "0.5582", "0.6989", "0.2790"],
        ["Exp B (Ablated)", "Decision Tree", "0.8603", "0.5484", "0.4146", "0.6959", "0.7330", "0.4420"]
    ]
    t_mod = doc.add_table(rows=len(m_rows) + 1, cols=len(m_headers))
    for c_idx, h in enumerate(m_headers):
        t_mod.rows[0].cells[c_idx].paragraphs[0].add_run(h)
    for r_idx, row in enumerate(m_rows):
        for c_idx, val in enumerate(row):
            t_mod.rows[r_idx + 1].cells[c_idx].paragraphs[0].add_run(val)
    format_table(t_mod, header_bg="1E3A8A")

    add_body_p(doc, "Table 6.1: Comprehensive Classification Performance on Held-Out Test Split (N = 272).")

    add_styled_heading(doc, "6.3 Confusion Matrices & Evaluation Curves", level=2)
    add_body_p(doc, "Figures 6.1, 6.2, and 6.3 show the test partition confusion matrices for Decision Tree, SVM, and KNN classifiers under Experiment A.")

    add_image_safe(doc, "ml/evaluation/confusion_matrices/confusion_matrix_decision_tree_test.png", "Figure 6.1: Confusion Matrix on Held-Out Test Set — Decision Tree Classifier", width=Inches(4.5))
    add_image_safe(doc, "ml/evaluation/confusion_matrices/confusion_matrix_svm_classifier_test.png", "Figure 6.2: Confusion Matrix on Held-Out Test Set — SVM Classifier", width=Inches(4.5))

    add_styled_heading(doc, "6.4 Receiver Operating Characteristic (ROC) & PR Curves", level=2)
    add_body_p(doc, "Because the dataset exhibits class imbalance (15.5% positive class), Precision-Recall curves provide the most reliable assessment of classification performance. In Experiment B, the Decision Tree achieves an Average Precision (PR-AUC) of 0.4420, substantially outperforming the 0.1507 random baseline.")

    add_image_safe(doc, "ml/evaluation/roc_curves/comparative_roc_test_experiment_a_(full_features).png", "Figure 6.3: Comparative ROC Curves on Held-Out Test Split (Experiment A)", width=Inches(5.0))
    add_image_safe(doc, "ml/evaluation/precision_recall_curves/comparative_pr_test_experiment_b_(feature_ablation).png", "Figure 6.4: Comparative Precision-Recall Curves on Held-Out Test Split (Experiment B Ablated)", width=Inches(5.0))

    doc.add_page_break()

    # ==========================================================================
    # CHAPTER 7 — MODEL BUILDING, REGRESSION & MULTIMODAL INFERENCE
    # ==========================================================================
    print("Writing Chapter 7: Regression & Multimodal...")
    add_styled_heading(doc, "CHAPTER 7 — MODEL BUILDING, REGRESSION & MULTIMODAL INFERENCE", level=1)

    add_styled_heading(doc, "7.1 Random Forest Regression Architecture", level=2)
    add_body_p(doc, "The production technical grading engine utilizes an ensemble Random Forest Regressor (sklearn.ensemble.RandomForestRegressor) trained on 2,651 multi-source technical Q&A pairs. The model architecture uses 350 decision trees with a maximum tree depth of 10.")

    add_styled_heading(doc, "7.2 Continuous Target Score Interpretation", level=2)
    add_body_p(doc, "The target score in the training dataset is generated via an institutional multi-criteria evaluation rubric:")
    add_body_p(doc, "Target Score = 0.30 x Concept Coverage + 0.25 x Technical Depth + 0.25 x Semantic Similarity + 0.20 x Keyword Alignment")
    add_body_p(doc, "Adversarial responses (< 3 words, explicit evasions, or off-topic statements) receive an automatic zero-floor penalty. The Random Forest model therefore acts as a high-capacity, non-linear function approximator of this multi-rubric institutional grading policy.")

    add_styled_heading(doc, "7.3 Empirical Regression Performance", level=2)
    add_body_p(doc, "Performance evaluated on the held-out test partition (N = 272):")
    add_bullet_p(doc, "Test Mean Absolute Error (MAE)", "0.4798 points (on a 0–100 continuous grading scale).")
    add_bullet_p(doc, "Test Root Mean Squared Error (RMSE)", "0.6596 points.")
    add_bullet_p(doc, "Test Coefficient of Determination (R²)", "0.9985.")
    add_bullet_p(doc, "5-Fold Cross-Validation MAE", "Mean MAE = 0.472 across 5 folds [0.4828, 0.4558, 0.4532, 0.4963, 0.4718].")
    add_bullet_p(doc, "5-Fold Cross-Validation R²", "Mean R² = 0.9976 [0.9976, 0.9990, 0.9984, 0.9940, 0.9990].")

    # Table 7.1: Feature Importance Table
    add_styled_heading(doc, "7.4 Feature Importance Breakdown", level=2)
    fi_headers = ["Feature Name", "Importance Weight", "Percentage", "Diagnostic Role in Scoring"]
    fi_rows = [
        ["semantic_similarity", "0.4187", "41.87%", "Primary driver measuring core conceptual alignment"],
        ["keyword_alignment", "0.2843", "28.43%", "Measures domain terminology match with question context"],
        ["concept_coverage", "0.2529", "25.29%", "Evaluates inclusion of required technical entities"],
        ["answer_length", "0.0400", "4.00%", "Calibrates answer elaboration, penalizing truncated answers"],
        ["technical_depth", "0.0040", "0.40%", "Measures technical nomenclature and vocabulary sophistication"],
        ["question_length", "0.0002", "0.02%", "Context invariant ensuring zero question length bias"]
    ]
    t_fi = doc.add_table(rows=len(fi_rows) + 1, cols=len(fi_headers))
    for c_idx, h in enumerate(fi_headers):
        t_fi.rows[0].cells[c_idx].paragraphs[0].add_run(h)
    for r_idx, row in enumerate(fi_rows):
        for c_idx, val in enumerate(row):
            t_fi.rows[r_idx + 1].cells[c_idx].paragraphs[0].add_run(val)
    format_table(t_fi, header_bg="1E3A8A")

    add_body_p(doc, "Table 7.1: Random Forest Regressor Feature Importance Breakdown (350 Trees).")

    add_styled_heading(doc, "7.5 ML Training Pipeline Architecture", level=2)
    add_body_p(doc, "Figure 7.1 illustrates the complete ML training pipeline from data ingestion to model artifact persistence.")

    # Diagram 3: ML Training Pipeline
    add_image_safe(doc, "docs/diagrams/03_ml_training_pipeline.png", "Figure 7.1: Machine Learning Model Training Pipeline Diagram", width=Inches(6.2))

    add_styled_heading(doc, "7.6 Real-Time ML Inference & Multimodal Scoring Workflow", level=2)
    add_body_p(doc, "Figure 7.2 displays the live inference workflow. Candidate audio is transcribed by Faster-Whisper, encoded into embeddings, evaluated across 6 features by the Random Forest model, and passed through zero-floor guardrails.")

    # Diagram 4: ML Prediction Workflow
    add_image_safe(doc, "docs/diagrams/04_ml_prediction_workflow.png", "Figure 7.2: Real-Time ML Inference and Multi-Criteria Scoring Workflow", width=Inches(6.2))

    add_styled_heading(doc, "7.7 Strict Multimodal Architectural Decoupling", level=2)
    add_body_p(doc, "A fundamental architectural principle verified in this project is that the Random Forest model operates strictly on text NLP features. It does NOT take raw audio waveforms or raw video frames. Audio (Faster-Whisper) and Video (MediaPipe) run through decoupled, specialized microservices; their metrics are synthesized by the FastAPI application gateway into the final report.")

    doc.add_page_break()

    # ==========================================================================
    # CHAPTER 8 — SYSTEM DESIGN, UML & K-MEANS PATTERN DISCOVERY
    # ==========================================================================
    print("Writing Chapter 8: UML & Clustering...")
    add_styled_heading(doc, "CHAPTER 8 — SYSTEM DESIGN, UML & K-MEANS PATTERN DISCOVERY", level=1)

    add_styled_heading(doc, "8.1 Use Case Architecture", level=2)
    add_body_p(doc, "Figure 8.1 depicts the UML Use Case Diagram illustrating the separation between Candidate (User) interactions and Administrative governance.")

    # Diagram 5: Use Case Diagram
    add_image_safe(doc, "docs/diagrams/05_use_case_diagram.png", "Figure 8.1: UML Use Case Diagram: User and Administrator Capabilities", width=Inches(6.2))

    add_styled_heading(doc, "8.2 Database Entity-Relationship Schema", level=2)
    add_body_p(doc, "Figure 8.2 presents the relational database schema implemented in SQLite with SQLAlchemy ORM, showing primary keys, foreign keys, and cardinalities across users, interviews, questions, user_answers, feedback, and system_logs.")

    # Diagram 6: Database ER Diagram
    add_image_safe(doc, "docs/diagrams/06_database_er_diagram.png", "Figure 8.2: Database Entity-Relationship (ER) Schema Diagram", width=Inches(6.2))

    add_styled_heading(doc, "8.3 UML Sequence Diagram", level=2)
    add_body_p(doc, "Figure 8.3 models the complete synchronous and asynchronous communication flow between Candidate, Frontend UI, FastAPI Gateway, Whisper Service, ML Scoring Engine, and SQLite Database during an interview session.")

    # Diagram 7: Sequence Diagram
    add_image_safe(doc, "docs/diagrams/07_sequence_diagram.png", "Figure 8.3: UML Sequence Diagram: Interview Session Lifecycle Execution", width=Inches(6.2))

    add_styled_heading(doc, "8.4 Unsupervised Behavioral Answer Clustering via K-Means", level=2)
    add_body_p(doc, "To uncover latent behavioral answer patterns without relying on labels, K-Means clustering was executed on the standardized 5-feature space across k in [2, 10].")
    add_bullet_p(doc, "Optimal Cluster Count", "Selected k = 3 based on the Elbow heuristic and the global Silhouette Score maximum of 0.2311.")
    add_bullet_p(doc, "PCA 2D Visualization Variance", "Principal Component Analysis captures 65.91% of total variance (PC1: 39.08%, PC2: 26.83%).")

    # Table 8.1: Silhouette Score Progression
    sil_headers = ["k Value", "Silhouette Score", "Inertia (SSE)", "Cluster Evaluation Status"]
    sil_rows = [
        ["k = 2", "0.2167", "4,482.11", "Underfitting (Oversimplified bipartite split)"],
        ["k = 3", "0.2311", "3,831.56", "Optimal Cohesion & Silhouette Peak"],
        ["k = 4", "0.1895", "3,341.20", "Silhouette decline (Cluster overfragmentation)"],
        ["k = 5", "0.1890", "2,987.45", "Within-cluster variance plateau"],
        ["k = 6", "0.1786", "2,698.32", "High inter-cluster overlap"],
        ["k = 7", "0.1831", "2,465.18", "Local plateau"],
        ["k = 8", "0.1766", "2,284.90", "Diminishing marginal returns"],
        ["k = 9", "0.1721", "2,143.70", "Over-segmentation"],
        ["k = 10", "0.1739", "2,012.44", "Unstable cluster centroids"]
    ]
    t_sil = doc.add_table(rows=len(sil_rows) + 1, cols=len(sil_headers))
    for c_idx, h in enumerate(sil_headers):
        t_sil.rows[0].cells[c_idx].paragraphs[0].add_run(h)
    for r_idx, row in enumerate(sil_rows):
        for c_idx, val in enumerate(row):
            t_sil.rows[r_idx + 1].cells[c_idx].paragraphs[0].add_run(val)
    format_table(t_sil, header_bg="1E3A8A")

    add_body_p(doc, "Table 8.1: Silhouette Score and Inertia Progression for k = 2 through k = 10.")

    add_styled_heading(doc, "8.5 Discovered Candidate Response Archetypes", level=2)
    add_body_p(doc, "Profiling the unscaled centroids of the 1,264 training records reveals three distinct candidate response styles:")
    add_bullet_p(doc, "Cluster 0: Extended / Substantive (N = 323, 25.6%)", "Highest word count (20.0 words), highest lexical overlap (0.144), and high semantic similarity (0.717). Represents candidates who articulate thorough, well-structured answers.")
    add_bullet_p(doc, "Cluster 1: Low Alignment / Divergent (N = 325, 25.7%)", "Lowest semantic similarity (0.448), lowest lexical overlap (0.039), and shortest word count (15.4 words). Contains 0% Class 1 candidates, representing weak or off-topic responses.")
    add_bullet_p(doc, "Cluster 2: Concise Technical (N = 616, 48.7%)", "High semantic similarity (0.717), highest average word length (6.83 chars), and highest unique word ratio (0.970). Represents candidates who provide precise technical definitions.")

    add_image_safe(doc, "ml/clustering/plots/elbow_curve.png", "Figure 8.4: K-Means Elbow Method Curve (Inertia vs Number of Clusters k)", width=Inches(4.8))
    add_image_safe(doc, "ml/clustering/plots/pca_cluster_visualization.png", "Figure 8.5: 2D PCA Projection of Discovered K-Means Clusters (Total Explained Variance: 65.91%)", width=Inches(5.2))

    doc.add_page_break()

    # ==========================================================================
    # CHAPTER 9 — SYSTEM TESTING, VERIFICATION & FUTURE WORK
    # ==========================================================================
    print("Writing Chapter 9: Testing & Future Work...")
    add_styled_heading(doc, "CHAPTER 9 — SYSTEM TESTING, VERIFICATION & FUTURE WORK", level=1)

    add_styled_heading(doc, "9.1 Comprehensive Test Suite Verification", level=2)
    add_body_p(doc, "A complete automated test harness comprising 69 pytest tests across 10 test modules was executed. All 69 tests pass with 100% green status, verifying full application security, audio validation, evaluator heuristics, and database integrity.")

    # Table 9.1: Test Suite Summary
    test_headers = ["Test Module", "Test File", "Test Count", "Execution Status", "Primary Subsystems Verified"]
    test_rows = [
        ["Voice Interview", "tests/test_voice_interview_system.py", "12", "100% PASS", "Audio MIME, magic bytes, duration (1-300s), safe temp files"],
        ["Secure Engine", "tests/test_secure_question_engine.py", "13", "100% PASS", "Anti-leakage protection, question ID check, personalization"],
        ["Evaluator Rules", "tests/test_evaluator_rules.py", "10", "100% PASS", "Rules A-H, concept coverage, zero-floor non-answer guard"],
        ["Question Bank", "tests/test_question_bank_migration.py", "10", "100% PASS", "SQLite schema, question seeding (150+), difficulty pools"],
        ["Resume & Questions", "tests/test_resume_and_questions.py", "7", "100% PASS", "PyPDF parsing, skill taxonomy mapping, tailored questions"],
        ["Admin & Governance", "tests/test_admin_and_analytics.py", "7", "100% PASS", "Role-based auth, metrics aggregation, audit logging"],
        ["Live API & Voice", "tests/test_live_api.py", "1", "100% PASS", "Silent audio detection, short answer, polymorphism audio test"],
        ["No-Answer Guard", "tests/test_no_answer_detection.py", "1", "100% PASS", "Zero-floor clamp on evasions and non-answers"],
        ["Provider Fallback", "tests/test_provider_integration.py", "4", "100% PASS", "LLM fallback resilience, timeout handling, JSON schema"],
        ["Interview Sessions", "tests/test_interview_api.py", "4", "100% PASS", "Session start, submit answer, feedback synthesis, DB write"],
        ["Total Test Suite", "10 Test Files", "69", "100% PASS", "Complete Full-Stack Operational Verification"]
    ]
    t_test = doc.add_table(rows=len(test_rows) + 1, cols=len(test_headers))
    for c_idx, h in enumerate(test_headers):
        t_test.rows[0].cells[c_idx].paragraphs[0].add_run(h)
    for r_idx, row in enumerate(test_rows):
        for c_idx, val in enumerate(row):
            t_test.rows[r_idx + 1].cells[c_idx].paragraphs[0].add_run(val)
    format_table(t_test, header_bg="1E3A8A")

    add_body_p(doc, "Table 9.1: Automated Pytest Regression & Integration Test Suite Results (69/69 Passing).")

    add_styled_heading(doc, "9.2 Hardware & Software Execution Environment", level=2)
    add_bullet_p(doc, "Operating System", "Microsoft Windows 11 Home (64-bit)")
    add_bullet_p(doc, "Python Environment", "Python 3.11.0 Virtual Environment (venv)")
    add_bullet_p(doc, "Deep Learning Frameworks", "PyTorch 2.6.0+cpu, SentenceTransformers 3.4.1, Faster-Whisper 1.1.1 (CTranslate2)")
    add_bullet_p(doc, "Computer Vision", "Google MediaPipe 0.10.21 Face Landmarker (478 3D landmarks)")
    add_bullet_p(doc, "Backend Framework", "FastAPI 0.115.8, Uvicorn 0.34.0, SQLAlchemy 2.0.38, SQLite3")
    add_bullet_p(doc, "Testing Engine", "Pytest 9.1.1, AnyIO 4.14.2, Requests 2.32.3")

    add_styled_heading(doc, "9.3 Conclusion & Future Enhancements", level=2)
    add_body_p(doc, "The AI Interview Analyzer successfully fulfills all research and implementation objectives. By synthesizing semantic embeddings, ensemble regression trees, speech recognition, and facial landmark tracking, the platform delivers an objective, reproducible, and private technical interview preparation experience.")
    add_body_p(doc, "Recommended future enhancements include:")
    add_bullet_p(doc, "1. Coding Sandbox Integration", "Embedding an interactive in-browser Monaco/WebAssembly code editor for live algorithmic problem solving.")
    add_bullet_p(doc, "2. Emotion & Micro-expression Analysis", "Extending MediaPipe landmarks to compute facial action units for subtle anxiety and confidence tracking.")
    add_bullet_p(doc, "3. Multilingual Support", "Leveraging Whisper's multilingual translation capabilities to support regional languages.")

    doc.add_page_break()

    # ==========================================================================
    # CHAPTER 10 — BIBLIOGRAPHY
    # ==========================================================================
    print("Writing Chapter 10: Bibliography...")
    add_styled_heading(doc, "CHAPTER 10 — BIBLIOGRAPHY & TECHNICAL REFERENCES", level=1)

    references = [
        "Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP 2019), pp. 3982–3992.",
        "Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023). Robust Speech Recognition via Large-Scale Weak Supervision. In International Conference on Machine Learning (ICML 2023), PMLR 202:28492–28518.",
        "Lugaresi, C., Tang, J., Nash, H., McClanahan, C., Uboweja, E., Hays, M., Zhang, F., et al. (2019). MediaPipe: A Framework for Building Perception Pipelines. arXiv preprint arXiv:1906.08172.",
        "Breiman, L. (2001). Random Forests. Machine Learning, 45(1), 5–32.",
        "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825–2830.",
        "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention Is All You Need. In Advances in Neural Information Processing Systems (NeurIPS 2017), 30, 5998–6008.",
        "Rousseeuw, P. J. (1987). Silhouettes: A Graphical Aid to the Interpretation and Validation of Cluster Analysis. Journal of Computational and Applied Mathematics, 20, 53–65.",
        "Tiangolo, S. (2018). FastAPI: High Performance, Easy to Learn, Fast to Code, Ready for Production. https://fastapi.tiangolo.com/.",
        "Bayer, M. (2012). SQLAlchemy: The Database Toolkit for Python. In The Architecture of Open Source Applications, Volume II.",
        "MacQueen, J. (1967). Some Methods for Classification and Analysis of Multivariate Observations. In Proceedings of the 5th Berkeley Symposium on Mathematical Statistics and Probability, 1, 281–297."
    ]

    for idx, ref in enumerate(references, 1):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.line_spacing = 1.15
        r_num = p_ref.add_run(f"[{idx}] ")
        r_num.font.name = "Arial"
        r_num.font.size = Pt(10)
        r_num.font.bold = True
        r_num.font.color.rgb = COLOR_PRIMARY
        r_txt = p_ref.add_run(ref)
        r_txt.font.name = "Arial"
        r_txt.font.size = Pt(10)
        r_txt.font.color.rgb = COLOR_DARK

    print(f"Saving Document to {DOCX_OUTPUT}...")
    doc.save(DOCX_OUTPUT)
    print(f"Document successfully created: {DOCX_OUTPUT} ({os.path.getsize(DOCX_OUTPUT)} bytes)")

if __name__ == "__main__":
    build_report()

"""
================================================================================
AI INTERVIEW ANALYZER - SYSTEM ARCHITECTURE & WORKFLOW DIAGRAMS GENERATOR
Generates 7 publication-grade high-resolution diagrams (300 DPI) for the project report:
1. System Architecture Diagram
2. Interview Workflow Diagram
3. ML Training Pipeline Diagram
4. ML Prediction and Scoring Workflow
5. Use Case Diagram (User & Admin)
6. Database Entity-Relationship (ER) Diagram
7. Sequence Diagram (Session Lifecycle)
================================================================================
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

OUTPUT_DIR = os.path.join("docs", "diagrams")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Common styling palette
PRIMARY = "#1e3a8a"       # Deep Navy
SECONDARY = "#0284c7"     # Bright Blue
ACCENT = "#0d9488"        # Teal
SUCCESS = "#16a34a"       # Green
WARNING = "#d97706"       # Amber
PURPLE = "#7c3aed"        # Indigo/Purple
TEXT_DARK = "#0f172a"     # Slate 900
TEXT_MUTED = "#475569"    # Slate 600
BG_CARD = "#f8fafc"       # Slate 50
BORDER_COLOR = "#cbd5e1"  # Slate 300


# ------------------------------------------------------------------------------
# 1. OVERALL SYSTEM ARCHITECTURE DIAGRAM
# ------------------------------------------------------------------------------
def generate_system_architecture():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")

    # Title
    ax.text(7, 8.6, "AI INTERVIEW ANALYZER - OVERALL SYSTEM ARCHITECTURE", 
            ha="center", va="center", fontsize=15, fontweight="bold", color=PRIMARY)
    ax.text(7, 8.25, "Layered Multimodal Pipeline: Web Client, FastAPI Gateway, ML/Speech/Vision Services, and Persistent Storage",
            ha="center", va="center", fontsize=9.5, color=TEXT_MUTED)

    # 1. Client Layer (Top)
    client_box = FancyBboxPatch((0.6, 6.4), 12.8, 1.45, boxstyle="round,pad=0.1,rounding_size=0.15",
                                ec=SECONDARY, fc="#f0f9ff", lw=1.5)
    ax.add_patch(client_box)
    ax.text(1.0, 7.55, "FRONTEND PRESENTATION LAYER (Single Page Application)", fontsize=10.5, fontweight="bold", color=SECONDARY)
    
    components = [
        ("UI & Styling", "HTML5, CSS3, Glassmorphism\nResponsive Layout (320px - 1920px)"),
        ("Client Logic", "Vanilla JavaScript (ES6+)\nModular State & API Controller"),
        ("Media Capture", "WebRTC MediaStream API\nMic Audio Blob + Webcam Stream"),
        ("Report & Visuals", "Chart.js Visualizations\nLive Metric Meters & PDF Export")
    ]
    for i, (title, desc) in enumerate(components):
        x = 0.9 + i * 3.1
        box = FancyBboxPatch((x, 6.55), 2.9, 0.85, boxstyle="round,pad=0.05,rounding_size=0.1",
                             ec=BORDER_COLOR, fc="#ffffff", lw=1)
        ax.add_patch(box)
        ax.text(x + 1.45, 7.15, title, ha="center", va="center", fontsize=9, fontweight="bold", color=PRIMARY)
        ax.text(x + 1.45, 6.8, desc, ha="center", va="center", fontsize=7.5, color=TEXT_MUTED)

    # Down arrow to API
    ax.annotate("", xy=(7, 5.85), xytext=(7, 6.4),
                arrowprops=dict(arrowstyle="->", lw=2, color=SECONDARY))
    ax.text(7.2, 6.1, "HTTP REST / Multipart Form Audio", fontsize=8, fontweight="bold", color=SECONDARY)

    # 2. Application & API Gateway (Middle)
    api_box = FancyBboxPatch((0.6, 4.3), 12.8, 1.55, boxstyle="round,pad=0.1,rounding_size=0.15",
                             ec=PRIMARY, fc="#f8fafc", lw=1.5)
    ax.add_patch(api_box)
    ax.text(1.0, 5.55, "BACKEND APPLICATION GATEWAY (FastAPI + Python 3.11)", fontsize=10.5, fontweight="bold", color=PRIMARY)

    api_modules = [
        ("Auth & Security Router", "JWT Auth, Argon2 Password Hashing\nRole-Based Access (User/Admin)"),
        ("Interview Controller", "Session Management, Next Question\nAnswer Submission & Routing"),
        ("Multimodal Orchestrator", "Dispatches Audio, Video & Text\nAggregates Final Report Scores"),
        ("Resume & Question Engine", "PyPDF Resume Parser & Keyword Engine\n150+ Curated Question Bank")
    ]
    for i, (title, desc) in enumerate(api_modules):
        x = 0.9 + i * 3.1
        box = FancyBboxPatch((x, 4.45), 2.9, 0.95, boxstyle="round,pad=0.05,rounding_size=0.1",
                             ec=BORDER_COLOR, fc="#ffffff", lw=1)
        ax.add_patch(box)
        ax.text(x + 1.45, 5.15, title, ha="center", va="center", fontsize=9, fontweight="bold", color=PRIMARY)
        ax.text(x + 1.45, 4.75, desc, ha="center", va="center", fontsize=7.5, color=TEXT_MUTED)

    # Arrows to Processing & Storage
    ax.annotate("", xy=(3.5, 3.65), xytext=(3.5, 4.3), arrowprops=dict(arrowstyle="->", lw=2, color=ACCENT))
    ax.annotate("", xy=(7.0, 3.65), xytext=(7.0, 4.3), arrowprops=dict(arrowstyle="->", lw=2, color=WARNING))
    ax.annotate("", xy=(10.5, 3.65), xytext=(10.5, 4.3), arrowprops=dict(arrowstyle="->", lw=2, color=PURPLE))

    # 3. Processing Services (Bottom Row)
    # 3a. ML Text Scoring Engine
    ml_box = FancyBboxPatch((0.6, 0.6), 3.9, 3.0, boxstyle="round,pad=0.1,rounding_size=0.15",
                            ec=ACCENT, fc="#f0fdfa", lw=1.5)
    ax.add_patch(ml_box)
    ax.text(2.55, 3.3, "ML TEXT SCORING ENGINE", ha="center", fontsize=10, fontweight="bold", color=ACCENT)
    ml_items = [
        "SentenceTransformer ('all-MiniLM-L6-v2')",
        "384-Dimensional Embeddings & Cosine Sim",
        "Feature Extractor (Coverage, Depth, Overlap)",
        "Random Forest Regressor (350 Trees, Depth 10)",
        "Zero-Floor Heuristics (Non-Answer Blocker)",
        "Test MAE: 0.48 | RMSE: 0.66 | R²: 0.998"
    ]
    for idx, item in enumerate(ml_items):
        ax.text(0.8, 2.9 - idx * 0.38, f"• {item}", fontsize=7.6, color=TEXT_DARK)

    # 3b. Speech & Vision Services
    av_box = FancyBboxPatch((4.8, 0.6), 4.3, 3.0, boxstyle="round,pad=0.1,rounding_size=0.15",
                            ec=WARNING, fc="#fffbeb", lw=1.5)
    ax.add_patch(av_box)
    ax.text(6.95, 3.3, "AUDIO & VISION PROCESSING", ha="center", fontsize=10, fontweight="bold", color=WARNING)
    av_items = [
        "Faster-Whisper (OpenAI Whisper Small/Base)",
        "Speech-to-Text Transcription & Word Timestamps",
        "Pacing Analysis (WPM: Target 110-160)",
        "Speech Fillers Detection ('um', 'uh', 'like')",
        "MediaPipe Face Mesh (478 3D Landmarks)",
        "Eye Gaze & Head Pose Pitch/Yaw/Roll",
        "Visual Attention & Posture Confidence Metric"
    ]
    for idx, item in enumerate(av_items):
        ax.text(5.0, 2.9 - idx * 0.38, f"• {item}", fontsize=7.6, color=TEXT_DARK)

    # 3c. Database & Persistence
    db_box = FancyBboxPatch((9.4, 0.6), 4.0, 3.0, boxstyle="round,pad=0.1,rounding_size=0.15",
                            ec=PURPLE, fc="#faf5ff", lw=1.5)
    ax.add_patch(db_box)
    ax.text(11.4, 3.3, "PERSISTENCE & STORAGE", ha="center", fontsize=10, fontweight="bold", color=PURPLE)
    db_items = [
        "SQLite Relational Database Engine",
        "SQLAlchemy ORM (Async & Sync Sessions)",
        "Tables: users, interviews, questions",
        "Tables: user_answers, feedback, logs",
        "Pre-populated Curated Technical Questions",
        "JSON Session Cache & Performance History",
        "PDF Report Generator (WeasyPrint / ReportLab)"
    ]
    for idx, item in enumerate(db_items):
        ax.text(9.6, 2.9 - idx * 0.38, f"• {item}", fontsize=7.6, color=TEXT_DARK)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "01_system_architecture.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {out_path}")


# ------------------------------------------------------------------------------
# 2. INTERVIEW WORKFLOW DIAGRAM
# ------------------------------------------------------------------------------
def generate_interview_workflow():
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(6.5, 7.6, "END-TO-END INTERVIEW LIFECYCLE WORKFLOW", 
            ha="center", va="center", fontsize=14, fontweight="bold", color=PRIMARY)
    ax.text(6.5, 7.25, "Sequential Execution: Setup -> Real-time Audio/Video Capture -> Multi-Criteria Evaluation -> Comprehensive Report",
            ha="center", va="center", fontsize=9, color=TEXT_MUTED)

    steps = [
        ("Step 1: Setup & Profile", "User authenticates, selects Job Role, Experience Level (Junior/Mid/Senior), Tech Stacks, or uploads Resume for personalized extraction.", 0.8, 5.2, PRIMARY),
        ("Step 2: Device Check", "System tests microphone input levels, webcam video feed, and browser WebRTC compatibility before interview initiation.", 4.9, 5.2, SECONDARY),
        ("Step 3: Question Dispatch", "Backend question engine selects optimal questions or dynamically tailors queries matching candidate's resume keywords.", 9.0, 5.2, ACCENT),
        ("Step 4: Live Answer Capture", "Candidate records audio response while MediaPipe tracks face landmarks, head posture, and eye contact in real time.", 9.0, 2.2, WARNING),
        ("Step 5: Transcription & NLP", "Faster-Whisper converts speech to text. Text NLP extracts semantic similarity, technical depth, and concept coverage.", 4.9, 2.2, PURPLE),
        ("Step 6: Scoring & Report", "Random Forest Regressor infers technical score (0-100). Aggregator compiles speech & vision metrics into an interactive PDF report.", 0.8, 2.2, SUCCESS)
    ]

    for title, desc, x, y, color in steps:
        box = FancyBboxPatch((x, y), 3.3, 1.6, boxstyle="round,pad=0.08,rounding_size=0.12",
                             ec=color, fc="#ffffff", lw=1.5)
        ax.add_patch(box)
        # Header bar
        header_bar = FancyBboxPatch((x, y + 1.15), 3.3, 0.45, boxstyle="round,pad=0.04,rounding_size=0.08",
                                    ec=color, fc=color, lw=1)
        ax.add_patch(header_bar)
        ax.text(x + 1.65, y + 1.37, title, ha="center", va="center", fontsize=8.8, fontweight="bold", color="#ffffff")
        ax.text(x + 1.65, y + 0.55, desc, ha="center", va="center", fontsize=7.6, color=TEXT_DARK, wrap=True)

    # Workflow arrows
    # 1 -> 2
    ax.annotate("", xy=(4.9, 6.0), xytext=(4.1, 6.0), arrowprops=dict(arrowstyle="->", lw=2, color=SECONDARY))
    # 2 -> 3
    ax.annotate("", xy=(9.0, 6.0), xytext=(8.2, 6.0), arrowprops=dict(arrowstyle="->", lw=2, color=SECONDARY))
    # 3 -> 4 (down)
    ax.annotate("", xy=(10.65, 3.8), xytext=(10.65, 5.2), arrowprops=dict(arrowstyle="->", lw=2, color=SECONDARY))
    # 4 -> 5 (left)
    ax.annotate("", xy=(8.2, 3.0), xytext=(9.0, 3.0), arrowprops=dict(arrowstyle="->", lw=2, color=SECONDARY))
    # 5 -> 6 (left)
    ax.annotate("", xy=(4.1, 3.0), xytext=(4.9, 3.0), arrowprops=dict(arrowstyle="->", lw=2, color=SECONDARY))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "02_interview_workflow.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {out_path}")


# ------------------------------------------------------------------------------
# 3. ML TRAINING PIPELINE DIAGRAM
# ------------------------------------------------------------------------------
def generate_ml_training_pipeline():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(7, 7.6, "MACHINE LEARNING MODEL TRAINING PIPELINE", 
            ha="center", va="center", fontsize=14, fontweight="bold", color=PRIMARY)
    ax.text(7, 7.25, "From Multi-Source Corpus Ingestion to SentenceTransformer Feature Engineering and Random Forest Model Artifacts",
            ha="center", va="center", fontsize=9, color=TEXT_MUTED)

    blocks = [
        ("1. Data Sources", ["Academic QA (1,806)", "HF Interview Coach (1,227)", "Hard Negatives (160)", "Total Corpus: 3,193"], 0.6, 3.2, PRIMARY),
        ("2. Data Preparation", ["Duplicate Detection", "Missing Value Cleaning", "Token Extraction", "Strict Split Isolation"], 3.3, 3.2, SECONDARY),
        ("3. Feature Extraction", ["MiniLM-L6-v2 Embeddings", "Cosine Similarity", "Coverage & Depth Rubrics", "Keyword Overlap Ratios"], 6.0, 3.2, ACCENT),
        ("4. Dataset Partition", ["Train Set: 2,651 rows", "Val Set: 270 rows", "Test Set: 272 rows", "Zero Snooping / Leakage"], 8.7, 3.2, WARNING),
        ("5. RF Regressor Fit", ["350 Decision Trees", "Max Depth: 10", "5-Fold Cross Validation", "Mean MAE: 0.472 | R²: 0.998"], 11.4, 3.2, SUCCESS)
    ]

    for title, items, x, y, color in blocks:
        box = FancyBboxPatch((x, y), 2.2, 3.5, boxstyle="round,pad=0.08,rounding_size=0.12",
                             ec=color, fc="#f8fafc", lw=1.5)
        ax.add_patch(box)
        header = FancyBboxPatch((x, y + 2.9), 2.2, 0.6, boxstyle="round,pad=0.04,rounding_size=0.08",
                                ec=color, fc=color, lw=1)
        ax.add_patch(header)
        ax.text(x + 1.1, y + 3.2, title, ha="center", va="center", fontsize=8.8, fontweight="bold", color="#ffffff")
        for i, item in enumerate(items):
            ax.text(x + 0.15, y + 2.4 - i * 0.55, f"• {item}", fontsize=7.4, color=TEXT_DARK)

    # Connecting arrows
    for i in range(4):
        x_from = 2.8 + i * 2.7
        x_to = 3.3 + i * 2.7
        ax.annotate("", xy=(x_to, 4.95), xytext=(x_from, 4.95),
                    arrowprops=dict(arrowstyle="->", lw=2, color=SECONDARY))

    # Bottom Export Box
    export_box = FancyBboxPatch((3.0, 0.8), 8.0, 1.6, boxstyle="round,pad=0.08,rounding_size=0.12",
                                ec=PURPLE, fc="#faf5ff", lw=1.5)
    ax.add_patch(export_box)
    ax.text(7.0, 2.05, "PERSISTED MODEL ARTIFACTS & EVALUATION METRICS", ha="center", fontsize=9.5, fontweight="bold", color=PURPLE)
    ax.text(7.0, 1.6, "interview_scoring_model.pkl (Random Forest Regressor)  |  scoring_model_metrics.json (Hyperparams & CV)",
            ha="center", fontsize=8.2, color=TEXT_DARK)
    ax.text(7.0, 1.2, "academic_scaler.pkl (Fitted StandardScaler)  |  Held-out Test Performance: MAE=0.4798, RMSE=0.6596, R²=0.9985",
            ha="center", fontsize=8.2, color=TEXT_MUTED)

    ax.annotate("", xy=(7.0, 2.4), xytext=(12.5, 3.2),
                arrowprops=dict(arrowstyle="->", lw=1.5, color=PURPLE, connectionstyle="arc3,rad=-0.2"))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "03_ml_training_pipeline.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {out_path}")


# ------------------------------------------------------------------------------
# 4. ML PREDICTION & SCORING WORKFLOW DIAGRAM
# ------------------------------------------------------------------------------
def generate_prediction_workflow():
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(6.5, 7.6, "REAL-TIME ML INFERENCE & MULTI-CRITERIA SCORING WORKFLOW", 
            ha="center", va="center", fontsize=14, fontweight="bold", color=PRIMARY)
    ax.text(6.5, 7.25, "Mathematical Evaluation: Speech -> Embeddings -> 6-Dimensional Feature Vector -> Regressor -> Calibrated Output",
            ha="center", va="center", fontsize=9, color=TEXT_MUTED)

    stages = [
        ("1. Input Intake", "Candidate Audio / Text\n+ Expected Question Context", 0.6, 4.4, PRIMARY),
        ("2. Speech Transcription", "Faster-Whisper (Float32)\nRaw Candidate Transcript", 3.1, 4.4, SECONDARY),
        ("3. Embedding Generator", "SentenceTransformer MiniLM\n384-d Cosine Similarity", 5.6, 4.4, ACCENT),
        ("4. Feature Extraction", "Vector [Sem, QLen, ALen,\nCov, Align, Depth]", 8.1, 4.4, WARNING),
        ("5. Random Forest Model", "350 Trees Regressor\nMulti-Rubric Approximation", 10.6, 4.4, SUCCESS),
    ]

    for title, desc, x, y, color in stages:
        box = FancyBboxPatch((x, y), 2.0, 2.2, boxstyle="round,pad=0.08,rounding_size=0.12",
                             ec=color, fc="#f8fafc", lw=1.5)
        ax.add_patch(box)
        header = FancyBboxPatch((x, y + 1.6), 2.0, 0.6, boxstyle="round,pad=0.04,rounding_size=0.08",
                                ec=color, fc=color, lw=1)
        ax.add_patch(header)
        ax.text(x + 1.0, y + 1.9, title, ha="center", va="center", fontsize=8, fontweight="bold", color="#ffffff")
        ax.text(x + 1.0, y + 0.8, desc, ha="center", va="center", fontsize=7.4, color=TEXT_DARK)

    for i in range(4):
        ax.annotate("", xy=(3.1 + i * 2.5, 5.5), xytext=(2.6 + i * 2.5, 5.5),
                    arrowprops=dict(arrowstyle="->", lw=2, color=SECONDARY))

    # Output post-processing box
    post_box = FancyBboxPatch((2.0, 1.0), 9.0, 2.4, boxstyle="round,pad=0.08,rounding_size=0.12",
                              ec=PURPLE, fc="#faf5ff", lw=1.5)
    ax.add_patch(post_box)
    ax.text(6.5, 3.0, "POST-PROCESSING, GUARDRAILS & CALIBRATED FEEDBACK", ha="center", fontsize=9.8, fontweight="bold", color=PURPLE)
    
    post_items = [
        ("Zero-Floor Non-Answer Guard", "If candidate answer < 3 words, or contains 'I don't know' / gibberish, score is clamped to 0."),
        ("Score Normalization & Clipping", "Raw model output clamped to [0.0, 100.0] range, preventing anomalous boundary predictions."),
        ("Multi-Dimensional Score Breakdown", "Generates granular feedback: Technical Score (0-100), Speaking Pacing (WPM), Visual Attention (%)."),
        ("Actionable Improvement Recommendations", "Produces natural language recommendations highlighting missing concepts and speech filler counts.")
    ]
    for idx, (head, text) in enumerate(post_items):
        ax.text(2.3, 2.55 - idx * 0.45, f"• {head}: ", fontsize=7.8, fontweight="bold", color=PRIMARY)
        ax.text(4.8, 2.55 - idx * 0.45, text, fontsize=7.6, color=TEXT_DARK)

    ax.annotate("", xy=(11.0, 3.4), xytext=(11.6, 4.4),
                arrowprops=dict(arrowstyle="->", lw=2, color=PURPLE, connectionstyle="arc3,rad=0.3"))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "04_ml_prediction_workflow.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {out_path}")


# ------------------------------------------------------------------------------
# 5. USE CASE DIAGRAM (USER & ADMIN)
# ------------------------------------------------------------------------------
def generate_use_case_diagram():
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(6.5, 7.6, "UML USE CASE DIAGRAM: USER & ADMINISTRATOR ROLES", 
            ha="center", va="center", fontsize=14, fontweight="bold", color=PRIMARY)
    ax.text(6.5, 7.25, "Separation of Candidate Interview Practice vs Platform Administrative Governance",
            ha="center", va="center", fontsize=9, color=TEXT_MUTED)

    # Candidate Actor (Left)
    ax.text(1.2, 5.0, "CANDIDATE\n(USER)", ha="center", va="center", fontsize=10, fontweight="bold", color=PRIMARY)
    circle_user = plt.Circle((1.2, 5.8), 0.35, color=PRIMARY, fill=False, lw=2)
    ax.add_patch(circle_user)
    # Actor stick figure
    ax.plot([1.2, 1.2], [4.65, 5.45], color=PRIMARY, lw=2)
    ax.plot([0.8, 1.6], [5.1, 5.1], color=PRIMARY, lw=2)
    ax.plot([1.2, 0.8], [4.65, 4.2], color=PRIMARY, lw=2)
    ax.plot([1.2, 1.6], [4.65, 4.2], color=PRIMARY, lw=2)

    # Administrator Actor (Right)
    ax.text(11.8, 5.0, "ADMINISTRATOR\n(STAFF)", ha="center", va="center", fontsize=10, fontweight="bold", color=WARNING)
    circle_admin = plt.Circle((11.8, 5.8), 0.35, color=WARNING, fill=False, lw=2)
    ax.add_patch(circle_admin)
    ax.plot([11.8, 11.8], [4.65, 5.45], color=WARNING, lw=2)
    ax.plot([11.4, 12.2], [5.1, 5.1], color=WARNING, lw=2)
    ax.plot([11.8, 11.4], [4.65, 4.2], color=WARNING, lw=2)
    ax.plot([11.8, 12.2], [4.65, 4.2], color=WARNING, lw=2)

    # System Boundary Box (Center)
    sys_box = FancyBboxPatch((2.6, 0.8), 7.8, 6.2, boxstyle="round,pad=0.1,rounding_size=0.15",
                             ec=BORDER_COLOR, fc="#ffffff", lw=1.5, ls="--")
    ax.add_patch(sys_box)
    ax.text(6.5, 6.7, "AI Interview Analyzer System Boundary", ha="center", fontsize=10.5, fontweight="bold", color=PRIMARY)

    user_use_cases = [
        ("Register & Authenticate Account", 5.9),
        ("Upload Resume & Extract Keywords", 5.1),
        ("Configure Practice Interview Session", 4.3),
        ("Perform Real-Time Audio/Video Practice", 3.5),
        ("View Performance Analytics & Report", 2.7),
        ("Download Comprehensive PDF Report", 1.9),
    ]

    admin_use_cases = [
        ("Manage Curated Question Bank", 5.5),
        ("Monitor System Audit Logs & Health", 4.5),
        ("View Platform Analytics & Cohorts", 3.5),
        ("Manage User Roles & Permissions", 2.5),
    ]

    # Draw User Use Cases (Left side of boundary)
    for title, y in user_use_cases:
        ellipse = FancyBboxPatch((3.0, y - 0.28), 3.4, 0.56, boxstyle="round,pad=0.05,rounding_size=0.25",
                                 ec=SECONDARY, fc="#f0f9ff", lw=1.2)
        ax.add_patch(ellipse)
        ax.text(4.7, y, title, ha="center", va="center", fontsize=7.8, fontweight="bold", color=TEXT_DARK)
        ax.plot([1.6, 3.0], [5.0, y], color=SECONDARY, lw=1.2, ls=":")

    # Draw Admin Use Cases (Right side of boundary)
    for title, y in admin_use_cases:
        ellipse = FancyBboxPatch((6.8, y - 0.28), 3.3, 0.56, boxstyle="round,pad=0.05,rounding_size=0.25",
                                 ec=WARNING, fc="#fffbeb", lw=1.2)
        ax.add_patch(ellipse)
        ax.text(8.45, y, title, ha="center", va="center", fontsize=7.8, fontweight="bold", color=TEXT_DARK)
        ax.plot([11.4, 10.1], [5.0, y], color=WARNING, lw=1.2, ls=":")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "05_use_case_diagram.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {out_path}")


# ------------------------------------------------------------------------------
# 6. DATABASE ENTITY-RELATIONSHIP (ER) DIAGRAM
# ------------------------------------------------------------------------------
def generate_database_er_diagram():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")

    ax.text(7, 8.6, "DATABASE ENTITY-RELATIONSHIP (ER) SCHEMA DIAGRAM", 
            ha="center", va="center", fontsize=14, fontweight="bold", color=PRIMARY)
    ax.text(7, 8.25, "Relational SQLite / SQLAlchemy Schema with Primary Keys (PK), Foreign Keys (FK), and Cardinalities",
            ha="center", va="center", fontsize=9, color=TEXT_MUTED)

    tables = [
        # (title, attributes, x, y, width, height, color)
        ("users", [
            ("id", "INTEGER (PK)"),
            ("email", "VARCHAR(255) UNIQUE"),
            ("hashed_password", "VARCHAR(255)"),
            ("full_name", "VARCHAR(100)"),
            ("role", "VARCHAR(20) [user/admin]"),
            ("created_at", "DATETIME")
        ], 0.6, 4.6, 3.4, 3.2, PRIMARY),

        ("interviews", [
            ("id", "INTEGER (PK)"),
            ("user_id", "INTEGER (FK -> users.id)"),
            ("job_role", "VARCHAR(100)"),
            ("experience_level", "VARCHAR(50)"),
            ("overall_score", "FLOAT"),
            ("status", "VARCHAR(30)"),
            ("created_at", "DATETIME")
        ], 5.3, 4.6, 3.5, 3.2, SECONDARY),

        ("questions", [
            ("id", "INTEGER (PK)"),
            ("text", "TEXT"),
            ("category", "VARCHAR(50)"),
            ("difficulty", "VARCHAR(30)"),
            ("expected_answer", "TEXT"),
            ("keywords", "TEXT (JSON)")
        ], 10.0, 4.6, 3.4, 3.2, ACCENT),

        ("user_answers", [
            ("id", "INTEGER (PK)"),
            ("interview_id", "INTEGER (FK -> interviews.id)"),
            ("question_id", "INTEGER (FK -> questions.id)"),
            ("candidate_text", "TEXT"),
            ("audio_path", "VARCHAR(255)"),
            ("technical_score", "FLOAT"),
            ("wpm_pacing", "FLOAT"),
            ("gaze_confidence", "FLOAT")
        ], 5.3, 0.7, 3.5, 3.4, WARNING),

        ("feedback", [
            ("id", "INTEGER (PK)"),
            ("interview_id", "INTEGER (FK -> interviews.id)"),
            ("overall_score", "FLOAT"),
            ("strengths", "TEXT"),
            ("weaknesses", "TEXT"),
            ("recommendations", "TEXT")
        ], 0.6, 0.7, 3.4, 3.0, SUCCESS),

        ("system_logs", [
            ("id", "INTEGER (PK)"),
            ("user_id", "INTEGER (FK -> users.id)"),
            ("event_type", "VARCHAR(50)"),
            ("endpoint", "VARCHAR(100)"),
            ("status_code", "INTEGER"),
            ("timestamp", "DATETIME")
        ], 10.0, 0.7, 3.4, 3.0, PURPLE),
    ]

    for title, fields, x, y, w, h, color in tables:
        # Outer box
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.1",
                             ec=color, fc="#ffffff", lw=1.5)
        ax.add_patch(box)
        # Header
        header = FancyBboxPatch((x, y + h - 0.55), w, 0.55, boxstyle="round,pad=0.03,rounding_size=0.06",
                                ec=color, fc=color, lw=1)
        ax.add_patch(header)
        ax.text(x + w / 2, y + h - 0.28, f"TABLE: {title}", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#ffffff")
        # Fields
        for i, (field_name, field_type) in enumerate(fields):
            is_pk = "PK" in field_type
            is_fk = "FK" in field_type
            f_color = PRIMARY if is_pk else (WARNING if is_fk else TEXT_DARK)
            ax.text(x + 0.15, y + h - 0.95 - i * 0.38, field_name, fontsize=7.4, fontweight="bold" if is_pk else "normal", color=f_color)
            ax.text(x + w - 0.15, y + h - 0.95 - i * 0.38, field_type, ha="right", fontsize=7.0, color=TEXT_MUTED)

    # Relationships
    # users (1) -> (N) interviews
    ax.annotate("", xy=(5.3, 6.2), xytext=(4.0, 6.2),
                arrowprops=dict(arrowstyle="->", lw=2, color=SECONDARY))
    ax.text(4.2, 6.35, "1", fontsize=8, fontweight="bold", color=PRIMARY)
    ax.text(5.0, 6.35, "N", fontsize=8, fontweight="bold", color=SECONDARY)

    # interviews (1) -> (N) user_answers
    ax.annotate("", xy=(7.05, 4.1), xytext=(7.05, 4.6),
                arrowprops=dict(arrowstyle="->", lw=2, color=WARNING))
    ax.text(7.2, 4.4, "1 : N", fontsize=8, fontweight="bold", color=WARNING)

    # questions (1) -> (N) user_answers
    ax.annotate("", xy=(8.8, 3.0), xytext=(10.0, 5.0),
                arrowprops=dict(arrowstyle="->", lw=1.8, color=ACCENT, connectionstyle="arc3,rad=0.2"))
    ax.text(9.6, 4.3, "1 : N", fontsize=8, fontweight="bold", color=ACCENT)

    # interviews (1) -> (1) feedback
    ax.annotate("", xy=(4.0, 2.2), xytext=(5.3, 5.0),
                arrowprops=dict(arrowstyle="->", lw=1.8, color=SUCCESS, connectionstyle="arc3,rad=0.2"))
    ax.text(4.4, 3.4, "1 : 1", fontsize=8, fontweight="bold", color=SUCCESS)

    # users (1) -> (N) system_logs
    ax.annotate("", xy=(10.0, 2.0), xytext=(2.3, 4.6),
                arrowprops=dict(arrowstyle="->", lw=1.8, color=PURPLE, connectionstyle="arc3,rad=-0.15"))
    ax.text(5.8, 0.45, "users 1 : N system_logs", fontsize=8, fontweight="bold", color=PURPLE)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "06_database_er_diagram.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {out_path}")


# ------------------------------------------------------------------------------
# 7. SEQUENCE DIAGRAM (INTERVIEW SESSION LIFECYCLE)
# ------------------------------------------------------------------------------
def generate_sequence_diagram():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")

    ax.text(7, 8.6, "UML SEQUENCE DIAGRAM: INTERVIEW SESSION EXECUTION LIFECYCLE", 
            ha="center", va="center", fontsize=14, fontweight="bold", color=PRIMARY)
    ax.text(7, 8.25, "Synchronous & Asynchronous Message Exchange Across Candidate, Frontend, Gateway, ML, and Database",
            ha="center", va="center", fontsize=9, color=TEXT_MUTED)

    lifelines = [
        ("Candidate", 1.0, PRIMARY),
        ("Frontend UI", 3.0, SECONDARY),
        ("FastAPI Gateway", 5.2, ACCENT),
        ("Whisper Service", 7.4, WARNING),
        ("ML Scoring Engine", 9.6, SUCCESS),
        ("SQLite DB", 12.0, PURPLE)
    ]

    # Draw Lifeline Headers and Dashed Lines
    for name, x, color in lifelines:
        header = FancyBboxPatch((x - 0.8, 7.4), 1.6, 0.55, boxstyle="round,pad=0.04,rounding_size=0.08",
                                ec=color, fc=color, lw=1)
        ax.add_patch(header)
        ax.text(x, 7.68, name, ha="center", va="center", fontsize=8.2, fontweight="bold", color="#ffffff")
        ax.plot([x, x], [1.0, 7.4], color="#cbd5e1", lw=1.2, ls="--")

    # Sequence Messages
    messages = [
        # (from_x, to_x, y, label, is_return)
        (1.0, 3.0, 6.9, "1: Click 'Start Interview'", False),
        (3.0, 5.2, 6.5, "2: POST /api/interview/start (role, tech)", False),
        (5.2, 12.0, 6.1, "3: Query Question Bank for Role", False),
        (12.0, 5.2, 5.8, "4: Return Curated Question List", True),
        (5.2, 3.0, 5.5, "5: 200 OK + First Question Data", True),
        (3.0, 1.0, 5.2, "6: Display Question & Prompt Mic/Cam", True),
        (1.0, 3.0, 4.7, "7: Record Voice Answer (Audio Blob)", False),
        (3.0, 5.2, 4.3, "8: POST /api/interview/submit-answer", False),
        (5.2, 7.4, 3.9, "9: Dispatch Audio -> Faster-Whisper", False),
        (7.4, 5.2, 3.5, "10: Return Transcribed Text + WPM", True),
        (5.2, 9.6, 3.1, "11: Dispatch Text -> SentenceTransformer + RF", False),
        (9.6, 5.2, 2.7, "12: Return Technical Score (0-100) + Rubric", True),
        (5.2, 12.0, 2.3, "13: INSERT user_answers & update session", False),
        (5.2, 3.0, 1.9, "14: 200 OK + Score Feedback & Next Question", True),
        (3.0, 1.0, 1.5, "15: Render Immediate Score Badge & Advice", True)
    ]

    for fx, tx, y, label, is_ret in messages:
        color = SECONDARY if not is_ret else SUCCESS
        ls = "-" if not is_ret else "--"
        ax.annotate("", xy=(tx, y), xytext=(fx, y),
                    arrowprops=dict(arrowstyle="->", lw=1.4, color=color, ls=ls))
        mid_x = (fx + tx) / 2
        ax.text(mid_x, y + 0.12, label, ha="center", va="bottom", fontsize=7.2, fontweight="bold" if not is_ret else "normal", color=TEXT_DARK)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "07_sequence_diagram.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    print("Generating 7 System Architecture & Workflow Diagrams...")
    generate_system_architecture()
    generate_interview_workflow()
    generate_ml_training_pipeline()
    generate_prediction_workflow()
    generate_use_case_diagram()
    generate_database_er_diagram()
    generate_sequence_diagram()
    print("All 7 Diagrams Generated Successfully in docs/diagrams/!")

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class VisualAnalysisRequest(BaseModel):
    total_samples: int = Field(0, description="Total webcam frame samples collected during answer recording")
    face_detected_samples: int = Field(0, description="Samples where a candidate face was detected")
    face_missing_samples: int = Field(0, description="Samples where no candidate face was detected")
    looking_at_camera_samples: int = Field(0, description="Samples where candidate was facing the camera")
    looking_away_samples: int = Field(0, description="Samples where candidate was looking away or off-center")
    head_orientation_counts: Dict[str, int] = Field(
        default_factory=lambda: {"center": 0, "left": 0, "right": 0, "up": 0, "down": 0},
        description="Counts of head pose orientation samples"
    )
    expression_counts: Dict[str, int] = Field(
        default_factory=lambda: {"neutral": 0, "speaking": 0, "expressive": 0},
        description="Counts of facial movement/expression samples"
    )
    multiple_face_events: int = Field(0, description="Count of frames with multiple faces detected")


class VisualAnalysisResponse(BaseModel):
    status: str
    face_presence_pct: float
    camera_attention_pct: float
    looking_away_count: int
    primary_orientation: str
    head_pose_distribution: str
    expression_summary: str
    visual_attention_score: float
    message: str
    eye_contact_percentage: Optional[float] = None
    multiple_faces_detected: Optional[bool] = False


def process_visual_observations(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes aggregated MediaPipe landmark visual observations collected during live interview answer recording.
    Returns deterministic visual attention & head pose metrics without random/fake values.
    """
    total = int(data.get("total_samples", 0))
    detected = int(data.get("face_detected_samples", 0))
    missing = int(data.get("face_missing_samples", 0))
    at_camera = int(data.get("looking_at_camera_samples", 0))
    looking_away = int(data.get("looking_away_samples", 0))
    orientations = data.get("head_orientation_counts", {"center": 0, "left": 0, "right": 0, "up": 0, "down": 0})
    expressions = data.get("expression_counts", {"neutral": 0, "speaking": 0, "expressive": 0})

    # Insufficient visual data check (< 3 samples or camera off)
    if total < 3 or (detected == 0 and missing == 0):
        return {
            "status": "insufficient_visual_data",
            "face_presence_pct": 0.0,
            "camera_attention_pct": 0.0,
            "looking_away_count": 0,
            "primary_orientation": "N/A",
            "head_pose_distribution": "Insufficient visual data",
            "expression_summary": "Expression analysis unavailable",
            "visual_attention_score": 0.0,
            "message": "Insufficient webcam sampling data recorded during answer."
        }

    # 1. Face Presence Percentage
    face_presence_pct = round((detected / float(total)) * 100.0, 1)

    # 2. Camera Attention Percentage
    camera_attention_pct = round((at_camera / float(total)) * 100.0, 1) if detected > 0 else 0.0

    # 3. Dominant Head Orientation & Pose Distribution
    primary_orientation = "Center"
    max_count = 0
    pose_parts = []

    for pose, count in orientations.items():
        if count > max_count:
            max_count = count
            primary_orientation = pose.capitalize()
        if count > 0:
            pct = round((count / float(total)) * 100.0, 1)
            pose_parts.append(f"{pose.capitalize()} ({pct}%)")

    head_pose_distribution = ", ".join(pose_parts) if pose_parts else "Center (100%)"

    # 4. Expression / Facial Movement Summary
    expr_parts = []
    total_expr = sum(expressions.values())
    if total_expr > 0:
        for expr, count in expressions.items():
            if count > 0:
                pct = round((count / float(total_expr)) * 100.0, 1)
                label = "Neutral / Attentive" if expr == "neutral" else ("Speaking / Active" if expr == "speaking" else "Expressive")
                expr_parts.append(f"{label} ({pct}%)")
        expression_summary = ", ".join(expr_parts)
    else:
        expression_summary = "Expression analysis unavailable"

    # 5. Visual Attention Score (0-100)
    attention_score = round(max(0.0, min(100.0, (0.6 * face_presence_pct) + (0.4 * camera_attention_pct))), 1)

    multiple_faces = int(data.get("multiple_face_events", 0)) > 0

    return {
        "status": "success",
        "face_presence_pct": face_presence_pct,
        "camera_attention_pct": camera_attention_pct,
        "eye_contact_percentage": camera_attention_pct,
        "multiple_faces_detected": multiple_faces,
        "looking_away_count": looking_away,
        "primary_orientation": primary_orientation,
        "head_pose_distribution": head_pose_distribution,
        "expression_summary": expression_summary,
        "visual_attention_score": attention_score,
        "message": "MediaPipe visual observations analyzed successfully."
    }

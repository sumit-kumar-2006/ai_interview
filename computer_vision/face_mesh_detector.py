"""
================================================================================
MEDIAPIPE FACE MESH & IRIS GAZE DETECTOR
================================================================================
Production-grade 3D Facial Landmark, Head Pose, and Eye-Contact Tracking.
Powered by Google MediaPipe Tasks API (478 3D landmarks + 52 Blendshapes).
================================================================================
"""

import os
import cv2
import numpy as np
from typing import Dict, Any, Optional, List, Tuple

import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models",
    "face_landmarker.task"
)

_DETECTOR_INSTANCE = None


class MediaPipeFaceMeshDetector:
    """
    High-accuracy 3D FaceMesh, Head Pose, and Iris Eye-Contact Tracker.
    """
    def __init__(self, model_path: str = MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"MediaPipe face landmarker model not found at: {model_path}")
        
        options = vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
            num_faces=2,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)

    def process_frame(self, frame_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Analyzes a single BGR image/frame.
        Returns face presence, 3D head pose, iris gaze direction, and expression state.
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return {"face_detected": False, "multiple_faces": False}

        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection = self.landmarker.detect(mp_image)

        if not detection.face_landmarks or len(detection.face_landmarks) == 0:
            return {
                "face_detected": False,
                "multiple_faces": False,
                "eye_contact": False,
                "head_pose": "UNKNOWN",
                "expression": "neutral",
                "gaze_direction": "Unknown"
            }

        num_faces = len(detection.face_landmarks)
        multiple_faces = num_faces > 1
        landmarks = detection.face_landmarks[0]

        # 1. Head Pose Estimation (Yaw & Pitch)
        nose = landmarks[1]
        chin = landmarks[152]
        left_eye = landmarks[33]
        right_eye = landmarks[263]

        mid_eye_x = (left_eye.x + right_eye.x) / 2.0
        mid_eye_y = (left_eye.y + right_eye.y) / 2.0

        dist_left = np.hypot(nose.x - left_eye.x, nose.y - left_eye.y)
        dist_right = np.hypot(nose.x - right_eye.x, nose.y - right_eye.y)
        yaw_ratio = (dist_left / dist_right) if dist_right > 0 else 1.0

        upper_vert = abs(nose.y - mid_eye_y)
        lower_vert = abs(chin.y - nose.y)
        pitch_ratio = (upper_vert / lower_vert) if lower_vert > 0 else 0.5

        head_pose = "CENTER"
        if yaw_ratio < 0.65:
            head_pose = "LEFT"
        elif yaw_ratio > 1.55:
            head_pose = "RIGHT"
        elif pitch_ratio < 0.35:
            head_pose = "UP"
        elif pitch_ratio > 0.85:
            head_pose = "DOWN"

        # 2. Iris Gaze & Eye Contact Tracking (Landmarks 468 = Left Iris, 473 = Right Iris)
        eye_contact = False
        gaze_direction = "Center"
        
        # Check blendshapes if available
        if detection.face_blendshapes and len(detection.face_blendshapes) > 0:
            shapes = {cat.category_name: cat.score for cat in detection.face_blendshapes[0]}
            look_down = max(shapes.get("eyeLookDownLeft", 0.0), shapes.get("eyeLookDownRight", 0.0))
            look_out_left = shapes.get("eyeLookOutLeft", 0.0)
            look_out_right = shapes.get("eyeLookOutRight", 0.0)
            look_up = max(shapes.get("eyeLookUpLeft", 0.0), shapes.get("eyeLookUpRight", 0.0))
            blink = min(shapes.get("eyeBlinkLeft", 0.0), shapes.get("eyeBlinkRight", 0.0))

            if look_down > 0.45:
                gaze_direction = "Down"
            elif look_out_left > 0.40:
                gaze_direction = "Left"
            elif look_out_right > 0.40:
                gaze_direction = "Right"
            elif look_up > 0.40:
                gaze_direction = "Up"
            else:
                gaze_direction = "Center"

            # Eye contact requires looking toward camera while head is oriented center
            is_gaze_center = (gaze_direction == "Center") or (blink > 0.6)  # Don't penalize normal blinks
            eye_contact = (head_pose == "CENTER") and is_gaze_center
        else:
            # Fallback to iris coordinate geometry
            if len(landmarks) >= 474:
                left_iris = landmarks[468]
                right_iris = landmarks[473]
                left_eye_w = abs(landmarks[133].x - landmarks[33].x)
                right_eye_w = abs(landmarks[263].x - landmarks[362].x)
                
                left_ratio = (left_iris.x - min(landmarks[33].x, landmarks[133].x)) / max(0.001, left_eye_w)
                right_ratio = (right_iris.x - min(landmarks[362].x, landmarks[263].x)) / max(0.001, right_eye_w)
                avg_iris_x = (left_ratio + right_ratio) / 2.0
                
                is_gaze_center = (0.38 <= avg_iris_x <= 0.62)
                eye_contact = (head_pose == "CENTER") and is_gaze_center
                gaze_direction = "Center" if is_gaze_center else ("Left" if avg_iris_x < 0.38 else "Right")
            else:
                eye_contact = (head_pose == "CENTER")

        # 3. Facial Expression & Mouth Activity
        top_lip = landmarks[13]
        bottom_lip = landmarks[14]
        mouth_l = landmarks[61]
        mouth_r = landmarks[291]

        mouth_h = np.hypot(top_lip.x - bottom_lip.x, top_lip.y - bottom_lip.y)
        mouth_w = np.hypot(mouth_l.x - mouth_r.x, mouth_l.y - mouth_r.y)
        mar = (mouth_h / mouth_w) if mouth_w > 0 else 0.0

        expression = "neutral"
        if mar > 0.40:
            expression = "speaking"
        elif mar > 0.25:
            expression = "expressive"

        return {
            "face_detected": True,
            "multiple_faces": multiple_faces,
            "eye_contact": bool(eye_contact),
            "head_pose": head_pose,
            "gaze_direction": gaze_direction,
            "expression": expression
        }

    def analyze_video(self, video_path: str, sample_fps: int = 2) -> Dict[str, Any]:
        """
        Samples an entire video file at sample_fps intervals and aggregates visual metrics.
        Returns a dictionary compatible with VisualAnalysisRequest.
        """
        if not os.path.exists(video_path):
            return {"status": "error", "message": f"Video file not found: {video_path}"}

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"status": "error", "message": "Failed to open video file"}

        video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_interval = max(1, int(video_fps / sample_fps))

        total_samples = 0
        face_detected = 0
        face_missing = 0
        looking_at_camera = 0
        looking_away = 0
        multiple_face_events = 0

        head_counts = {"center": 0, "left": 0, "right": 0, "up": 0, "down": 0}
        expr_counts = {"neutral": 0, "speaking": 0, "expressive": 0}

        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                total_samples += 1
                result = self.process_frame(frame)

                if result.get("face_detected"):
                    face_detected += 1
                    if result.get("multiple_faces"):
                        multiple_face_events += 1

                    pose_key = result.get("head_pose", "CENTER").lower()
                    head_counts[pose_key] = head_counts.get(pose_key, 0) + 1

                    expr_key = result.get("expression", "neutral").lower()
                    expr_counts[expr_key] = expr_counts.get(expr_key, 0) + 1

                    if result.get("eye_contact"):
                        looking_at_camera += 1
                    else:
                        looking_away += 1
                else:
                    face_missing += 1

            frame_idx += 1

        cap.release()

        return {
            "total_samples": total_samples,
            "face_detected_samples": face_detected,
            "face_missing_samples": face_missing,
            "looking_at_camera_samples": looking_at_camera,
            "looking_away_samples": looking_away,
            "head_orientation_counts": head_counts,
            "expression_counts": expr_counts,
            "multiple_face_events": multiple_face_events
        }


def get_face_mesh_detector() -> MediaPipeFaceMeshDetector:
    """Singleton getter for MediaPipe FaceMesh detector."""
    global _DETECTOR_INSTANCE
    if _DETECTOR_INSTANCE is None:
        _DETECTOR_INSTANCE = MediaPipeFaceMeshDetector()
    return _DETECTOR_INSTANCE


# Convenience alias for backwards compatibility
FaceMeshDetector = MediaPipeFaceMeshDetector



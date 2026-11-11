import sys
import os
sys.path.insert(0, os.path.abspath("."))

from computer_vision.visual_analyzer import process_visual_observations
from backend.app.speech_analyzer import SpeechAnalyzer

def test_cv():
    print("Testing Computer Vision Visual Analyzer...")
    # Normal attentive session
    attentive_data = {
        "total_samples": 100,
        "face_detected_samples": 98,
        "face_missing_samples": 2,
        "looking_at_camera_samples": 92,
        "looking_away_samples": 8,
        "head_orientation_counts": {"center": 88, "left": 6, "right": 4, "up": 1, "down": 1},
        "expression_counts": {"neutral": 60, "speaking": 40, "expressive": 0}
    }
    res = process_visual_observations(attentive_data)
    assert res["status"] == "success"
    assert res["face_presence_pct"] == 98.0
    assert res["camera_attention_pct"] == 92.0
    assert res["primary_orientation"] == "Center"
    assert res["visual_attention_score"] >= 90.0
    print("  -> [PASS] Attentive session:", res["visual_attention_score"], "%")

    # Inattentive session
    inattentive_data = {
        "total_samples": 100,
        "face_detected_samples": 50,
        "face_missing_samples": 50,
        "looking_at_camera_samples": 20,
        "looking_away_samples": 80,
        "head_orientation_counts": {"center": 10, "left": 50, "right": 30, "up": 10, "down": 0}
    }
    res_inattentive = process_visual_observations(inattentive_data)
    assert res_inattentive["visual_attention_score"] < 50.0
    print("  -> [PASS] Inattentive session correctly scored lower:", res_inattentive["visual_attention_score"], "%")

    # Insufficient samples check
    insufficient = {"total_samples": 1}
    res_insuf = process_visual_observations(insufficient)
    assert res_insuf["status"] == "insufficient_visual_data"
    print("  -> [PASS] Insufficient visual samples cleanly flagged.")

def test_speech():
    print("\nTesting Speech Fluency & Prosody Analyzer...")
    sa = SpeechAnalyzer()

    # Fluent answer
    whisper_fluent = {
        "text": "The Global Interpreter Lock prevents concurrent thread execution in Python.",
        "segments": [
            {"start": 0.0, "end": 4.5, "text": "The Global Interpreter Lock prevents concurrent thread execution in Python."}
        ]
    }
    res_fluent = sa.analyze(whisper_fluent)
    assert res_fluent["word_count"] == 10
    assert res_fluent["filler_word_count"] == 0
    assert res_fluent["fluency_score"] >= 80.0
    print("  -> [PASS] Fluent speech detected: Fluency =", res_fluent["fluency_score"])

    # Filler word heavy answer
    whisper_fillers = {
        "text": "Um like actually you know Python has uh like basically a lock.",
        "segments": [
            {"start": 0.0, "end": 6.0, "text": "Um like actually you know Python has uh like basically a lock."}
        ]
    }
    res_fillers = sa.analyze(whisper_fillers)
    assert res_fillers["filler_word_count"] >= 5
    assert res_fillers["filler_words"]["um"] >= 1
    assert res_fillers["filler_words"]["like"] >= 2
    assert res_fillers["fluency_score"] < res_fluent["fluency_score"]
    print("  -> [PASS] Filler words accurately detected:", res_fillers["filler_words"], "Fluency =", res_fillers["fluency_score"])

    # Silent / empty answer
    res_empty = sa.analyze({"text": ""})
    assert res_empty["status"] == "no_speech_detected"
    assert res_empty["fluency_score"] == 0.0
    print("  -> [PASS] Silent answer detected with 0 score.")

if __name__ == "__main__":
    test_cv()
    test_speech()
    print("\n==================================================")
    print("PHASE 5 CV & SPEECH ENGINE VERIFICATION: 100% PASS")
    print("==================================================")

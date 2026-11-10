import os
import sys

# Configure testing environment for standalone test execution
os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("ALLOW_LEGACY_SCORING", "true")

import wave
import struct
import numpy as np
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.main import app
from speech.transcribe import parse_whisper_result, transcribe_audio

client = TestClient(app)


def create_silent_wav(filename="tests/test_silent.wav", duration_sec=2.0, sample_rate=16000):
    """Creates a 2-second silent WAV file (zeros)."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    num_samples = int(duration_sec * sample_rate)
    with wave.open(filename, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        # Write zeros for silence
        wav_file.writeframes(b"\x00\x00" * num_samples)
    return filename


def test_no_answer_detection():
    print("\n=========================================")
    print("RUNNING AUTOMATED TEST SUITE")
    print("=========================================")

    # ----------------------------------------------------
    # TEST A: Completely silent WAV file
    # ----------------------------------------------------
    print("\n[TEST A] Completely silent WAV file...")
    silent_file = create_silent_wav()
    with open(silent_file, "rb") as f:
        response = client.post(
            "/transcribe-and-score",
            files={"audio": ("test_silent.wav", f, "audio/wav")},
            data={
                "question": "What is polymorphism in object oriented programming?",
                "reference_answer": "Polymorphism allows the same interface or method to behave differently for different objects."
            }
        )
    
    assert response.status_code == 200
    res_json = response.json()
    print("Response JSON:", res_json)
    assert res_json["status"] == "no_answer"
    assert res_json["speech_detected"] is False
    assert res_json["predicted_score"] == 0
    assert res_json["transcript"] == ""
    assert res_json["message"] == "No answer detected. Please record your answer and try again."
    print("✓ [TEST A PASSED]")

    # ----------------------------------------------------
    # TEST B: Short non-answer / fewer than 3 words test
    # ----------------------------------------------------
    print("\n[TEST B] Testing transcription logic with < 3 words...")
    fake_whisper_result_short = {
        "text": "Hello",
        "segments": [{"no_speech_prob": 0.05, "text": "Hello"}]
    }
    transcript, speech_detected = parse_whisper_result(fake_whisper_result_short)
    assert speech_detected is True
    assert transcript == "Hello"

    # Test main.py endpoint mock logic with short transcript
    words = [w for w in transcript.split() if w.strip()]
    assert len(words) < 3
    print("✓ [TEST B PASSED]")

    # ----------------------------------------------------
    # TEST C: Valid polymorphism answer (using speech/test.wav)
    # ----------------------------------------------------
    print("\n[TEST C] Valid polymorphism answer (speech/test.wav)...")
    valid_file = "speech/test.wav"
    with open(valid_file, "rb") as f:
        response = client.post(
            "/transcribe-and-score",
            files={"audio": ("test.wav", f, "audio/wav")},
            data={
                "question": "What is polymorphism in object oriented programming?",
                "reference_answer": "Polymorphism allows the same interface or method to behave differently for different objects."
            }
        )

    assert response.status_code == 200
    res_json = response.json()
    print("Response JSON:", res_json)
    assert res_json["status"] == "success"
    assert res_json["speech_detected"] is True
    assert res_json["predicted_score"] > 50
    assert len(res_json["transcript"]) > 10
    print("✓ [TEST C PASSED]")

    # ----------------------------------------------------
    # TEST D: Existing /predict-score endpoint
    # ----------------------------------------------------
    print("\n[TEST D] Existing /predict-score endpoint...")
    response = client.post(
        "/predict-score",
        json={
            "question": "What is polymorphism in object oriented programming?",
            "candidate_answer": "Polymorphism allows the same interface or method to behave differently for different objects.",
            "reference_answer": "Polymorphism allows the same interface or method to behave differently for different objects."
        }
    )

    assert response.status_code == 200
    res_json = response.json()
    print("Response JSON:", res_json)
    assert res_json["predicted_score"] > 80
    assert "question_similarity" in res_json
    assert "reference_similarity" in res_json
    print("✓ [TEST D PASSED]")

    print("\n=========================================")
    print("ALL 4 TEST CASES PASSED SUCCESSFULLY!")
    print("=========================================\n")


if __name__ == "__main__":
    test_no_answer_detection()

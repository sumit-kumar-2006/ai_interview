import os
import sys
import torch
from faster_whisper import WhisperModel

MODEL_NAME = "base"
_whisper_model = None


class FasterWhisperWrapper:
    """
    High-performance wrapper around faster-whisper CTranslate2 model.
    Automatically detects CUDA (GPU) vs CPU, selects float16 / int8 quantization,
    and returns dict output matching standard Whisper schema:
    {
        "text": str,
        "segments": [{"start": float, "end": float, "text": str, "no_speech_prob": float}],
        "language": str,
        "duration": float
    }
    """
    def __init__(self, model_size: str = MODEL_NAME):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        print(f"Loading faster-whisper ({model_size}) on {self.device} with {self.compute_type} quantization...")
        self.model = WhisperModel(model_size, device=self.device, compute_type=self.compute_type)
        print("faster-whisper model loaded.")

    def transcribe(self, audio_path: str, beam_size: int = 1, **kwargs):
        """
        Transcribes the given audio file and returns a Whisper-compatible dictionary.
        """
        segments, info = self.model.transcribe(audio_path, beam_size=beam_size, **kwargs)
        seg_list = []
        text_parts = []
        for s in segments:
            clean_text = s.text.strip()
            if clean_text:
                text_parts.append(clean_text)
            seg_list.append({
                "start": float(s.start),
                "end": float(s.end),
                "text": clean_text,
                "no_speech_prob": float(s.no_speech_prob)
            })

        full_text = " ".join(text_parts).strip()
        return {
            "text": full_text,
            "segments": seg_list,
            "language": getattr(info, "language", "en"),
            "duration": getattr(info, "duration", 0.0)
        }


def get_whisper_model():
    """Singleton getter for faster-whisper model."""
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = FasterWhisperWrapper(MODEL_NAME)
    return _whisper_model


def parse_whisper_result(result):
    """
    Inspects Whisper's transcription result and segment metrics (no_speech_prob)
    to detect silent, hallucinated, or empty recordings.

    Returns:
        tuple: (transcript: str, speech_detected: bool)
    """
    raw_text = result.get("text", "").strip() if result else ""
    segments = result.get("segments", []) if result else []

    if not raw_text or not segments:
        return "", False

    # Inspect no_speech_prob for segments
    no_speech_probs = [seg.get("no_speech_prob", 0.0) for seg in segments]
    avg_no_speech = sum(no_speech_probs) / len(no_speech_probs) if no_speech_probs else 0.0

    # High average no_speech_prob indicates silence or non-speech audio
    if avg_no_speech > 0.5:
        return "", False

    # Check single segment high no_speech_prob (> 0.6)
    if len(segments) == 1 and segments[0].get("no_speech_prob", 0.0) > 0.6:
        return "", False

    # Check if there are meaningful words
    words = [w for w in raw_text.split() if w.strip()]
    if len(words) == 0:
        return "", False

    return raw_text, True


def transcribe_audio(audio_path, whisper_model=None):
    m = whisper_model if whisper_model is not None else get_whisper_model()
    result = m.transcribe(audio_path)
    return parse_whisper_result(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("python speech/transcribe.py <audio_file>")
        sys.exit(1)

    audio_path = sys.argv[1]

    print("\n========================================")
    print("       FASTER-WHISPER SPEECH TO TEXT")
    print("========================================")
    print("Audio:", audio_path)
    print("\nTranscribing...")

    transcript, speech_detected = transcribe_audio(audio_path)

    print("\n========================================")
    print("TRANSCRIPT")
    print("========================================")
    print("Speech Detected:", speech_detected)
    print("Text:", transcript)
    print("========================================")

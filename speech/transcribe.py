import sys
import whisper


MODEL_NAME = "base"
_whisper_model = None


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        print("Loading Whisper model...")
        _whisper_model = whisper.load_model(MODEL_NAME)
        print("Whisper model loaded.")
    return _whisper_model


model = None


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
    print("       SPEECH TO TEXT")
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

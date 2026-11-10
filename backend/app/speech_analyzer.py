import re
import wave
from typing import Dict, Any, List, Optional


class SpeechAnalyzer:
    """
    Analyzes spoken audio transcripts and timing information from Whisper AI.
    Calculates duration, word count, WPM, filler word breakdown, long pauses,
    speaking fluency, conciseness, and communication score.
    """

    FILLER_PATTERNS = {
        "um": r"\bum\b",
        "uh": r"\buh\b",
        "like": r"\blike\b",
        "you know": r"\byou\s+know\b",
        "basically": r"\bbasically\b",
        "actually": r"\bactually\b"
    }

    def analyze(self, whisper_result: Dict[str, Any], audio_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyzes Whisper result dict and optional audio file path.
        """
        text = whisper_result.get("text", "").strip() if whisper_result else ""
        segments = whisper_result.get("segments", []) if whisper_result else []

        # Handle empty/no speech transcript
        if not text or len(text.split()) == 0:
            return {
                "duration_seconds": 0.0,
                "word_count": 0,
                "words_per_minute": 0.0,
                "filler_word_count": 0,
                "filler_words": {k: 0 for k in self.FILLER_PATTERNS.keys()},
                "long_pauses_count": 0,
                "fluency_score": 0.0,
                "conciseness_score": 0.0,
                "communication_score": 0.0,
                "status": "no_speech_detected",
                "message": "No speech detected in audio recording."
            }

        # 1. Calculate Speaking Duration
        duration_seconds = None

        if segments and len(segments) > 0:
            start_t = float(segments[0].get("start", 0.0))
            end_t = float(segments[-1].get("end", 0.0))
            if end_t > start_t:
                duration_seconds = round(end_t - start_t, 2)

        if (duration_seconds is None or duration_seconds <= 0) and audio_path:
            try:
                if audio_path.lower().endswith(".wav"):
                    with wave.open(audio_path, "rb") as wf:
                        frames = wf.getnframes()
                        rate = wf.getframerate()
                        duration_seconds = round(frames / float(rate), 2)
            except Exception:
                pass

        # 2. Word Count
        words = [w.strip() for w in re.split(r'\s+', text) if w.strip()]
        word_count = len(words)

        # Handle insufficient speech data (< 3 words)
        if word_count < 3:
            return {
                "duration_seconds": duration_seconds,
                "word_count": word_count,
                "words_per_minute": round((word_count / duration_seconds) * 60, 2) if duration_seconds and duration_seconds > 0 else None,
                "filler_word_count": 0,
                "filler_words": {k: 0 for k in self.FILLER_PATTERNS.keys()},
                "long_pauses_count": 0,
                "fluency_score": 20.0,
                "conciseness_score": 20.0,
                "communication_score": 20.0,
                "status": "insufficient_speech_data",
                "message": "Answer too short for reliable speech & fluency analysis."
            }

        # 3. Words Per Minute (WPM)
        if duration_seconds and duration_seconds > 0:
            wpm = round((word_count / duration_seconds) * 60, 2)
        else:
            wpm = None

        # 4. Filler Word Detection
        filler_counts: Dict[str, int] = {}
        total_fillers = 0

        for key, pattern in self.FILLER_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            count = len(matches)
            filler_counts[key] = count
            total_fillers += count

        # 5. Long Pauses (gap >= 1.5s between consecutive segments)
        long_pauses_count = 0
        if segments and len(segments) > 1:
            for i in range(len(segments) - 1):
                curr_end = float(segments[i].get("end", 0.0))
                next_start = float(segments[i+1].get("start", 0.0))
                if next_start - curr_end >= 1.5:
                    long_pauses_count += 1
        elif not segments:
            long_pauses_count = None

        # 6. Fluency Score (0-100)
        if wpm is not None:
            if 110 <= wpm <= 165:
                base_fluency = 95.0
            elif 80 <= wpm < 110:
                base_fluency = 80.0 + ((wpm - 80) / 30.0) * 15.0
            elif 165 < wpm <= 200:
                base_fluency = 95.0 - ((wpm - 165) / 35.0) * 20.0
            else:
                base_fluency = 60.0
        else:
            base_fluency = 80.0

        # Penalties for fillers and long pauses
        filler_penalty = min(30.0, total_fillers * 4.0)
        pause_penalty = min(20.0, (long_pauses_count or 0) * 5.0)

        fluency_score = round(max(10.0, min(100.0, base_fluency - filler_penalty - pause_penalty)), 2)

        # 7. Conciseness Score (0-100)
        filler_ratio = total_fillers / max(1, word_count)
        conciseness_base = 100.0 - (filler_ratio * 250.0)
        
        if word_count > 250:
            conciseness_base -= min(20.0, (word_count - 250) * 0.1)

        conciseness_score = round(max(10.0, min(100.0, conciseness_base)), 2)

        # 8. Communication Score
        communication_score = round(max(0.0, min(100.0, (0.5 * fluency_score) + (0.5 * conciseness_score))), 2)

        return {
            "duration_seconds": duration_seconds,
            "word_count": word_count,
            "words_per_minute": wpm,
            "filler_word_count": total_fillers,
            "filler_words": filler_counts,
            "long_pauses_count": long_pauses_count,
            "fluency_score": fluency_score,
            "conciseness_score": conciseness_score,
            "communication_score": communication_score,
            "status": "success",
            "message": "Speech analysis completed successfully."
        }

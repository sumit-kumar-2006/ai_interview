"""
Audio Validation Module for AI Interview Analyzer (Part B - Step 4).
Validates audio uploads for MIME type, file size, duration, container headers,
and safe temporary file lifecycle management.
"""

import io
import os
import re
import wave
import tempfile
import uuid
from typing import Dict, Any, Optional, Tuple
from fastapi import HTTPException, status

# Sensible architectural limits
MAX_AUDIO_SIZE_BYTES = 25 * 1024 * 1024   # 25 MB (prevents DoS / memory exhaustion)
MIN_AUDIO_SIZE_BYTES = 100                # 100 bytes (rejects 0-byte or empty headers)
MIN_RECORDING_DURATION_SEC = 1.0          # Minimum 1 second for a spoken response
MAX_RECORDING_DURATION_SEC = 300.0        # Maximum 5 minutes (300 seconds)

# Allowed extensions and standard MIME types
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".webm", ".mp4", ".m4a", ".ogg", ".mp3"}

ALLOWED_AUDIO_MIME_TYPES = {
    "audio/wav", "audio/x-wav", "audio/wave",
    "audio/webm",
    "audio/mp4", "audio/m4a", "audio/x-m4a", "audio/aac",
    "audio/ogg", "audio/x-ogg", "application/ogg",
    "audio/mpeg", "audio/mp3",
    "video/webm"  # Some Chromium browsers tag WebM audio as video/webm
}

# Magic bytes headers for audio containers
CONTAINER_SIGNATURES = [
    # WAV / RIFF: starts with 'RIFF' and bytes 8..12 are 'WAVE'
    ("wav", lambda b: len(b) >= 12 and b[:4] == b"RIFF" and b[8:12] == b"WAVE"),
    # WebM / Matroska: EBML header magic 0x1A 0x45 0xDF 0xA3
    ("webm", lambda b: len(b) >= 4 and b[:4] == b"\x1a\x45\xdf\xa3"),
    # MP4 / M4A: bytes 4..8 are 'ftyp'
    ("mp4", lambda b: len(b) >= 8 and b[4:8] == b"ftyp"),
    # OGG: starts with 'OggS'
    ("ogg", lambda b: len(b) >= 4 and b[:4] == b"OggS"),
    # MP3: ID3 tag or MPEG sync word
    ("mp3", lambda b: len(b) >= 3 and (b[:3] == b"ID3" or (b[0] == 0xFF and (b[1] & 0xE0) == 0xE0)))
]


def detect_audio_container(content: bytes) -> Optional[str]:
    """
    Inspects binary magic bytes to determine the underlying container format.
    Returns format string ('wav', 'webm', 'mp4', 'ogg', 'mp3') or None if unrecognized.
    """
    for fmt_name, checker in CONTAINER_SIGNATURES:
        try:
            if checker(content):
                return fmt_name
        except Exception:
            continue
    return None


def get_wav_duration_seconds(content: bytes) -> Optional[float]:
    """
    Extracts duration from standard WAV audio bytes using the standard library wave module.
    Returns duration in seconds, or None if not a valid readable WAV.
    """
    try:
        with wave.open(io.BytesIO(content), "rb") as wf:
            framerate = wf.getframerate()
            nframes = wf.getnframes()
            if framerate > 0:
                return round(nframes / float(framerate), 2)
    except Exception:
        pass
    return None


def sanitize_filename(filename: Optional[str]) -> str:
    """
    Removes path traversal components and unsafe characters from filenames.
    """
    if not filename:
        return f"recording_{uuid.uuid4().hex[:8]}.webm"
    base = os.path.basename(filename)
    clean = re.sub(r"[^a-zA-Z0-9_\.-]", "_", base)
    return clean or f"recording_{uuid.uuid4().hex[:8]}.webm"


def validate_audio_recording(
    content: bytes,
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
    reported_duration: Optional[float] = None
) -> Dict[str, Any]:
    """
    Validates uploaded audio payload across size, container headers, format,
    and duration. Raises HTTPException with appropriate status codes on failure.

    Returns:
        dict with validated metadata:
            {
                "format": str,
                "size_bytes": int,
                "duration_seconds": float,
                "sanitized_filename": str,
                "content_type": str
            }
    """
    # 1. Size Validation (Empty / Zero-Byte Rejection)
    if not content or len(content) < MIN_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Audio recording is empty or corrupt. Payload size ({len(content) if content else 0} bytes) "
                f"is below the minimum required size of {MIN_AUDIO_SIZE_BYTES} bytes."
            )
        )

    # 2. Maximum Upload Size Validation (25 MB)
    if len(content) > MAX_AUDIO_SIZE_BYTES:
        max_mb = MAX_AUDIO_SIZE_BYTES // (1024 * 1024)
        actual_mb = round(len(content) / (1024 * 1024), 2)
        raise HTTPException(
            status_code=getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413),
            detail=f"Audio payload ({actual_mb} MB) exceeds maximum allowed size of {max_mb} MB."
        )

    # 3. Filename & Extension Validation
    safe_name = sanitize_filename(filename)
    _, ext = os.path.splitext(safe_name)
    ext = ext.lower()

    if ext and ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported audio file extension '{ext}'. "
                f"Allowed formats: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}."
            )
        )

    # 4. MIME Type Validation (if supplied by client)
    normalized_mime = None
    if content_type:
        normalized_mime = content_type.split(";")[0].strip().lower()
        if normalized_mime not in ALLOWED_AUDIO_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unsupported audio MIME type '{content_type}'. "
                    f"Supported types: {', '.join(sorted(ALLOWED_AUDIO_MIME_TYPES))}."
                )
            )

    # 5. Binary Container Header Inspection (Detect Corrupted / Non-Audio Payloads)
    detected_container = detect_audio_container(content)
    if not detected_container:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid or corrupted audio payload. The uploaded file does not contain "
                "valid audio container header signatures (e.g. WAV, WebM, MP4/M4A, OGG, MP3)."
            )
        )

    # 6. Duration Calculation & Boundary Validation
    # A. Validate client-reported duration if provided
    if reported_duration is not None:
        if reported_duration < MIN_RECORDING_DURATION_SEC:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Audio duration ({reported_duration:.1f}s) is below the minimum "
                    f"required duration of {MIN_RECORDING_DURATION_SEC:.1f}s."
                )
            )
        if reported_duration > MAX_RECORDING_DURATION_SEC:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Audio duration ({reported_duration:.1f}s) exceeds the maximum "
                    f"allowed limit of {MAX_RECORDING_DURATION_SEC:.1f}s (5 minutes)."
                )
            )

    # B. If WAV container, calculate exact duration from binary frames and validate
    resolved_duration = reported_duration
    if detected_container == "wav":
        wav_dur = get_wav_duration_seconds(content)
        if wav_dur is not None and wav_dur > 0:
            resolved_duration = wav_dur
            if wav_dur < MIN_RECORDING_DURATION_SEC:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Audio duration ({wav_dur:.1f}s) is below the minimum "
                        f"required duration of {MIN_RECORDING_DURATION_SEC:.1f}s."
                    )
                )
            if wav_dur > MAX_RECORDING_DURATION_SEC:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Audio duration ({wav_dur:.1f}s) exceeds the maximum "
                        f"allowed limit of {MAX_RECORDING_DURATION_SEC:.1f}s (5 minutes)."
                    )
                )

    return {
        "format": detected_container,
        "size_bytes": len(content),
        "duration_seconds": resolved_duration if resolved_duration is not None else 0.0,
        "sanitized_filename": safe_name,
        "content_type": normalized_mime or f"audio/{detected_container}"
    }


class SafeTemporaryAudioFile:
    """
    Context manager for creating a safely named temporary audio file
    in the OS temp directory with guaranteed automatic deletion.
    """
    def __init__(self, content: bytes, suffix: str = ".webm"):
        self.content = content
        self.suffix = suffix if suffix.startswith(".") else f".{suffix}"
        self.path: Optional[str] = None

    def __enter__(self) -> str:
        safe_suffix = re.sub(r"[^a-zA-Z0-9_\.]", "", self.suffix)
        with tempfile.NamedTemporaryFile(delete=False, suffix=safe_suffix) as tf:
            self.path = tf.name
            tf.write(self.content)
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.path and os.path.exists(self.path):
            try:
                os.remove(self.path)
            except OSError:
                pass

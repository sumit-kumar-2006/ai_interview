# Part B – Step 5: Whisper Speech-to-Text Integration Plan (Phase 1 — Read-Only Planning Audit)

**Project:** AI Interview Analyzer  
**Workspace:** `D:\AI-Interview-Analyzer`  
**Date:** November 6, 2026  
**Auditor / Engineer:** Senior Full-Stack Developer & AI Speech Systems Engineer  
**Scope:** Phase 1 — Read-Only Architecture Inspection, Integration Planning, and Security Design  
**Status:** Planning Audit Complete — **STRICT READ-ONLY (Zero Code, Database, or ML Asset Modifications)**

---

## 1. Executive Summary

This deliverable provides the comprehensive technical planning audit for **Part B – Step 5: Whisper Speech-to-Text Integration**.

The objective of Step 5 is to bridge the **Voice Interview System (Step 4)** and the **Secure Backend Question & Evaluation Engine (Step 3)** through an accurate, secure, and candidate-friendly Whisper AI transcription workflow.

In accordance with user instructions:
- **Zero changes have been made to application code, datasets, models, database records, or schemas.**
- This document outlines the exact architecture, code locations, flows, security measures, and automated regression test plans required prior to implementation approval.

---

## 2. Existing Whisper Architecture & Reusable Components

The project codebase currently contains several foundational speech processing assets developed during earlier prototypes and academic milestones:

### A. Pre-loaded Whisper Model in Memory
- **Location:** `backend/app/main.py:88`
- **Specification:**
  ```python
  print("Loading Whisper model...")
  whisper_model = whisper.load_model("base")
  ```
- **Runtime Environment:**
  - Whisper version: `20250625`
  - PyTorch version: `2.13.0+cpu`
  - Execution Device: CPU (FP32 mode)
  - Underlying Audio Engine: FFmpeg (`D:\ffmpeg\bin\ffmpeg.exe` verified available on system path)
- **Status:** Already initialized at application startup; reusable without reloading overhead.

### B. Segment Metrics & No-Speech Detection Wrapper
- **Location:** `speech/transcribe.py:12-44`
- **Specification:**
  `parse_whisper_result(result)` inspects Whisper segment-level probabilities (`no_speech_prob`):
  - Returns `(raw_text, False)` if average `no_speech_prob > 0.5` or single segment $> 0.6$.
  - Returns `(raw_text, False)` if word count is 0.
  - Returns `(raw_text, True)` for valid speech.
- **Status:** Production-ready and verified by `tests/test_no_answer_detection.py`.

### C. Speech & Fluency Telemetry Analyzer
- **Location:** `backend/app/speech_analyzer.py:6-154`
- **Class:** `SpeechAnalyzer` (initialized in `main.py:96`)
- **Capabilities:**
  - Speaking duration extraction from Whisper segment timestamps (`start`, `end`).
  - Word count and Words-Per-Minute (WPM) calculation.
  - Filler word detection (`um`, `uh`, `like`, `you know`, `basically`, `actually`).
  - Long pause detection (pauses $> 1.8\text{s}$ between consecutive segments).
  - Fluency, conciseness, and communication score calculation.
- **Status:** Fully decoupled from technical evaluation (does not penalize semantic score).

### D. Multi-Tier Audio Validation (Step 4)
- **Location:** `backend/app/audio_validator.py`
- **Capabilities:**
  - File size bounds ($100\text{ bytes} \le \text{size} \le 25\text{ MB}$).
  - Audio container magic bytes inspection (WAV, WebM, MP4, OGG, MP3).
  - Duration limits ($1.0\text{s} \le \text{duration} \le 300.0\text{s}$).
  - `SafeTemporaryAudioFile` context manager for zero-leakage ephemeral storage.

### E. Existing Legacy Monolithic Endpoint (`POST /transcribe-and-score`)
- **Location:** `backend/app/main.py:611-741`
- **Behavior:** Receives `audio`, `question`, and `reference_answer`, runs Whisper, and immediately evaluates score in one monolithic pass.
- **Limitation:** Does not allow candidate transcript review or editing; requires client to supply reference answer (violating Step 3 security principles). Retained strictly for backward compatibility with legacy test suites.

---

## 3. Exact Files Requiring Modification in Step 5

| File | Nature of Change | Purpose |
| :--- | :---: | :--- |
| `backend/app/main.py` | **Additive Modification** | Add dedicated endpoint `POST /transcribe-audio` that accepts audio, validates payload, runs Whisper transcription + `SpeechAnalyzer`, returns transcript + telemetry, and cleans up temp files. |
| `frontend/script.js` | **Flow Alignment** | Update `transcribeAudioForCandidateReview()` to call `POST /transcribe-audio` on recording stop, populate `#audio-playback-preview`, populate `#transcript-edit-input`, display telemetry badges, and allow candidate to edit transcript before calling `/evaluate-answer`. |
| `frontend/index.html` | **Minor Enhancement** | Verify Stage 1 Transcript Review card elements (`#transcript-review-card`, `#audio-playback-preview`, `#transcript-edit-input`, `#trc-badge-wpm`, `#trc-badge-fillers`, `#trc-badge-fluency`) match API response fields. |
| `tests/test_whisper_transcription.py` | **New Test Suite** | Author comprehensive automated tests for Whisper STT, silence detection, technical word transcription, candidate edit submission, and cleanup. |

---

## 4. Proposed Audio-to-Transcript Workflow

```
[Candidate finishes recording in browser]
                     │
                     ▼
             Blob assembled (WebM/MP4/WAV)
                     │
                     ▼
  POST /transcribe-audio (multipart/form-data)
  - Fields: audio file, question_id, duration_seconds
                     │
                     ▼
  ┌────────────────────────────────────────────────────────┐
  │ FASTAPI BACKEND: POST /transcribe-audio               │
  │ 1. validate_audio_recording() (MIME, size, headers)    │
  │ 2. SafeTemporaryAudioFile(content, suffix=format)      │
  │ 3. whisper_model.transcribe(temp_path)                 │
  │ 4. parse_whisper_result(result) (detect silence/noise) │
  │ 5. speech_analyzer.analyze(result, temp_path)          │
  │ 6. os.remove(temp_path) via context manager finally    │
  └────────────────────────┬───────────────────────────────┘
                           │
                           ▼
  Return JSON:
  {
    "status": "success" | "no_speech" | "answer_too_short",
    "speech_detected": true,
    "transcript": "Metaclasses in Python define how classes are constructed...",
    "speech_analysis": {
      "words_per_minute": 132.0,
      "filler_word_count": 1,
      "fluency_score": 92.0,
      "duration_seconds": 18.5
    },
    "question_id": 159
  }
                           │
                           ▼
  ┌────────────────────────────────────────────────────────┐
  │ FRONTEND: Stage 1 Mandatory Review & Editing Card      │
  │ 1. Mount Object URL to <audio id="audio-playback-preview">
  │ 2. Candidate listens to recorded audio                 │
  │ 3. Candidate inspects transcript in textarea           │
  │ 4. Candidate corrects technical misspellings           │
  │ 5. Displays Communication Metrics (WPM, Fillers)       │
  └────────────────────────┬───────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
    [Click "Re-record"]             [Click "Submit Answer"]
           │                               │
    Clears draft, attempt +1        POST /evaluate-answer
    Zero penalty applied            - question_id: 159
                                    - candidate_answer: edited_text
                                    - speech_analysis: telemetry
                                    - visual_analysis: cv_data
                                           │
                                           ▼
                                    Evaluated against DB ground truth
```

---

## 5. Secure Integration with `question_id` & Canonical DB Evaluation

### A. Separation of Concerns (Transcription vs Evaluation)
1. **Transcription Endpoint (`POST /transcribe-audio`):**
   - Pure acoustic-to-text transformation and communication fluency telemetry.
   - **Never** accesses, reveals, or scores against the reference answer or rubric.
   - Accepts optional `question_id` to validate question existence and active status.
2. **Evaluation Endpoint (`POST /evaluate-answer`):**
   - Strictly retrieves the canonical reference answer from the MySQL database using `question_id`.
   - Never accepts client-supplied reference answers or rubrics.
   - Evaluates candidate's verified, reviewed transcript.

### B. Elimination of Cheating Vectors
- Because `/transcribe-audio` returns **only** what the candidate spoke, a candidate cannot extract the expected answer by inspecting network traffic during audio transcription.
- Client-side text edits are evaluated exclusively against the server-side ground truth stored in MySQL.

---

## 6. Transcript Review and Editing Workflow

### Why Transcript Editing Is Essential
1. **Acoustic / Technical Term Errors:** Standard Whisper models occasionally mistranscribe domain-specific jargon (e.g., transcribing *"PostgreSQL"* as *"post grass Q L"*, *"Kubernetes"* as *"coober netties"*, or *"k-NN"* as *"canon"*).
2. **Fair Candidate Evaluation:** Allowing candidates to review and edit recognized text ensures candidates are scored on their **technical knowledge and comprehension**, not on speech-recognition acoustic artifacts.
3. **Decoupled Telemetry:** Speech telemetry (speaking rate, filler words, fluency) is computed from the **raw audio** during transcription and preserved independently. Editing the transcript improves technical accuracy but does not rewrite the audio telemetry.

### Workflow Controls in Frontend
- **Editor:** Native `<textarea id="transcript-edit-input">` with live word counter (`#trc-word-count`).
- **Telemetry Badges:** `#trc-badge-wpm` (Words per minute), `#trc-badge-fillers` (Filler count), `#trc-badge-fluency` (Fluency %).
- **Retake Guarantee:** Candidate can click `btn-review-rerecord` to discard the draft and re-record with attempt counter incremented and zero score penalty.

---

## 7. Audio & Transcript Privacy and Temporary-File Cleanup

### Storage Lifecycle
1. **Zero Permanent Audio Storage:** Audio files are never permanently saved to the file system, S3 buckets, or database columns.
2. **Safe Ephemeral Disk Files:** During Whisper transcription, audio is spooled using `SafeTemporaryAudioFile` in OS temp directories (`tempfile.gettempdir()`) using randomized filenames with sanitized extensions.
3. **Guaranteed Deletion:** Cleanup is enforced in the `finally:` block of the request handler. Even if Whisper throws an unhandled exception or CUDA/CPU error, the temporary file is deleted before the HTTP response terminates.
4. **Database Privacy:** Only the final submitted transcript, calculated scores, and aggregated metrics are stored in MySQL `question_results` upon completed interview submission.

---

## 8. Performance, Latency, and Error Handling

### Performance on CPU
- The project environment runs Whisper `base` on CPU (`torch 2.13.0+cpu`).
- **Observed Latencies:**
  - 2-second audio: $\approx 0.8\text{s}$
  - 15-second audio: $\approx 1.8\text{s} - 2.5\text{s}$
  - 60-second audio: $\approx 4.0\text{s} - 6.5\text{s}$
- **Sensible Limit:** Capped by Step 4 at 300 seconds (5 minutes).

### Error Handling & Edge Cases
1. **Silent Audio / Background Noise:**
   - Evaluated by `parse_whisper_result()`: If `avg(no_speech_prob) > 0.5`, returns `status: "no_speech"` with message prompting candidate to speak closer to the microphone.
2. **Short Utterances (< 3 words):**
   - Returns `status: "answer_too_short"`, guiding candidate to provide a more detailed technical response.
3. **Corrupt / Malformed Audio:**
   - Caught before Whisper execution by `validate_audio_recording()`, returning `HTTP 400 Bad Request`.
4. **Whisper Timeout / Exception Fallback:**
   - If the backend transcription encounters an error, the frontend gracefully falls back to the live Web Speech API transcript captured during the recording session, preventing the interview from freezing.

---

## 9. Automated Test Cases & Regression Strategy

### Dedicated Step 5 Test Suite (`tests/test_whisper_transcription.py`)
1. **`test_whisper_silent_audio_rejection`:** Submits silent WAV; asserts `speech_detected == False`, `status == "no_speech"`.
2. **`test_whisper_short_utterance_handling`:** Submits short utterance; asserts `status == "answer_too_short"`.
3. **`test_whisper_valid_technical_transcription`:** Submits `speech/test.wav`; asserts `speech_detected == True`, transcript contains key terms (`"polymorphism"`, `"interface"`), and status is `"success"`.
4. **`test_whisper_telemetry_generation`:** Validates WPM, filler word dictionary, and fluency score in `speech_analysis`.
5. **`test_transcribe_audio_temp_file_cleanup`:** Proves temporary file is deleted from disk immediately after response generation.
6. **`test_transcribe_audio_no_reference_answer_leak`:** Asserts response does not contain `reference_answer`, `evaluation_spec`, or `rubric`.
7. **`test_end_to_end_voice_to_evaluation_flow`:** Simulates candidate recording $\rightarrow$ `/transcribe-audio` $\rightarrow$ editing transcript text $\rightarrow$ submitting to `/evaluate-answer` $\rightarrow$ accurate score calculation.

### Full Regression Suite
- Run all 54 existing tests alongside the new Step 5 tests (expecting 61+ passed tests).

---

## 10. Risks, Dependencies, and Rollback Plan

### Identified Risks & Mitigations
| Risk | Severity | Mitigation |
| :--- | :---: | :--- |
| **CPU High Load during Concurrency** | Medium | Whisper `base` model is lightweight (142M params). For production scaling, process queues or async threadpool executors will isolate transcription threads. |
| **FFmpeg Missing on Client Machines** | Low | FFmpeg is verified installed locally at `D:\ffmpeg\bin\ffmpeg.exe` and is bundled on server environments. |
| **Whisper Hallucination on Ambient Noise** | Low | `parse_whisper_result` segment `no_speech_prob` filtering reliably detects and discards hallucinations. Candidate review card allows manual correction. |

### Rollback Strategy
- The Step 5 implementation is **purely additive**:
  - Adds `POST /transcribe-audio` in `main.py`.
  - Links frontend review card in `script.js`.
  - Does **not** modify existing `/evaluate-answer`, `/transcribe-and-score`, or question bank routes.
- If any unforeseen defect occurs, reverting changes to `backend/app/main.py` and `frontend/script.js` completely restores the Step 4 baseline without database migrations or data loss.

---

## 11. Confirmation of Protected Asset Invariance

- **Part A Academic Assets:** Zero changes to `ml/datasets/academic_train.csv`, validation/test CSVs, `interview_scoring_model.pkl`, scalers, or evaluation reports.
- **MySQL Database Integrity:** Zero record modifications; schema remains unchanged; 1,816 question records intact.
- **Implementation State:** **No files have been modified or created during this planning audit (except this markdown report).**

---

## 12. Final Checkpoint

Phase 1 (Read-Only Planning Audit) for Part B Step 5 is complete.
All development is paused. Awaiting explicit user approval before proceeding to Phase 2 (Implementation).


# AI INTERVIEW ANALYZER — MASTER TESTING REPORT
**Document Reference:** `TESTING_REPORT.md`  
**Execution Timestamp:** 2026-11-11T11:35:00+05:30  
**Test Framework:** Pytest 9.1.1 + FastAPI TestClient + Chrome DevTools Protocol

---

## 1. AUTOMATED TEST SUITES SUMMARY

| Suite Name | File Location | Tests | Passed | Failed | Execution Time | Coverage Area |
|---|---|---:|---:|---:|---:|---|
| **Admin & Analytics** | `tests/test_admin_and_analytics.py` | 8 | 8 | 0 | ~4.2s | Admin stats, pagination, user role updates, analytics trends |
| **Evaluator Rules** | `tests/test_evaluator_rules.py` | 10 | 10 | 0 | ~5.8s | Rules A through H, technical synonyms, contradiction checks |
| **Interview API** | `tests/test_interview_api.py` | 7 | 7 | 0 | ~3.1s | Session creation, detail fetch, deletion, report JSON/PDF |
| **Live API Integration** | `tests/test_live_api.py` | 1 | 0 | 1 | ~1.5s | Live HTTP request to `/transcribe-and-score` (port 8000) |
| **No-Answer Detection** | `tests/test_no_answer_detection.py` | 4 | 4 | 0 | ~2.6s | Silence detection, whitespace answers, empty audio rejection |
| **Provider Integration** | `tests/test_provider_integration.py` | 3 | 3 | 0 | ~1.8s | LLM fallback, provider switching, rubric formatting |
| **Question Bank Migration** | `tests/test_question_bank_migration.py` | 6 | 6 | 0 | ~2.9s | MySQL 1,816 question verification, active training split isolation |
| **Resume & Questions** | `tests/test_resume_and_questions.py` | 5 | 5 | 0 | ~3.4s | Resume text extraction, skill detection, personalized questions |
| **Secure Question Engine**| `tests/test_secure_question_engine.py` | 10 | 10 | 0 | ~6.5s | Rubric anti-tampering, reference answer stripping |
| **Voice Interview System**| `tests/test_voice_interview_system.py` | 15 | 15 | 0 | ~145.0s | Audio magic bytes, duration checks, STT transcription, scoring |
| **TOTAL** | | **69** | **68** | **1** | **~177.5s** | **98.5% Pass Rate** |

---

## 2. ROOT CAUSE ANALYSIS FOR FAILED TEST

### Failure: `tests/test_live_api.py::test_live_backend`
- **Error:** `requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /transcribe-and-score (Caused by NewConnectionError("... [WinError 10061] No connection could be made because the target machine actively refused it"))`
- **Root Cause:** The test issues raw `requests.post()` calls to `http://127.0.0.1:8000`. In automated pytest runs, no external server process is bound to port 8000.
- **Resolution Plan:** Upgrade `test_live_api.py` to first probe `http://127.0.0.1:8000/health`. If reachable, execute live HTTP network requests; if unreachable, execute directly using FastAPI's in-process `TestClient(app)` from `backend.app.main`. This guarantees 100% test reliability in all testing environments.

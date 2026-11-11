# AI INTERVIEW ANALYZER — MASTER BUG TRACKER
**Document Reference:** `BUG_TRACKER.md`  
**Last Updated:** 2026-11-11T11:35:00+05:30  
**Strict Classification:** Critical | High | Medium | Low  

---

## ACTIVE ISSUE REGISTRY

| ID | Module | Problem | Severity | Root Cause | Required Fix | Status |
|---|---|---|---|---|---|---|
| **BUG-001** | Testing / QA | `tests/test_live_api.py` raises `ConnectionRefusedError` during isolated `pytest` runs | High | Test file assumes an external Uvicorn server is pre-launched on port 8000 using raw `requests` library | Add dynamic fallback to FastAPI `TestClient(app)` if live HTTP socket `127.0.0.1:8000` is unreachable, enabling both live integration and isolated pytest execution | **Resolved** |
| **BUG-002** | Frontend / UX | `#btn-pause-recording` in `index.html` has no explicit JS handler | Low | Button was rendered with class `hidden` as a placeholder for pause functionality | Removed orphaned hidden placeholder button from markup; all 115 interactive buttons verified with active handlers | **Resolved** |
| **BUG-003** | Audio / STT | Monolithic vs Decoupled STT review workflow integration | Medium | `/transcribe-and-score` combines Whisper transcription with scoring; modern UI has review card requiring editable transcript prior to grading | Verify and polish decoupled `/transcribe-audio` flow in `frontend/script.js` with transcript editing and re-recording options | In Progress |
| **BUG-004** | Device Check | Dynamic innerHTML buttons (`#btn-quick-switch-audio`, `#btn-quick-retry-cam`) on camera denial | Low | Buttons are injected via template string in `script.js` when camera permission is denied | Ensure event listeners are attached reliably whenever the HTML is dynamically re-rendered | Verified / Monitored |
| **BUG-005** | UI / Responsive | Ensure complete visual fidelity and zero horizontal scrolling across 320px-1920px viewports | Medium | `.profile-ambient-glow` decorative radial blur extended beyond container width on 768px tablet, combined with class name mismatch (`profile-analytics-wrap` vs `wrapper`) | Supported both class names, added `overflow-x: clip` to `.profile-analytics-wrap`, `.profile-analytics-wrapper`, and `#view-profile`; verified zero overflow across all 64 view/viewport combinations | **Resolved** |

---

## RESOLUTION LOG

### BUG-001: Test Runner Network Isolation in `tests/test_live_api.py`
- **File:** `tests/test_live_api.py`
- **Root Cause:** Test used raw `requests.post()` targeting `127.0.0.1:8000`. In automated pytest runs without an external server, socket connection failed.
- **Solution:** Implemented `get_api_client()` that probes `http://127.0.0.1:8000/health`. If reachable, it uses live network `requests`; otherwise, it falls back to FastAPI's in-process `TestClient(app)`.
- **Verification:** Ran `pytest tests/test_live_api.py -v`. Executed in 52.68s with 100% pass rate.

### BUG-002: Dead Hidden Placeholder Button `#btn-pause-recording`
- **File:** `frontend/index.html` (line 1210)
- **Root Cause:** Orphaned empty `<button class="hidden" id="btn-pause-recording"></button>` inside recording controls with no JS event listener.
- **Solution:** Removed dead element.
- **Verification:** Executed `scripts/audit_all_buttons.py`. All 115 remaining buttons confirmed with active handlers (0 dead buttons).

### BUG-005: Horizontal Overflow on Tablet Profile View (768px)
- **File:** `frontend/style.css` (lines 10758-10766)
- **Root Cause:** Decorative `.profile-ambient-glow` radial gradient (width 650px, left 30%) overflowed beyond the 768px viewport width because `style.css` selector had `.profile-analytics-wrapper` while `index.html` used `<div class="profile-analytics-wrap">`.
- **Solution:** Added `.profile-analytics-wrap` selector with `position: relative; overflow-x: clip;` and `#view-profile { overflow-x: clip; }`.
- **Verification:** Verified docWidth dropped from 876px to 753px (under 768px window width). All 8 viewports tested across all 8 views with zero unwanted overflow.

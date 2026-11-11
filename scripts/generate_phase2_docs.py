import os

page_inventory_md = """# AI INTERVIEW ANALYZER — COMPLETE PAGE INVENTORY
**Document Reference:** `PAGE_INVENTORY.md`  
**Standard:** Enterprise Single-Page Application (SPA) Architectural Audit  
**Target System:** `d:\\AI-Interview-Analyzer`  
**Execution Timestamp:** 2026-11-11  

---

## 1. PAGE & VIEW INVENTORY MATRIX

| Page Name | Actual Route / Hash | Container ID | Controller File & Functions | Backend APIs Used | Database Dependencies | Auth Level | Reference Screenshot / Spec |
|---|---|---|---|---|---|---|---|
| **Landing Page** | `/?view=landing` or `/` or `#landing` | `#view-landing` | `frontend/script.js`<br>`initLandingPage()`, `initScrollObserver()` | `GET /interview/questions` (sample), `GET /health` | `questions` (public samples) | **Public** | `screenshots_audit/01_landing_fullpage_pixel_perfect.png`, `shot_landing_1440_final.png` |
| **Authentication Modal** | Pop-up overlay | `#auth-modal` | `frontend/script.js`<br>`showAuthModal()`, `handleAuthSubmit()` | `POST /auth/login`, `POST /auth/register` | `users`, `user_profiles` | **Public** | `screenshots_audit/09_auth_login_modal.png`, `10_auth_register_modal.png` |
| **Candidate Dashboard** | `/?view=dashboard` or `#dashboard` | `#view-dashboard` | `frontend/script.js`<br>`updateDashboardStats()`, `renderPerformanceChart()` | `GET /profile`, `GET /profile/analytics`, `GET /interviews` | `users`, `user_profiles`, `interviews`, `question_results` | **Authenticated Candidate** | `screenshots_audit/02_dashboard_fullpage.png`, `shot_dashboard_1440.png` |
| **Profile & Resume Analytics** | `/?view=profile` or `/?view=analytics` | `#view-profile` | `frontend/script.js`<br>`initProfileAnalyticsPage()`, `handleResumeUpload()` | `GET /profile`, `PUT /profile`, `POST /profile/resume`, `GET /profile/analytics`, `GET /profile/pdf` | `users`, `user_profiles`, `interviews` | **Authenticated Candidate** | `screenshots_audit/11_profile_modal.png`, `scripts/screenshots/profile_1440_desktop.png` |
| **Interview Setup Page** | `/?view=interview-setup` or `#interview-setup` | `#view-interview-setup` | `frontend/script.js`<br>`initInterviewSetupPage()`, `saveSetupConfiguration()` | `GET /profile`, `GET /interview/questions` | `user_profiles`, `questions` | **Authenticated Candidate** | `screenshots_audit/03_setup_view.png`, `scripts/screenshots/setup_page_1440.png` |
| **Device & Hardware Check** | `/?view=device-check` or `#device-check` | `#view-device-check` | `frontend/script.js`<br>`initDeviceCheckPage()`, `testMicrophone()`, `testWebcam()` | Client Web Audio API, MediaStream, MediaPipe FaceMesh | None (Client hardware) | **Authenticated Candidate** | `screenshots_audit/04_device_check_view.png`, `shot_device_check_1184.png` |
| **Live Practice Room** | `/?view=practice` or `#practice` | `#view-practice` | `frontend/script.js`<br>`startInterviewWorkflow()`, `recordAnswer()`, `evaluateCurrentAnswer()` | `POST /interview/audio/upload`, `POST /transcribe-audio`, `POST /evaluate-answer`, `POST /visual-analysis` | `questions`, `interviews`, `question_results` | **Authenticated Candidate** | `screenshots_audit/05_practice_room_100vh.png`, `scripts/screenshots/live_interview_1440.png` |
| **Comprehensive Assessment Report** | Inside `#view-practice` state `#completion-card` | `#completion-card` | `frontend/script.js`<br>`renderComprehensiveReport()`, `exportReportPDF()` | `GET /interviews/{id}/report`, `GET /interviews/{id}/report/pdf`, `POST /interviews/preview-pdf` | `interviews`, `question_results`, `users` | **Authenticated Candidate** | `screenshots_audit/07_report_fullpage.png` |
| **Interview History & Reports** | `/?view=history` or `#history` | `#view-history` | `frontend/script.js`<br>`loadInterviewHistory()`, `deleteInterviewSession()` | `GET /interviews`, `DELETE /interviews/{id}` | `interviews`, `question_results` | **Authenticated Candidate** | `screenshots_audit/08_history_view.png`, `screenshots_audit/history_desktop.png` |
| **Admin Management Console** | `/?view=admin` or `#admin` | `#view-admin` | `frontend/script.js`<br>`initAdminPage()`, `loadAdminStats()`, `manageUserRole()` | `GET /admin/stats`, `GET /admin/users`, `PUT /admin/users/{id}/role`, `DELETE /admin/users/{id}`, `GET /admin/interviews` | `users`, `user_profiles`, `interviews`, `question_results` | **Superadmin / Admin** | `screenshots_audit/admin_desktop.png` |
| **Quick Profile Modal** | Pop-up overlay | `#profile-modal` | `frontend/script.js`<br>`showProfileModal()`, `saveProfileModalData()` | `GET /profile`, `PUT /profile`, `POST /profile/resume` | `user_profiles`, `users` | **Authenticated Candidate** | `screenshots_audit/11_profile_modal.png` |
| **Privacy Policy Modal** | Pop-up overlay | `#privacy-modal` | `frontend/script.js`<br>`openModal('privacy-modal')` | Static client document | None | **Public** | Semantic Modal Spec |
| **Terms of Service Modal** | Pop-up overlay | `#terms-modal` | `frontend/script.js`<br>`openModal('terms-modal')` | Static client document | None | **Public** | Semantic Modal Spec |
| **Admin User Deletion Modal**| Pop-up overlay | `#admin-delete-modal`| `frontend/script.js`<br>`confirmDeleteAdminUser()` | `DELETE /admin/users/{id}` | `users`, `interviews` | **Superadmin** | Admin Action Spec |

---

## 2. DETAILED PAGE SPECIFICATIONS

### 1. Landing Page (`#view-landing`)
- **Template & CSS:** `frontend/index.html` (lines 48-720), `frontend/style.css` (lines 1-2800).
- **Entry Points:** Direct URL `/`, `/?view=landing`, Brand logo click (`#brand-logo`), Nav "Home" link (`#nav-home`), Footer "Home" link, Logout redirect.
- **Exit Points:** 
  - "Start Free Interview" CTA -> Opens `#view-interview-setup` (if auth) or `#auth-modal` (if guest).
  - "Get Started" / "Log In" Nav buttons -> Opens `#auth-modal`.
  - Feature cards / How It Works anchor scroll.
  - "Explore Analytics" CTA -> `#view-profile`.
- **Backend APIs:** Optional health probe `GET /health`.

### 2. Candidate Dashboard (`#view-dashboard`)
- **Template & CSS:** `frontend/index.html` (lines 722-1100), `frontend/style.css` (lines 2801-4400).
- **Entry Points:** Nav "Dashboard" button (`#nav-dash-btn`), Successful Login redirect, Setup Back button, Report "Back to Dashboard" button.
- **Exit Points:**
  - "Start New Practice" CTA (`#dash-start-interview-btn`) -> `#view-interview-setup`.
  - "Customize Profile" CTA (`#dash-customize-profile-btn`) -> `#view-profile`.
  - "View All History" link (`#dash-view-reports-btn`) -> `#view-history`.
  - Profile dropdown links -> `#view-profile`, `#view-admin`, Logout.
- **Backend APIs:** `GET /profile`, `GET /profile/analytics`, `GET /interviews`.

### 3. Profile & Resume Analytics (`#view-profile`)
- **Template & CSS:** `frontend/index.html` (lines 1850-2500), `frontend/style.css` (lines 6500-8200).
- **Entry Points:** Nav "Profile" button (`#nav-profile-btn`), Nav "Analytics" button (`#nav-analytics-btn`), Dashboard profile card, Avatar dropdown.
- **Exit Points:**
  - Back to Dashboard button -> `#view-dashboard`.
  - Start Interview button -> `#view-interview-setup`.
  - Export PDF Report button -> `GET /profile/pdf`.
- **Backend APIs:** `GET /profile`, `PUT /profile`, `POST /profile/resume`, `GET /profile/analytics`, `GET /profile/pdf`.

### 4. Interview Setup Page (`#view-interview-setup`)
- **Template & CSS:** `frontend/index.html` (lines 2502-3100), `frontend/style.css` (lines 8201-9500).
- **Entry Points:** Dashboard "Start Interview" CTA, Nav "Practice" button (when starting fresh), Landing page hero CTA.
- **Exit Points:**
  - "Back to Dashboard" button (`#btn-setup-back-dash`) -> `#view-dashboard`.
  - "Continue to Device Check" button (`#btn-setup-continue`) -> `#view-device-check`.
  - "Upload New Resume" dropzone -> Triggers resume re-parse API.
- **Backend APIs:** `GET /profile`, `POST /profile/resume`, `GET /interview/questions`.

### 5. Device & Hardware Check (`#view-device-check`)
- **Template & CSS:** `frontend/index.html` (lines 3102-3550), `frontend/style.css` (lines 9501-10200).
- **Entry Points:** Setup "Continue to Device Check" CTA (`#btn-setup-continue`).
- **Exit Points:**
  - "Back to Setup" button (`#btn-device-back-setup`) -> `#view-interview-setup`.
  - "Start Interview Now" button (`#btn-start-interview-confirmed`) -> `#view-practice`.
- **Hardware Integration:** Webcam video stream preview via `<video id="device-video-preview">`, Audio VU meter via `<canvas id="device-audio-meter">`, MediaPipe FaceMesh detection initialization.

### 6. Live Practice Room (`#view-practice`)
- **Template & CSS:** `frontend/index.html` (lines 1102-1848), `frontend/style.css` (lines 4401-6499).
- **Entry Points:** Device check confirmed start, Quick Start action.
- **Exit Points:**
  - "End Interview" button (`#btn-end-interview`) -> Triggers early wrap-up or `#completion-card`.
  - Completion of all interview questions -> Automatically transitions to `#completion-card`.
  - Emergency Quit / Leave session -> `#view-dashboard`.
- **Backend APIs:** `POST /interview/audio/upload`, `POST /transcribe-audio`, `POST /evaluate-answer`, `POST /visual-analysis`, `POST /interviews`.

### 7. Comprehensive Assessment Report (`#completion-card`)
- **Template & CSS:** `frontend/index.html` (lines 1328-1700), `frontend/style.css` (lines 5500-6400).
- **Entry Points:** End of interview session in `#view-practice`, History view "View Report" click (`#btn-history-view-{id}`).
- **Exit Points:**
  - "Download PDF" button (`#btn-download-report`) -> Downloads official vector PDF via `GET /interviews/{id}/report/pdf`.
  - "Return to Dashboard" button (`#btn-report-dashboard`) -> `#view-dashboard`.
  - "Practice Another Session" button (`#btn-report-retry`) -> `#view-interview-setup`.
- **Backend APIs:** `GET /interviews/{id}/report`, `GET /interviews/{id}/report/pdf`.

### 8. Interview History & Reports (`#view-history`)
- **Template & CSS:** `frontend/index.html` (lines 3552-3850), `frontend/style.css` (lines 10201-10550).
- **Entry Points:** Dashboard "View All Practice Sessions" CTA, Avatar dropdown "History".
- **Exit Points:**
  - Back to Dashboard button (`#btn-history-back-dash`) -> `#view-dashboard`.
  - "View Report" button on session card -> Displays `#completion-card` populated with historical evaluation data.
  - "Download PDF" button on session card -> Directly streams PDF.
  - "Delete Session" button -> `DELETE /interviews/{id}`.
- **Backend APIs:** `GET /interviews`, `DELETE /interviews/{id}`.

### 9. Admin Management Console (`#view-admin`)
- **Template & CSS:** `frontend/index.html` (lines 3852-4279), `frontend/style.css` (lines 10551-10972).
- **Entry Points:** Avatar dropdown "Admin Console" (strictly displayed only for `currentUser.is_admin == true`), Direct URL `/?view=admin`.
- **Exit Points:**
  - Back to Dashboard button (`#btn-admin-back-dash`) -> `#view-dashboard`.
  - Logout action -> Redirects to landing page.
- **Backend APIs:** `GET /admin/stats`, `GET /admin/users`, `PUT /admin/users/{id}/role`, `DELETE /admin/users/{id}`, `GET /admin/interviews`, `DELETE /admin/interviews/{id}`.

---

## 3. AUDIT OF ROUTE INTEGRITY & ANOMALIES

- **Missing Pages:** 0. All 8 core views and 5 modals are present in the DOM.
- **Duplicate Pages:** 0. Views are strictly demarcated with unique `.view-panel` IDs.
- **Broken Routes:** 0. Handled via central `navigateToView()` router with `history.pushState` and URL parameter sync (`?view={viewName}`).
- **Orphan Pages:** 0. Every view has multiple clear inbound navigation buttons and clear back buttons.
- **Protected-Route Handling:** Enforced in `navigateToView(viewName)`. Unauthenticated attempts to access protected routes (`dashboard`, `profile`, `interview-setup`, `device-check`, `practice`, `history`, `admin`) trigger a toast warning, display the Auth Modal, and redirect safely to `landing`.
- **Admin Security:** Non-admin attempts to access `admin` route are rejected and redirected to `dashboard`.
"""

with open("PAGE_INVENTORY.md", "w", encoding="utf-8") as f:
    f.write(page_inventory_md)

print("Generated PAGE_INVENTORY.md.")

route_map_md = """# AI INTERVIEW ANALYZER — COMPLETE ROUTE & DEPENDENCY MAP
**Document Reference:** `ROUTE_MAP.md`  
**Standard:** Enterprise Full-Stack Route & API Dependency Architecture  
**Target System:** `d:\\AI-Interview-Analyzer`  
**Execution Timestamp:** 2026-11-11  

---

## 1. CLIENT-SIDE VIEW TRANSITION GRAPH

```mermaid
flowchart TD
    Landing["Landing Page (#view-landing)"]
    AuthModal["Auth Modal (#auth-modal)"]
    Dashboard["Dashboard (#view-dashboard)"]
    Profile["Profile & Analytics (#view-profile)"]
    Setup["Interview Setup (#view-interview-setup)"]
    DeviceCheck["Device Check (#view-device-check)"]
    Practice["Live Practice Room (#view-practice)"]
    Report["Assessment Report (#completion-card)"]
    History["Interview History (#view-history)"]
    Admin["Admin Panel (#view-admin)"]

    Landing -->|Login / Register CTA| AuthModal
    Landing -->|Start Free Practice| Setup
    AuthModal -->|Successful Auth| Dashboard
    
    Dashboard -->|Start New Practice| Setup
    Dashboard -->|Customize Profile| Profile
    Dashboard -->|View All Sessions| History
    Dashboard -->|Admin Shortcut| Admin
    
    Setup -->|Back to Dashboard| Dashboard
    Setup -->|Continue to Device Check| DeviceCheck
    
    DeviceCheck -->|Back to Setup| Setup
    DeviceCheck -->|Start Interview Now| Practice
    
    Practice -->|Complete All Questions| Report
    Practice -->|Early End Interview| Report
    
    Report -->|Return to Dashboard| Dashboard
    Report -->|Practice Another Session| Setup
    Report -->|Download PDF| Report
    
    History -->|Back to Dashboard| Dashboard
    History -->|View Session Report| Report
    
    Admin -->|Back to Dashboard| Dashboard
```

---

## 2. BACKEND REST API ENDPOINTS CATALOG

### Authentication Router (`/auth`)
| HTTP Method | URL Path | Function Name | Request Payload | Response Model | Auth Requirement |
|---|---|---|---|---|---|
| `POST` | `/auth/register` | `register` | `UserCreate` (email, password, full_name) | `TokenResponse` (token, user) | Public |
| `POST` | `/auth/login` | `login` | `UserLogin` (email, password) | `TokenResponse` (token, user) | Public |
| `GET` | `/auth/me` | `get_me` | None (Bearer token) | `UserResponse` | Authenticated User |
| `POST` | `/auth/logout` | `logout` | None (Bearer token) | `{"message": "Logged out"}` | Authenticated User |

### Candidate Profile & Analytics Router (`/profile`)
| HTTP Method | URL Path | Function Name | Request Payload | Response Model | Auth Requirement |
|---|---|---|---|---|---|
| `GET` | `/profile` | `get_user_profile` | None (Bearer token) | `UserProfileResponse` | Authenticated User |
| `PUT` | `/profile` | `update_user_profile` | `UserProfileUpdate` (skills, role, exp) | `UserProfileResponse` | Authenticated User |
| `POST` | `/profile/resume` | `upload_resume` | `multipart/form-data` (file) | `ResumeUploadResponse` | Authenticated User |
| `GET` | `/profile/analytics` | `get_profile_analytics` | None (Bearer token) | `ProfileAnalyticsResponse` | Authenticated User |
| `GET` | `/profile/pdf` | `get_profile_analytics_pdf`| None (Bearer token) | `application/pdf` stream | Authenticated User |

### Interview & Question Engine Router (`/interviews`, `/interview`)
| HTTP Method | URL Path | Function Name | Request Payload | Response Model | Auth Requirement |
|---|---|---|---|---|---|
| `GET` | `/interview/questions` | `get_questions` | Query (role, difficulty, count) | `List[QuestionPublicResponse]` | Public / Optional Auth |
| `POST` | `/interview/questions` | `get_questions_post` | `QuestionRequest` | `List[QuestionPublicResponse]` | Public / Optional Auth |
| `POST` | `/interviews` | `create_interview` | `InterviewCreate` | `InterviewResponse` | Authenticated User |
| `GET` | `/interviews` | `get_interviews` | None (Bearer token) | `List[InterviewSummary]` | Authenticated User |
| `GET` | `/interviews/{id}` | `get_interview_by_id` | Path param `{id}` | `InterviewDetailResponse` | Owner / Admin |
| `DELETE` | `/interviews/{id}` | `delete_interview` | Path param `{id}` | `{"message": "Deleted"}` | Owner / Admin |
| `GET` | `/interviews/{id}/report` | `get_interview_report` | Path param `{id}` | `ComprehensiveReportResponse` | Owner / Admin |
| `GET` | `/interviews/{id}/report/pdf` | `get_interview_pdf` | Path param `{id}` | `application/pdf` stream | Owner / Admin |
| `POST` | `/interviews/preview-pdf` | `preview_interview_pdf` | `PreviewPDFRequest` | `application/pdf` stream | Authenticated User |

### AI / Speech & ML Evaluation Endpoints
| HTTP Method | URL Path | Function Name | Request Payload | Response Model | Auth Requirement |
|---|---|---|---|---|---|
| `POST` | `/interview/audio/upload` | `upload_interview_audio`| `multipart/form-data` (audio file) | `AudioUploadResponse` | Authenticated User |
| `POST` | `/transcribe-audio` | `transcribe_audio` | `multipart/form-data` (audio file) | `{"transcript": str}` | Authenticated User |
| `POST` | `/evaluate-answer` | `evaluate_answer` | `AnswerEvaluationRequest` | `AnswerEvaluationResponse` | Authenticated User |
| `POST` | `/visual-analysis` | `analyze_visual_signals`| `VisualAnalysisRequest` | `VisualAnalysisResponse` | Authenticated User |
| `POST` | `/transcribe-and-score` | `transcribe_and_score` | `multipart/form-data` (audio + q_id) | `ComprehensiveEvaluationResponse` | Public / Optional Auth |

### Administrator Router (`/admin`)
| HTTP Method | URL Path | Function Name | Request Payload | Response Model | Auth Requirement |
|---|---|---|---|---|---|
| `GET` | `/admin/stats` | `get_admin_stats` | None (Bearer token) | `AdminStatsResponse` | Admin Only |
| `GET` | `/admin/users` | `list_admin_users` | Query (limit, offset, search) | `PaginatedUsersResponse` | Admin Only |
| `GET` | `/admin/users/{id}` | `get_admin_user_details`| Path param `{id}` | `AdminUserDetailResponse` | Admin Only |
| `PUT` | `/admin/users/{id}/role` | `update_user_role` | `RoleUpdateRequest` | `UserResponse` | Admin Only |
| `DELETE` | `/admin/users/{id}` | `delete_admin_user` | Path param `{id}` | `{"message": "User deleted"}` | Admin Only |
| `GET` | `/admin/interviews` | `list_admin_interviews`| Query (limit, offset) | `PaginatedInterviewsResponse` | Admin Only |
| `DELETE` | `/admin/interviews/{id}` | `delete_admin_interview`| Path param `{id}` | `{"message": "Interview deleted"}`| Admin Only |

---

## 3. PROTECTED ROUTE & SECURITY MATRIX

```
+------------------------+-------------------+---------------------------------------------------+
| Route / Panel          | Minimum Privilege | Enforcement Location                              |
+------------------------+-------------------+---------------------------------------------------+
| Landing (#view-landing)| Public            | None (Open to all visitors)                       |
| Auth Modal             | Public            | None (Login / Registration)                       |
| Dashboard              | Candidate User    | Client: navigateToView() -> redirect to auth modal|
|                        |                   | Server: Bearer Token required on /profile, /stats |
| Profile & Analytics    | Candidate User    | Client: navigateToView() -> redirect to auth modal|
|                        |                   | Server: Bearer Token required on /profile/resume  |
| Interview Setup        | Candidate User    | Client: navigateToView() -> redirect to auth modal|
| Device Check           | Candidate User    | Client: navigateToView() -> redirect to auth modal|
| Live Practice Room     | Candidate User    | Client: navigateToView() -> redirect to auth modal|
|                        |                   | Server: Bearer Token required on /evaluate-answer |
| Assessment Report      | Candidate User    | Client: navigateToView()                          |
|                        |                   | Server: User ID ownership check on interview id   |
| Interview History      | Candidate User    | Client: navigateToView() -> redirect to auth modal|
|                        |                   | Server: User ID query scoping on /interviews      |
| Admin Console          | Superadmin        | Client: currentUser.is_admin == true check        |
|                        |                   | Server: get_admin_user dependency on /admin/*     |
+------------------------+-------------------+---------------------------------------------------+
```
"""

with open("ROUTE_MAP.md", "w", encoding="utf-8") as f:
    f.write(route_map_md)

print("Generated ROUTE_MAP.md.")


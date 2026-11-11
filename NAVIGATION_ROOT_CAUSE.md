# NAVIGATION & REDIRECT ROOT CAUSE INVESTIGATION REPORT
**Project:** AI Interview Analyzer  
**Date:** November 11, 2026  
**Auditor / Engineer:** Senior Full-Stack Developer & Software Architect  
**Status:** FULLY INVESTIGATED & RESOLVED  

---

## 1. Executive Summary

A critical navigation flaw was identified in the AI Interview Analyzer web client where candidate users were unable to reliably access their personal profile, and navigation between the Home landing page, the User Dashboard, Candidate Profile, and Performance Analytics was conflated.

Specific user symptoms reported:
1. **Home -> Dashboard Navigation Failure:** Attempting to navigate from the Landing page to the authenticated User Dashboard exhibited broken redirect flow or looped back onto modal triggers.
2. **Profile Button Opens Analytics Dashboard:** Clicking the "Profile" navigation button opened the Analytics and Performance Reports dashboard instead of personal user profile settings.
3. **Analytics Navigation Duplication / Misrouting:** Clicking the "Analytics" navigation button navigated to the exact same DOM view as the Profile button.
4. **Button Aliasing & Disconnected Destinations:** Multiple navigation controls in the header, user avatar dropdown, and mobile navigation drawer were either aliased to the same view identifier or lacked independent view panels in the DOM.

A systematic audit revealed that this was caused by architectural view aliasing in the single-page application (SPA) router and an architectural omission where the user profile form was relegated to an unmounted overlay modal while the analytics dashboard occupied the DOM panel named `view-profile`.

---

## 2. Root Cause Analysis (Bug by Bug)

### 2.1. Bug #1: Home to Dashboard Redirect Interception & Modal Looping
- **Affected Files:** `frontend/script.js` (lines 5985–6030)
- **Mechanism:**  
  When an unauthenticated user arrived at `/?view=landing` or `/` and initiated authentication (via the "Log In" button or by clicking a protected action like "Practice Now"), the submission handler `handleLoginSubmit()` previously executed:
  ```javascript
  // Old code snippet in handleLoginSubmit:
  authToken = data.access_token;
  currentUser = data.user;
  updateAuthWidget();
  hideAuthModal();
  showProfileModal(); // <--- CRITICAL FLAW: FORCED PROFILE MODAL OVER LANDING
  ```
  Instead of transitioning the view to `dashboard` (or remembering the user's intended destination prior to login), the code opened the onboarding modal `showProfileModal()` while remaining anchored to `#view-landing`. Closing that modal left the user stranded on the landing page, giving the impression that login had failed or navigation was broken.
- **Missing Intent Tracking:**  
  When an unauthenticated user attempted to access protected views (`dashboard`, `interview-setup`, `history`, `profile`, `analytics`, `admin`), `navigateToView(viewName)` intercepted the request and called `showAuthModal('login')`, but completely dropped the destination parameter. Once logged in, the application had no record of what view the user was trying to access.

---

### 2.2. Bug #2 & Bug #3: Profile and Analytics Route Aliasing
- **Affected Files:** `frontend/index.html` (lines 2250–2500) and `frontend/script.js` (lines 1575–1585)
- **Mechanism:**  
  In `frontend/index.html`, the application defined view panels using the convention `<div class="view-panel" id="view-[name]">`.  
  However, there was **NO** `<div class="view-panel" id="view-analytics">`.  
  Instead, the Performance Analytics dashboard (containing the readiness gauge, score trends chart, category breakdown bar chart, and reports list) was placed directly inside:
  ```html
  <!-- View panel erroneously named "view-profile" -->
  <div class="view-panel" id="view-profile">
    <div class="profile-analytics-wrapper"> ... </div>
  </div>
  ```
  Meanwhile, the actual Candidate Profile form (full name, target role, years of experience, resume upload, skills tags) was trapped inside a hidden modal dialog: `<div id="profile-modal" class="modal-overlay hidden">`.
- **Router Aliasing in `script.js`:**  
  Because there was no `view-analytics` in the DOM, `navigateToView()` had a hardcoded alias:
  ```javascript
  // Line 1579 in old script.js:
  const targetPanelId = (viewName === 'analytics') ? 'view-profile' : `view-${viewName}`;
  ```
  Consequently:
  - When the user clicked **Profile** (`#nav-profile-btn`), `navigateToView('profile')` activated `#view-profile`, rendering the Analytics charts.
  - When the user clicked **Analytics** (`#nav-analytics-btn`), `navigateToView('analytics')` resolved to `#view-profile`, rendering the exact same Analytics charts.
  - Clicking either button yielded the exact same screen, leaving no standalone page for the candidate's personal profile credentials.

---

### 2.3. Bug #4: Navbar Button Binding & State Inconsistencies
- **Affected Files:** `frontend/index.html` (lines 90–120) and `frontend/script.js` (lines 1600–1695)
- **Mechanism:**  
  1. The authenticated navbar container `#auth-nav` contained `#nav-profile-btn` and `#nav-analytics-btn`, but lacked `data-view` attributes on several buttons.
  2. The event listeners inside `initNavigation()` only attached listeners to `#nav-dash-btn` and `#nav-practice-btn`, relying on an incomplete delegation loop or duplicate handlers in `updateAuthWidget()`.
  3. The user avatar dropdown (`#nav-profile-menu-dropdown`) only contained an item labeled "Profile Settings" (`#npd-item-profile`) which opened the profile modal, and an item for "Dashboard", but had no dedicated option for "Performance Analytics".
  4. Active navbar pill styling (`.nav-btn-link.active`) was hardcoded to check only `dashboard` and `interview-setup`, leaving `profile` and `analytics` buttons in an inactive visual state even when their views were visible.

---

## 3. Summary of Root Cause Matrix

| Issue ID | Problem | Root Cause | Impact |
|---|---|---|---|
| **RC-01** | Profile button opens Analytics | `view-profile` DOM panel contained the Analytics dashboard; profile form was trapped in a modal `#profile-modal`. | Candidate could not view or edit profile as a standalone page. |
| **RC-02** | Analytics button opens same page | `navigateToView('analytics')` aliased `targetPanelId` directly to `'view-profile'`. | Redundant navigation; user confused by identical destination. |
| **RC-03** | Home -> Dashboard redirect failure | `handleLoginSubmit` called `showProfileModal()` instead of navigating to `dashboard` and did not track `intendedViewAfterLogin`. | User was left on landing page after successful authentication. |
| **RC-04** | Active navbar highlight missing | `navigateToView` only toggled active classes on `#nav-dash-btn` and `#nav-practice-btn`. | Broken affordance and navigation feedback. |
| **RC-05** | Refresh desynchronization | Reloading `/?view=analytics` forced `targetPanelId = 'view-profile'`, desynchronizing query params from active DOM panel. | Inability to deep-link to analytics vs profile. |

---

## 4. Verification of Resolution Architecture

The architectural fix permanently decouples the two domains:
1. **Dedicated View Panel `#view-profile`:**  
   Contains a high-fidelity Candidate Profile workspace with candidate avatar, verified badge, education/status meta cards, attached resume management box with drag-and-drop parsing, AI-detected skills tags cloud, and full candidate details form that reads from `GET /profile` and saves via `PUT /profile`.
2. **Dedicated View Panel `#view-analytics`:**  
   Retains the comprehensive Analytics workspace with the overall readiness donut gauge, score trend line graphs, category breakdowns, WeasyPrint PDF report download, and historical reports list.
3. **Strict 1:1 View Routing:**  
   `navigateToView(viewName)` maps strictly to `document.getElementById('view-' + viewName)` with zero aliases.
4. **Intent-Preserving Authentication Redirects:**  
   `intendedViewAfterLogin` stores protected route requests when unauthenticated and immediately navigates to the requested view upon successful login.

Full details of the fix implementation and mapping are detailed in `ROUTE_MAPPING_REPORT.md` and `NAVIGATION_FIX_REPORT.md`.

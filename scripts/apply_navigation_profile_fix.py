import os
import sys

# 1. READ INDEX.HTML
with open("frontend/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace auth-nav buttons
old_auth_nav = '''      <!-- Authenticated Navigation Links (hidden when logged out) -->
      <nav class="nav-links auth-nav-links hidden" id="auth-nav">
        <button class="landing-nav-item nav-btn-link active" id="nav-dash-btn">Dashboard</button>
        <button class="landing-nav-item nav-btn-link" id="nav-practice-btn">Start Interview</button>
        <button class="landing-nav-item nav-btn-link" id="nav-profile-btn">Profile</button>
        <button class="landing-nav-item nav-btn-link" id="nav-analytics-btn">Analytics</button>
        <button class="landing-nav-item nav-btn-link hidden" id="nav-admin-btn">Admin Panel</button>
      </nav>'''

new_auth_nav = '''      <!-- Authenticated Navigation Links (hidden when logged out) -->
      <nav class="nav-links auth-nav-links hidden" id="auth-nav">
        <button class="landing-nav-item nav-btn-link" id="nav-home-btn" data-view="landing">Home</button>
        <button class="landing-nav-item nav-btn-link active" id="nav-dash-btn" data-view="dashboard">Dashboard</button>
        <button class="landing-nav-item nav-btn-link" id="nav-practice-btn" data-view="interview-setup">Start Interview</button>
        <button class="landing-nav-item nav-btn-link" id="nav-profile-btn" data-view="profile">Profile</button>
        <button class="landing-nav-item nav-btn-link" id="nav-analytics-btn" data-view="analytics">Analytics</button>
        <button class="landing-nav-item nav-btn-link hidden" id="nav-admin-btn" data-view="admin">Admin Panel</button>
      </nav>'''

if old_auth_nav in html:
    html = html.replace(old_auth_nav, new_auth_nav, 1)
    print("Replaced auth-nav in index.html")
else:
    print("WARNING: old_auth_nav not found in index.html")

# Replace dropdown items
old_dropdown = '''              <button class="npmd-link-btn" id="npmd-item-profile">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                <span>Profile & Analytics</span>
              </button>
              <button class="npmd-link-btn" id="npmd-item-dashboard">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                <span>Dashboard</span>
              </button>'''

new_dropdown = '''              <button class="npmd-link-btn" id="npmd-item-profile">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                <span>Candidate Profile</span>
              </button>
              <button class="npmd-link-btn" id="npmd-item-analytics">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                <span>Performance Analytics</span>
              </button>
              <button class="npmd-link-btn" id="npmd-item-dashboard">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                <span>Dashboard</span>
              </button>'''

if old_dropdown in html:
    html = html.replace(old_dropdown, new_dropdown, 1)
    print("Replaced dropdown in index.html")
else:
    print("WARNING: old_dropdown not found in index.html")

# Replace mobile drawer
old_mobile = '''    <!-- Mobile Navigation Drawer -->
    <div class="mobile-nav-drawer hidden" id="mobile-nav-drawer">
      <a href="#how-it-works" class="mobile-nav-item">How It Works</a>
      <a href="#features" class="mobile-nav-item">Features</a>
      <a href="#performance-report" class="mobile-nav-item">Analytics</a>
      <div class="mobile-nav-actions">
        <button class="btn btn-secondary w-full" id="mobile-login-btn">Log in</button>
        <button class="btn btn-primary w-full" id="mobile-start-btn">Start Interview</button>
      </div>
    </div>'''

new_mobile = '''    <!-- Mobile Navigation Drawer -->
    <div class="mobile-nav-drawer hidden" id="mobile-nav-drawer">
      <div class="mobile-auth-links hidden" id="mobile-auth-links">
        <button class="mobile-nav-item mobile-nav-btn" id="mobile-nav-dash-btn">Dashboard</button>
        <button class="mobile-nav-item mobile-nav-btn" id="mobile-nav-profile-btn">Profile</button>
        <button class="mobile-nav-item mobile-nav-btn" id="mobile-nav-analytics-btn">Analytics</button>
        <button class="mobile-nav-item mobile-nav-btn" id="mobile-nav-practice-btn">Start Interview</button>
        <button class="mobile-nav-item mobile-nav-btn" id="mobile-nav-history-btn">History</button>
      </div>
      <a href="#how-it-works" class="mobile-nav-item">How It Works</a>
      <a href="#features" class="mobile-nav-item">Features</a>
      <a href="#performance-report" class="mobile-nav-item">Analytics Preview</a>
      <div class="mobile-nav-actions">
        <button class="btn btn-secondary w-full" id="mobile-login-btn">Log in</button>
        <button class="btn btn-primary w-full" id="mobile-start-btn">Start Interview</button>
      </div>
    </div>'''

if old_mobile in html:
    html = html.replace(old_mobile, new_mobile, 1)
    print("Replaced mobile drawer in index.html")
else:
    print("WARNING: old_mobile not found in index.html")

# Rename lines 2256 from id="view-profile" to id="view-analytics" and insert dedicated view-profile right before it
old_profile_view_start = '''    <!-- VIEW 4.5: CANDIDATE PROFILE & ANALYTICS WORKSPACE (AUTHENTICATED) -->
    <div class="view-panel" id="view-profile">
      <div class="profile-analytics-wrapper">

        <!-- Ambient Glow Backdrops -->
        <div class="profile-ambient-glow profile-glow-top-left" aria-hidden="true"></div>
        <div class="profile-ambient-glow profile-glow-top-right" aria-hidden="true"></div>
        <div class="profile-ambient-glow profile-glow-mid" aria-hidden="true"></div>

        <!-- 1. USER PROFILE HERO SECTION -->
        <section class="profile-hero-card">
          <!-- Left: User Details & Meta Chips -->
          <div class="ph-left">
            <button class="btn btn-back-dashboard" id="btn-profile-back-dash" title="Return to Candidate Dashboard">'''

new_profile_and_analytics_views = '''    <!-- VIEW 4: CANDIDATE PROFILE WORKSPACE (AUTHENTICATED) -->
    <div class="view-panel" id="view-profile">
      <div class="profile-page-wrapper">
        <!-- Ambient Glow Backdrops -->
        <div class="profile-ambient-glow profile-glow-top-left" aria-hidden="true"></div>
        <div class="profile-ambient-glow profile-glow-top-right" aria-hidden="true"></div>
        <div class="profile-ambient-glow profile-glow-mid" aria-hidden="true"></div>

        <!-- PROFILE PAGE HEADER -->
        <header class="profile-page-header">
          <div class="pph-top-row">
            <button class="btn btn-back-dashboard" id="btn-profile-back-dash" title="Return to Candidate Dashboard">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              <span>Back to Dashboard</span>
            </button>
            <button class="btn btn-secondary btn-sm" id="btn-profile-to-analytics" title="Go to Performance Analytics">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
              <span>View Analytics →</span>
            </button>
          </div>
          <h1 class="profile-page-title">Candidate <span class="gradient-text">Profile</span> & Credentials</h1>
          <p class="profile-page-subtitle">Manage your personal credentials, target role, technical skills, and resume personalization.</p>
        </header>

        <!-- PROFILE MAIN 2-COLUMN GRID -->
        <div class="profile-page-grid">

          <!-- LEFT COLUMN: IDENTITY & RESUME -->
          <div class="profile-grid-col-left">

            <!-- Card 1: Identity Card -->
            <div class="profile-card-base pcard-identity">
              <div class="pcard-identity-header">
                <div class="profile-avatar-large-wrap">
                  <img src="assets/illustrations/candidate_avatar.png" alt="Candidate Avatar" class="profile-avatar-large" id="profile-page-avatar" onerror="this.src='assets/illustrations/hero_candidate_isolated_transparent.png'" />
                  <div class="avatar-verified-badge" title="Verified Candidate">✓</div>
                </div>
                <div class="pcard-identity-meta">
                  <h2 class="pcard-user-name" id="profile-page-name-display">Candidate Name</h2>
                  <p class="pcard-user-email" id="profile-page-email-display">candidate@example.com</p>
                  <div class="pcard-chips-row">
                    <span class="badge badge-primary-subtle" id="profile-page-role-badge">Software Engineer</span>
                    <span class="badge badge-success-subtle" id="profile-page-exp-badge">1–3 Years</span>
                  </div>
                </div>
              </div>
              <div class="pcard-divider"></div>
              <div class="pcard-meta-list">
                <div class="pcard-meta-item">
                  <span class="pmi-icon">📅</span>
                  <span class="pmi-label">Account Status:</span>
                  <strong class="pmi-val" id="profile-page-joined">Active Candidate</strong>
                </div>
                <div class="pcard-meta-item">
                  <span class="pmi-icon">🎯</span>
                  <span class="pmi-label">Interview Difficulty:</span>
                  <strong class="pmi-val" id="profile-page-diff-display">Intermediate</strong>
                </div>
                <div class="pcard-meta-item">
                  <span class="pmi-icon">🎓</span>
                  <span class="pmi-label">Degree / Field:</span>
                  <strong class="pmi-val" id="profile-page-edu-display">Computer Applications</strong>
                </div>
              </div>
            </div>

            <!-- Card 2: Attached Resume & Skills -->
            <div class="profile-card-base pcard-resume">
              <div class="pcard-header-row">
                <div class="pcard-title-group">
                  <span class="pcard-icon">📄</span>
                  <h3 class="pcard-title">Attached Resume</h3>
                </div>
                <span class="badge badge-success-subtle" id="profile-resume-status-badge">Active</span>
              </div>
              <p class="pcard-desc">Your uploaded resume is used by our AI engine to generate personalized interview questions matching your exact background.</p>

              <!-- Uploaded file chip -->
              <div class="profile-attached-file-box" id="profile-attached-file-box">
                <div class="paf-icon">📎</div>
                <div class="paf-info">
                  <strong class="paf-name" id="profile-attached-filename">No resume uploaded yet</strong>
                  <span class="paf-sub" id="profile-attached-sub">PDF, DOCX, or TXT (Max 10MB)</span>
                </div>
              </div>

              <!-- Drag and drop zone -->
              <div class="profile-resume-dropzone" id="profile-page-resume-dropzone">
                <input type="file" id="profile-page-resume-file" accept=".pdf,.docx,.txt" class="hidden" />
                <div class="prd-content" id="prd-idle-content">
                  <span class="prd-icon">☁️</span>
                  <strong class="prd-title">Drop new resume here or click to browse</strong>
                  <span class="prd-hint">Auto-extracts skills, programming languages, and experience</span>
                </div>
                <div class="prd-loading hidden" id="prd-loading-content">
                  <span>⏳ Parsing resume and extracting skills with AI...</span>
                </div>
              </div>

              <!-- Detected Skills Tags Cloud -->
              <div class="profile-skills-section">
                <label class="form-label-sub">AI-Detected Skills & Tags</label>
                <div class="profile-skills-tags-wrap" id="profile-page-skills-tags">
                  <span class="tag-pill tag-muted">Upload a resume to auto-detect skills</span>
                </div>
              </div>
            </div>

          </div>

          <!-- RIGHT COLUMN: DETAILED EDIT FORM -->
          <div class="profile-grid-col-right">
            <div class="profile-card-base pcard-form-card">
              <div class="pcard-header-row">
                <div class="pcard-title-group">
                  <span class="pcard-icon">✏️</span>
                  <h3 class="pcard-title">Personal & Technical Details</h3>
                </div>
                <span class="badge badge-primary-subtle">Authenticated Profile</span>
              </div>
              <p class="pcard-desc">Keep your details up to date so your mock interviews, reports, and readiness recommendations reflect your goals.</p>

              <form id="profile-page-form" class="profile-main-form">
                <div class="form-row-2">
                  <div class="form-group">
                    <label for="prof-page-name">Full Name</label>
                    <input type="text" id="prof-page-name" class="form-control" placeholder="Candidate Name" required />
                  </div>
                  <div class="form-group">
                    <label for="prof-page-target-role">Target Job Role</label>
                    <select id="prof-page-target-role" class="form-control" required>
                      <option value="Software Engineer" selected>Software Engineer</option>
                      <option value="Frontend Developer">Frontend Developer</option>
                      <option value="Backend Developer">Backend Developer</option>
                      <option value="Full Stack Developer">Full Stack Developer</option>
                      <option value="Data Scientist">Data Scientist</option>
                      <option value="DevOps Engineer">DevOps Engineer</option>
                      <option value="Product Manager">Product Manager</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>

                <div class="form-row-3">
                  <div class="form-group">
                    <label for="prof-page-exp-type">Experience Level</label>
                    <select id="prof-page-exp-type" class="form-control" required>
                      <option value="Student">Student</option>
                      <option value="Entry Level">Entry Level</option>
                      <option value="1-3 Years" selected>1–3 Years</option>
                      <option value="3-5 Years">3–5 Years</option>
                      <option value="5+ Years">5+ Years</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label for="prof-page-years-exp">Years of Experience</label>
                    <input type="number" step="0.5" min="0" max="30" id="prof-page-years-exp" class="form-control" placeholder="1.5" />
                  </div>
                  <div class="form-group">
                    <label for="prof-page-difficulty">Interview Difficulty</label>
                    <select id="prof-page-difficulty" class="form-control">
                      <option value="Beginner">Beginner</option>
                      <option value="Intermediate" selected>Intermediate</option>
                      <option value="Advanced">Advanced</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label for="prof-page-skills">Skills & Technologies (comma-separated)</label>
                  <input type="text" id="prof-page-skills" class="form-control" placeholder="e.g. Python, React, FastAPI, SQL, Docker, AWS" required />
                </div>

                <div class="form-group">
                  <label for="prof-page-languages">Programming Languages</label>
                  <input type="text" id="prof-page-languages" class="form-control" placeholder="e.g. Python, JavaScript, TypeScript, SQL, Java, C++" />
                </div>

                <div class="form-group">
                  <label for="prof-page-projects">Key Projects / Technical Highlights</label>
                  <textarea id="prof-page-projects" class="form-control" rows="3" placeholder="Describe 1–2 notable technical projects, responsibilities, or accomplishments..."></textarea>
                </div>

                <div class="form-row-2">
                  <div class="form-group">
                    <label for="prof-page-education">Degree / Field of Study</label>
                    <input type="text" id="prof-page-education" class="form-control" placeholder="e.g. Bachelor of Computer Applications" />
                  </div>
                  <div class="form-group">
                    <label for="prof-page-college">College / University</label>
                    <input type="text" id="prof-page-college" class="form-control" placeholder="e.g. Navgujarat College" />
                  </div>
                </div>

                <div class="profile-form-actions">
                  <button type="submit" class="btn btn-primary btn-lg" id="btn-save-profile-page">
                    <span>Save Profile Changes</span>
                  </button>
                  <button type="button" class="btn btn-secondary btn-lg" id="btn-reset-profile-page">
                    <span>Reset Changes</span>
                  </button>
                </div>
              </form>
            </div>
          </div>

        </div>

        <!-- PROFILE INTEGRATED FOOTER -->
        <footer class="app-footer profile-page-integrated-footer">
          <div class="footer-container">
            <div class="footer-left-brand">
              <div class="footer-logo">
                <div class="brand-icon small">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                  </svg>
                </div>
                <span class="footer-brand-name">AI Interview Analyzer</span>
              </div>
              <p class="footer-tagline">AI-powered interview practice and candidate personalization.</p>
            </div>
            <div class="footer-center-copy">
              <p class="footer-copyright">© 2026 AI Interview Analyzer. All rights reserved.</p>
            </div>
            <div class="footer-links-grid">
              <div class="footer-col">
                <h4 class="footer-heading">PRODUCT</h4>
                <a href="#how-it-works" class="footer-link">How It Works</a>
                <a href="#features" class="footer-link">Features</a>
                <a href="#performance-report" class="footer-link">Analytics</a>
              </div>
              <div class="footer-col">
                <h4 class="footer-heading">LEGAL</h4>
                <a href="#" class="footer-link policy-privacy-link">Privacy</a>
                <a href="#" class="footer-link policy-terms-link">Terms</a>
              </div>
            </div>
          </div>
        </footer>

      </div>
    </div>

    <!-- VIEW 4.5: PERFORMANCE ANALYTICS WORKSPACE (AUTHENTICATED) -->
    <div class="view-panel" id="view-analytics">
      <div class="profile-analytics-wrapper">

        <!-- Ambient Glow Backdrops -->
        <div class="profile-ambient-glow profile-glow-top-left" aria-hidden="true"></div>
        <div class="profile-ambient-glow profile-glow-top-right" aria-hidden="true"></div>
        <div class="profile-ambient-glow profile-glow-mid" aria-hidden="true"></div>

        <!-- 1. USER ANALYTICS HERO SECTION -->
        <section class="profile-hero-card">
          <!-- Left: User Details & Meta Chips -->
          <div class="ph-left">
            <button class="btn btn-back-dashboard" id="btn-analytics-back-dash" title="Return to Candidate Dashboard">'''

if old_profile_view_start in html:
    html = html.replace(old_profile_view_start, new_profile_and_analytics_views, 1)
    print("Successfully separated Profile and Analytics view panels in index.html!")
else:
    print("WARNING: old_profile_view_start not found in index.html")

# Write updated index.html
with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Updated frontend/index.html successfully.")

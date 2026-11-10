import sys

new_html = '''    <div class="view-panel" id="view-interview-setup">
      <!-- Background Ambient Glow Accents -->
      <div class="setup-ambient-glow setup-glow-top-right"></div>
      <div class="setup-ambient-glow setup-glow-bottom-left"></div>

      <div class="setup-wrapper">

        <!-- TOP HERO HEADER (TWO-COLUMN WITH 3D LAPTOP INTERVIEWER) -->
        <header class="setup-hero-split">
          <div class="setup-hero-content">
            <button class="btn-back-link" id="btn-setup-back-dash" type="button" aria-label="Back to Dashboard">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              <span>Back to Dashboard</span>
            </button>
            <h1 class="setup-hero-title">Set up your <span class="gradient-text">interview</span></h1>
            <div class="setup-hero-subtitle-wrap">
              <p class="setup-hero-subtitle">Customize your practice session before you begin.</p>
              <svg class="setup-title-wave" width="220" height="12" viewBox="0 0 220 12" fill="none" aria-hidden="true">
                <path d="M2 9C50 3 100 11 150 5C180 1.5 200 4 218 8" stroke="url(#paint-setup-wave)" stroke-width="3" stroke-linecap="round"/>
                <defs>
                  <linearGradient id="paint-setup-wave" x1="2" y1="6" x2="218" y2="6" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#1677FF"/>
                    <stop offset="1" stop-color="#792FFF"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>

          <div class="setup-hero-stage">
            <div class="setup-laptop-card">
              <!-- Floating Speech Bubble -->
              <div class="setup-speech-bubble">
                <span class="speech-text">Be Confident, You Got This!</span>
                <span class="speech-star">⭐</span>
              </div>
              <!-- Floating Blue Mic Badge -->
              <div class="setup-floating-mic">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                  <path d="M19 10v1a7 7 0 0 1-14 0v-1"></path>
                  <line x1="12" y1="19" x2="12" y2="23"></line>
                  <line x1="8" y1="23" x2="16" y2="23"></line>
                </svg>
              </div>
              <!-- 3D Laptop with Interviewer -->
              <img src="assets/illustrations/setup_laptop_interviewer_transparent.png"
                   alt="AI Interview Session Preview"
                   class="setup-hero-laptop-img"
                   loading="eager" />
            </div>
          </div>
        </header>

        <!-- MAIN TWO-COLUMN SETUP GRID -->
        <main class="setup-main-grid">

          <!-- LEFT COLUMN: CONFIGURATION SECTIONS -->
          <div class="setup-config-col">

            <!-- CARD 1: RESUME UPLOAD & AI PERSONALIZATION -->
            <section class="setup-card setup-resume-card" id="setup-resume-section" aria-label="Resume and AI Personalization">
              <div class="setup-card-header">
                <div class="setup-card-header-left">
                  <div class="setup-card-icon icon-blue">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                      <polyline points="14 2 14 8 20 8"></polyline>
                      <line x1="16" y1="13" x2="8" y2="13"></line>
                      <line x1="16" y1="17" x2="8" y2="17"></line>
                      <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                  </div>
                  <div>
                    <h2 class="setup-card-title">Candidate Resume (AI Personalized)</h2>
                    <p class="setup-card-hint">Upload your resume (.pdf, .docx, .txt) to generate personalized questions from your actual projects and tech stack.</p>
                  </div>
                </div>
                <div class="badge-ai-personalized" id="resume-status-badge">
                  <span class="b-check">✓</span> AI <span class="b-check">✓</span> PERSONALIZED
                </div>
              </div>

              <!-- RESUME DROPZONE (Hidden when preview is active) -->
              <div class="resume-dropzone hidden" id="setup-resume-dropzone">
                <input type="file" id="setup-resume-file-input" accept=".pdf,.docx,.txt" class="hidden">
                <div class="dropzone-content" id="dropzone-idle-content">
                  <div class="dropzone-icon">📄</div>
                  <div class="dropzone-text">
                    <strong class="dropzone-title">Click to upload resume or drag &amp; drop</strong>
                    <span class="dropzone-sub">Supports PDF, DOCX, and TXT (Max 10MB)</span>
                  </div>
                </div>
                <div class="dropzone-content hidden" id="dropzone-loading-content">
                  <div class="spinner-circle"></div>
                  <span class="dropzone-loading-text">Extracting skills, projects, and experience with AI...</span>
                </div>
              </div>

              <!-- PARSED RESUME PREVIEW PANEL -->
              <div class="setup-resume-preview" id="setup-resume-preview">
                <!-- Uploaded File Bar -->
                <div class="res-file-bar">
                  <div class="res-file-info">
                    <div class="res-check-circle">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                    </div>
                    <div class="res-file-text">
                      <strong class="res-filename" id="prp-filename">Jake_s_Resume__Anonymous__1__2_.pdf</strong>
                      <span class="res-meta-stats" id="prp-meta-stats">14 Skills • 1 Projects • 1 Roles Detected</span>
                    </div>
                  </div>
                  <button type="button" class="btn-change-file" id="btn-reupload-resume" aria-label="Change uploaded resume file">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
                    </svg>
                    <span>Change File</span>
                  </button>
                </div>

                <!-- Skill Chips Grid -->
                <div class="setup-skills-chips-wrapper" id="prp-skills-chips">
                  <span class="skill-tag-chip">PYTHON</span>
                  <span class="skill-tag-chip">JAVASCRIPT</span>
                  <span class="skill-tag-chip">JAVA</span>
                  <span class="skill-tag-chip">C#</span>
                  <span class="skill-tag-chip">PHP</span>
                  <span class="skill-tag-chip">HTML</span>
                  <span class="skill-tag-chip">CSS</span>
                  <span class="skill-tag-chip">DJANGO</span>
                  <span class="skill-tag-chip">LARAVEL</span>
                  <span class="skill-tag-chip">BOOTSTRAP</span>
                  <span class="skill-tag-chip">MYSQL</span>
                  <span class="skill-tag-chip">ORACLE</span>
                  <span class="skill-tag-chip">GITHUB</span>
                  <span class="skill-tag-chip">VS CODE</span>
                </div>

                <!-- Featured Projects Row -->
                <div class="setup-featured-projects-row" id="prp-projects-summary">
                  <span class="sfp-icon">📁</span>
                  <span class="sfp-label">Featured Projects:</span>
                  <strong class="sfp-name">Bootstrap</strong>
                </div>

                <!-- Collapsible Skills & Frameworks Accordion -->
                <div class="setup-skills-accordion">
                  <button type="button" class="setup-accordion-header" id="btn-toggle-skills-accordion" aria-expanded="false">
                    <span>Review or Add Technical Skills &amp; Frameworks (e.g. Django, Spring Boot, MySQL, Docker):</span>
                    <svg class="accordion-arrow-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                  </button>
                  <div class="setup-accordion-body" id="res-skills-accordion-body">
                    <div class="setup-skills-edit-bar">
                      <input type="text" id="prp-skills-editor" class="setup-skills-input" placeholder="Add or edit technical skills (comma separated)" value="PYTHON, JAVASCRIPT, JAVA, C#, PHP, HTML, CSS, DJANGO, LARAVEL, BOOTSTRAP, MYSQL, ORACLE, GITHUB, VS CODE">
                      <button type="button" class="btn btn-primary btn-sm btn-update-skills" id="btn-update-parsed-skills">Update Skills</button>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <!-- CARD 2: TARGET ROLE -->
            <section class="setup-card setup-role-card" aria-label="Target Role">
              <div class="setup-card-header setup-role-header">
                <div class="setup-card-header-left">
                  <div class="setup-card-icon icon-purple">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <circle cx="12" cy="12" r="6"></circle>
                      <circle cx="12" cy="2" r="2"></circle>
                    </svg>
                  </div>
                  <div>
                    <h2 class="setup-card-title">Target Role</h2>
                    <p class="setup-card-hint">Select the role you want to practice for.</p>
                  </div>
                </div>
                <div class="setup-select-container">
                  <select id="setup-role-select" class="setup-custom-dropdown" aria-label="Select target role">
                    <option value="Backend Developer" selected>Backend Developer</option>
                    <option value="Frontend Developer">Frontend Developer</option>
                    <option value="Full Stack Developer">Full Stack Developer</option>
                    <option value="Software Engineer">Software Engineer</option>
                    <option value="Data Scientist">Data Scientist</option>
                    <option value="Machine Learning Engineer">Machine Learning Engineer</option>
                    <option value="DevOps Engineer">DevOps Engineer</option>
                    <option value="Product Manager">Product Manager</option>
                    <option value="Data Analyst">Data Analyst</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
            </section>

            <!-- CARD 3: EXPERIENCE LEVEL -->
            <section class="setup-card" aria-label="Experience Level">
              <div class="setup-card-header">
                <div class="setup-card-header-left">
                  <div class="setup-card-icon icon-blue">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                      <line x1="16" y1="2" x2="16" y2="6"></line>
                      <line x1="8" y1="2" x2="8" y2="6"></line>
                      <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                  </div>
                  <h2 class="setup-card-title">Experience Level</h2>
                </div>
              </div>
              <div class="setup-grid-4" id="setup-exp-grid">
                <div class="opt-card setup-opt-card" data-val="Entry Level">
                  <div class="opt-check-bubble" aria-hidden="true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                  <strong class="soc-title">Entry Level</strong>
                  <span class="soc-sub">0–1 Years</span>
                </div>
                <div class="opt-card setup-opt-card active" data-val="Mid Level">
                  <div class="opt-check-bubble" aria-hidden="true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                  <strong class="soc-title">Mid Level</strong>
                  <span class="soc-sub">2–4 Years</span>
                </div>
                <div class="opt-card setup-opt-card" data-val="Senior">
                  <div class="opt-check-bubble" aria-hidden="true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                  <strong class="soc-title">Senior</strong>
                  <span class="soc-sub">5–8 Years</span>
                </div>
                <div class="opt-card setup-opt-card" data-val="Lead">
                  <div class="opt-check-bubble" aria-hidden="true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                  <strong class="soc-title">Lead</strong>
                  <span class="soc-sub">8+ Years</span>
                </div>
              </div>
            </section>

            <!-- CARD 4: INTERVIEW TYPE -->
            <section class="setup-card" aria-label="Interview Type">
              <div class="setup-card-header">
                <div class="setup-card-header-left">
                  <div class="setup-card-icon icon-blue">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                      <polygon points="23 7 16 12 23 17 23 7"></polygon>
                      <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
                    </svg>
                  </div>
                  <h2 class="setup-card-title">Interview Type</h2>
                </div>
              </div>
              <div class="type-card-grid" id="setup-type-grid">
                <div class="type-card setup-type-card" data-val="Technical Interview">
                  <div class="stc-badge-row">
                    <span class="stc-pill">Technical</span>
                    <div class="opt-check-bubble" aria-hidden="true">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                  </div>
                  <h3 class="stc-title">Technical Interview</h3>
                  <p class="stc-desc">Test technical knowledge, algorithms, and system design concepts.</p>
                </div>

                <div class="type-card setup-type-card" data-val="Behavioral Interview">
                  <div class="stc-badge-row">
                    <span class="stc-pill">Behavioral</span>
                    <div class="opt-check-bubble" aria-hidden="true">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                  </div>
                  <h3 class="stc-title">Behavioral Interview</h3>
                  <p class="stc-desc">Practice communication, STAR method, and workplace scenario questions.</p>
                </div>

                <div class="type-card setup-type-card active" data-val="Mixed Interview">
                  <div class="stc-badge-row">
                    <span class="stc-pill pill-recommended">Recommended</span>
                    <div class="opt-check-bubble" aria-hidden="true">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                  </div>
                  <h3 class="stc-title">Mixed Interview</h3>
                  <p class="stc-desc">Combine technical depth and behavioral communication evaluation.</p>
                </div>
              </div>
            </section>

            <!-- CARD 5: DIFFICULTY -->
            <section class="setup-card" aria-label="Difficulty">
              <div class="setup-card-header">
                <div class="setup-card-header-left">
                  <div class="setup-card-icon icon-blue">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="18" y1="20" x2="18" y2="10"></line>
                      <line x1="12" y1="20" x2="12" y2="4"></line>
                      <line x1="6" y1="20" x2="6" y2="14"></line>
                    </svg>
                  </div>
                  <h2 class="setup-card-title">Difficulty</h2>
                </div>
              </div>
              <div class="option-pill-grid trio" id="setup-diff-grid">
                <div class="opt-card setup-opt-card" data-val="Easy">
                  <strong class="soc-title">Easy</strong>
                  <div class="opt-check-bubble" aria-hidden="true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                </div>
                <div class="opt-card setup-opt-card active" data-val="Medium">
                  <strong class="soc-title">Medium</strong>
                  <div class="opt-check-bubble" aria-hidden="true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                </div>
                <div class="opt-card setup-opt-card" data-val="Hard">
                  <strong class="soc-title">Hard</strong>
                  <div class="opt-check-bubble" aria-hidden="true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                </div>
              </div>
            </section>

            <!-- CARD 6: NUMBER OF QUESTIONS -->
            <section class="setup-card" aria-label="Number of Questions">
              <div class="setup-card-header">
                <div class="setup-card-header-left">
                  <div class="setup-card-icon icon-blue">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                      <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                  </div>
                  <h2 class="setup-card-title">Number of Questions</h2>
                </div>
              </div>
              <div class="option-pill-grid trio" id="setup-qcount-grid">
                <div class="opt-card setup-opt-card active" data-val="5">
                  <strong class="soc-title">5 Questions</strong>
                  <span class="soc-sub">~15 mins</span>
                  <div class="opt-check-bubble" aria-hidden="true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                </div>
                <div class="opt-card setup-opt-card" data-val="10">
                  <strong class="soc-title">10 Questions</strong>
                  <span class="soc-sub">~30 mins</span>
                  <div class="opt-check-bubble" aria-hidden="true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                </div>
                <div class="opt-card setup-opt-card" data-val="15">
                  <strong class="soc-title">15 Questions</strong>
                  <span class="soc-sub">~45 mins</span>
                  <div class="opt-check-bubble" aria-hidden="true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </div>
                </div>
              </div>
            </section>

            <!-- CARD 7: INTERVIEW MODE -->
            <section class="setup-card" aria-label="Interview Mode">
              <div class="setup-card-header">
                <div class="setup-card-header-left">
                  <div class="setup-card-icon icon-blue">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                      <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                  </div>
                  <h2 class="setup-card-title">Interview Mode</h2>
                </div>
              </div>
              <div class="option-pill-grid duo setup-mode-grid" id="setup-mode-grid">
                <div class="opt-card setup-opt-card setup-mode-card active" data-val="Video Interview">
                  <div class="smc-header">
                    <div class="smc-title-group">
                      <svg class="smc-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="23 7 16 12 23 17 23 7"></polygon>
                        <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
                      </svg>
                      <strong class="soc-title">Video Interview</strong>
                    </div>
                    <div class="opt-check-bubble" aria-hidden="true">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                  </div>
                  <span class="soc-sub">Analyzes visual presence &amp; speech</span>
                </div>

                <div class="opt-card setup-opt-card setup-mode-card" data-val="Audio Interview">
                  <div class="smc-header">
                    <div class="smc-title-group">
                      <svg class="smc-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                        <path d="M19 10v1a7 7 0 0 1-14 0v-1"></path>
                        <line x1="12" y1="19" x2="12" y2="23"></line>
                        <line x1="8" y1="23" x2="16" y2="23"></line>
                      </svg>
                      <strong class="soc-title">Audio Interview</strong>
                    </div>
                    <div class="opt-check-bubble" aria-hidden="true">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                  </div>
                  <span class="soc-sub">Speech &amp; transcript evaluation</span>
                </div>
              </div>
            </section>

          </div>

          <!-- RIGHT COLUMN: STICKY INTERVIEW SUMMARY & 3D MICROPHONE -->
          <aside class="setup-summary-col">
            <!-- STICKY SUMMARY CARD -->
            <div class="summary-sticky-card">
              <div class="ssc-header">
                <div class="ssc-title-group">
                  <div class="ssc-icon-wrap">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1677FF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="18" y1="20" x2="18" y2="10"></line>
                      <line x1="12" y1="20" x2="12" y2="4"></line>
                      <line x1="6" y1="20" x2="6" y2="14"></line>
                    </svg>
                  </div>
                  <h3 class="ssc-title">Interview Summary</h3>
                </div>
                <span class="ssc-chip">LIVE CONFIG</span>
              </div>

              <div class="ssc-body-rows">
                <div class="ssc-row">
                  <span class="ssc-row-label">
                    <span class="ssc-row-icon icon-purple">💼</span>
                    <span>Target Role</span>
                  </span>
                  <span class="ssc-val" id="sum-role">Backend Developer</span>
                </div>
                <div class="ssc-row">
                  <span class="ssc-row-label">
                    <span class="ssc-row-icon icon-yellow">⭐</span>
                    <span>Experience</span>
                  </span>
                  <span class="ssc-val" id="sum-exp">Mid Level</span>
                </div>
                <div class="ssc-row">
                  <span class="ssc-row-label">
                    <span class="ssc-row-icon icon-blue">🌐</span>
                    <span>Type</span>
                  </span>
                  <span class="ssc-val" id="sum-type">Mixed Interview</span>
                </div>
                <div class="ssc-row">
                  <span class="ssc-row-label">
                    <span class="ssc-row-icon icon-indigo">⚡</span>
                    <span>Difficulty</span>
                  </span>
                  <span class="ssc-val" id="sum-diff">Medium</span>
                </div>
                <div class="ssc-row">
                  <span class="ssc-row-label">
                    <span class="ssc-row-icon icon-cyan">❓</span>
                    <span>Questions</span>
                  </span>
                  <span class="ssc-val" id="sum-count">5 Questions</span>
                </div>
                <div class="ssc-row">
                  <span class="ssc-row-label">
                    <span class="ssc-row-icon icon-teal">▶</span>
                    <span>Mode</span>
                  </span>
                  <span class="ssc-val" id="sum-mode">Video Interview</span>
                </div>
                <div class="ssc-row">
                  <span class="ssc-row-label">
                    <span class="ssc-row-icon icon-blue">📄</span>
                    <span>Resume</span>
                  </span>
                  <div class="sum-resume-val-wrap">
                    <span class="ssc-val res-truncate" id="sum-resume">Jake_s_Resume__A...</span>
                    <button type="button" class="btn-view-resume-eye" title="View Resume Preview" id="btn-view-resume-eye">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#53658F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- PERSONALIZATION INFO CALLOUT -->
              <div class="personalized-info-box">
                <span class="pib-sparkle">✨</span>
                <div class="pib-text">
                  <strong>Questions are personalized for you</strong>
                  <p>Your questions will be generated based on your selected role, experience level, and interview type.</p>
                </div>
              </div>

              <!-- CONTINUE BUTTON -->
              <button class="btn btn-primary btn-block btn-lg btn-gradient-continue" id="btn-continue-device-check">
                <span>Continue to Device Check →</span>
              </button>
            </div>

            <!-- 3D STUDIO MICROPHONE ARTWORK STAGE -->
            <div class="setup-mic-stage">
              <div class="setup-mic-glow"></div>
              <img src="assets/illustrations/setup_3d_microphone_transparent.png"
                   alt="3D Studio Microphone with Analytics Badges"
                   class="setup-mic-img"
                   loading="lazy" />
            </div>
          </aside>

        </main>

        <!-- FLOATING BOTTOM FOOTER -->
        <footer class="landing-footer setup-footer">
          <div class="landing-footer-main">
            <div class="footer-brand-col">
              <div class="footer-brand">
                <div class="footer-logo-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
                  </svg>
                </div>
                <span class="footer-brand-name">AI Interview Analyzer</span>
              </div>
              <p class="footer-tagline">AI-powered interview practice and feedback.</p>
            </div>

            <div class="footer-copyright-col">
              <span class="footer-copyright">&copy; 2026 AI Interview Analyzer. All rights reserved.</span>
            </div>

            <div class="footer-nav-col">
              <div class="footer-nav-group">
                <span class="footer-nav-title">PRODUCT</span>
                <div class="footer-links">
                  <a href="#how-it-works">How It Works</a>
                  <a href="#features">Features</a>
                  <a href="#login" id="setup-footer-login-link">Login</a>
                </div>
              </div>
              <div class="footer-nav-group">
                <span class="footer-nav-title">LEGAL</span>
                <div class="footer-links">
                  <a href="#privacy">Privacy</a>
                  <a href="#terms">Terms</a>
                </div>
              </div>
            </div>
          </div>
        </footer>

      </div>
    </div>'''

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '    <div class="view-panel" id="view-interview-setup">'
end_marker = '    <!-- VIEW 6: CAMERA & MICROPHONE DEVICE CHECK WORKSPACE (PHASE 4) -->'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1:
    print('ERROR: start_marker not found')
    sys.exit(1)
if end_idx == -1:
    print('ERROR: end_marker not found')
    sys.exit(1)

updated_content = content[:start_idx] + new_html + '\n\n    ' + content[end_idx:]

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print('SUCCESS: frontend/index.html updated successfully!')


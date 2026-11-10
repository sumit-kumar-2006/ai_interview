import sys

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update #auth-nav to include Analytics button if not present
if 'id="nav-analytics-btn"' not in content:
    old_nav = '<button class="landing-nav-item nav-btn-link" id="nav-profile-btn">Profile</button>'
    new_nav = '<button class="landing-nav-item nav-btn-link" id="nav-profile-btn">Profile</button>\n        <button class="landing-nav-item nav-btn-link" id="nav-analytics-btn">Analytics</button>'
    assert old_nav in content, "Could not find profile button in auth nav"
    content = content.replace(old_nav, new_nav, 1)

# 2. Build new practice view markup up to #completion-card
new_practice_html = '''    <div class="view-panel" id="view-practice">
      <!-- Background Ambient Lighting Accents -->
      <div class="interview-ambient-glow glow-top-left"></div>
      <div class="interview-ambient-glow glow-bottom-right"></div>

      <div class="interview-workspace-wrapper">

        <!-- PRE-INTERVIEW INITIALIZATION OVERLAY (INSIDE SAME ROOM) -->
        <div class="interview-init-overlay hidden" id="interview-init-overlay">
          <div class="init-modal-card">
            <div class="init-spinner-orbit">
              <div class="spinner-core"></div>
            </div>
            <h2 class="init-title">PREPARING YOUR INTERVIEW</h2>
            <p class="init-subtitle">Setting up your AI interview room environment...</p>

            <div class="init-checklist">
              <div class="init-check-item" id="init-item-cam">
                <span class="init-icon-status">⏳</span>
                <span class="init-label">Connecting camera stream...</span>
              </div>
              <div class="init-check-item" id="init-item-mic">
                <span class="init-icon-status">⏳</span>
                <span class="init-label">Checking microphone access...</span>
              </div>
              <div class="init-check-item" id="init-item-face">
                <span class="init-icon-status">⏳</span>
                <span class="init-label">Initializing MediaPipe face tracking...</span>
              </div>
              <div class="init-check-item" id="init-item-ai">
                <span class="init-icon-status">⏳</span>
                <span class="init-label">Loading personalized AI questions...</span>
              </div>
            </div>

            <!-- PROMINENT HEADPHONE RECOMMENDATION NOTICE -->
            <div class="headphone-notice-card mt-3">
              <span class="hnc-icon">🎧</span>
              <div class="hnc-text">
                <strong>For the Best AI Interview Experience:</strong>
                <span>Please wear <strong>headphones or earphones</strong> with a microphone. This eliminates acoustic feedback, echo, and ensures 100% accurate Whisper speech recognition.</span>
              </div>
            </div>

            <div class="init-status-footer">
              <p class="init-footer-msg" id="init-status-msg">Please allow camera and microphone permissions when prompted.</p>
              <div class="init-retry-actions hidden" id="init-retry-actions">
                <button class="btn btn-primary btn-sm" id="btn-init-retry">Grant Permissions &amp; Retry</button>
                <button class="btn btn-secondary btn-sm" id="btn-init-skip">Proceed with Available Hardware</button>
              </div>
            </div>
          </div>
        </div>

        <!-- QUESTION PROGRESS HEADER -->
        <header class="interview-progress-header" id="interview-progress-header">
          <div class="iph-left">
            <button class="btn-back-link" id="btn-interview-back-questions" type="button" aria-label="Back to Questions">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              <span>Back to Questions</span>
            </button>
          </div>

          <div class="iph-center">
            <span class="iph-counter-text" id="topbar-q-counter">Question 1 of 5</span>
            <div class="iph-progress-track">
              <div class="iph-progress-fill" id="topbar-progress-fill" style="width: 20%;"></div>
            </div>
          </div>

          <div class="iph-right">
            <span class="iph-chip iph-chip-headphones" id="chip-headphones" title="Headphones recommended for best voice clarity">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"></path><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"></path></svg>
              <span>Headphones Recommended</span>
            </span>
            <span class="iph-chip iph-chip-live" id="chip-live-status">
              <span class="live-pulsing-dot"></span>
              <span>LIVE</span>
            </span>
            <div class="iph-chip iph-chip-timer">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
              <span id="topbar-session-timer">00:37</span>
            </div>
          </div>
        </header>

        <!-- MAIN TWO-COLUMN STAGE (54% Left Column, 44% Right Column) -->
        <main class="interview-main-stage" id="interview-main-stage">

          <!-- LEFT COLUMN: AI QUESTION CARD & LIVE TRANSCRIPTION CARD -->
          <section class="interview-qa-col">

            <!-- QUESTION CARD -->
            <div class="card question-card" id="question-card">
              <!-- Card Top Row Badges -->
              <div class="question-header">
                <div class="qh-left">
                  <div class="interviewer-tag">
                    <span class="interviewer-avatar-circle">AI</span>
                    <span class="interviewer-label">AI INTERVIEWER</span>
                  </div>
                  <span class="qh-track-chip" id="qh-track-chip">&lt;/&gt; FRONTEND &amp; WEB DEVELOPMENT TRACK</span>
                </div>
                <span class="q-label-tag" id="question-number-badge">QUESTION 01 OF 05</span>
              </div>

              <!-- Question Content Row with 3D Illustration & Bold Navy Typography -->
              <div class="question-body-row">
                <div class="question-3d-visual-wrap">
                  <img src="assets/illustrations/interview_3d_code_speech_bubble_transparent.png"
                       alt="AI Interview 3D Code Symbol"
                       class="question-3d-bubble-img" />
                </div>
                <div class="question-text-wrap">
                  <h1 class="question-title-text" id="question-text">
                    "Explain what a generator function is in JavaScript."
                  </h1>
                  <p class="question-subhint" id="question-subhint">
                    Take your time. Explain clearly and give examples where relevant.
                  </p>
                </div>
              </div>

              <!-- LIVE REAL-TIME TRANSCRIPT CARD (DARK NAVY) -->
              <div class="live-transcript-panel" id="live-transcript-panel">
                <div class="ltp-header">
                  <div class="ltp-title-group">
                    <svg class="ltp-mic-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#258BFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                      <path d="M19 10v1a7 7 0 0 1-14 0v-1"></path>
                      <line x1="12" y1="19" x2="12" y2="23"></line>
                      <line x1="8" y1="23" x2="16" y2="23"></line>
                    </svg>
                    <span class="ltp-title">YOUR ANSWER (LIVE TRANSCRIPT)</span>
                  </div>
                  <div class="ltp-status-pill" id="ltp-live-status">
                    <span class="ltp-pulse-dot"></span>
                    <span id="ltp-status-text">Listening...</span>
                  </div>
                </div>

                <div class="ltp-body-row">
                  <!-- Animated Waveform Bars Driven by Real AudioContext Input -->
                  <div class="live-audio-waveform-bars" id="live-waveform-bars" aria-label="Audio level visualizer">
                    <canvas id="transcription-waveform-canvas" width="80" height="42" class="transcription-canvas"></canvas>
                  </div>
                  <!-- Real-time Speech Transcription Stream -->
                  <div class="ltp-scroll-box" id="live-transcript-box">
                    <p class="ltp-placeholder" id="ltp-placeholder">Click "Start Answer" below and speak into your microphone. Your spoken response will transcribe here in real time...</p>
                    <p class="ltp-content hidden" id="ltp-text"></p>
                  </div>
                </div>
              </div>

              <!-- Question Meta Badges Below Transcription -->
              <div class="question-footer-badges">
                <span class="q-meta-pill pill-purple" id="question-difficulty">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                  <span>Medium</span>
                </span>
                <span class="q-meta-pill pill-blue" id="question-category">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
                  <span>Frontend &amp; Web Development</span>
                </span>
                <span class="q-meta-pill pill-green" id="question-ans-state">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  <span>Ready to answer</span>
                </span>
              </div>
            </div>

            <!-- MANDATORY TRANSCRIPT REVIEW & RETRY CARD -->
            <div class="card transcript-review-card hidden" id="transcript-review-card">
              <div class="trc-header">
                <div class="trc-title-block">
                  <span class="badge badge-primary-subtle">STAGE 1 OF 2 · REVIEW YOUR ANSWER</span>
                  <h3 class="trc-title">Audio Playback &amp; Spoken Transcript</h3>
                </div>
                <div class="trc-audio-wrap">
                  <audio id="audio-playback-preview" controls class="audio-playback-player"></audio>
                  <span id="recorded-duration-text" class="recorded-duration-chip" style="font-size:0.85rem; color:#888; margin-top:4px; display:inline-block;">Duration: 00:00</span>
                </div>
              </div>

              <div class="trc-body">
                <div class="trc-prompt-bar">
                  <span class="trc-instruction">
                    Listen to your recorded audio. If Whisper speech recognition made a spelling or technical term error, edit it directly below before submitting for technical scoring.
                  </span>
                </div>

                <div class="trc-editor-area">
                  <div class="trc-editor-header">
                    <label for="transcript-edit-input" class="trc-editor-label">Recognized Answer (Editable):</label>
                    <span class="trc-word-count" id="trc-word-count">0 words</span>
                  </div>
                  <textarea id="transcript-edit-input" class="form-textarea trc-textarea" rows="4" placeholder="Your transcribed answer will appear here for review..."></textarea>
                </div>

                <div class="trc-telemetry-row">
                  <span class="telemetry-label">Communication Metrics (Analyzed Separately):</span>
                  <div class="telemetry-badges-group" id="trc-telemetry-badges">
                    <span class="badge-telemetry" id="trc-badge-wpm">Pace: -- WPM</span>
                    <span class="badge-telemetry" id="trc-badge-fillers">Fillers: 0</span>
                    <span class="badge-telemetry" id="trc-badge-fluency">Fluency: --</span>
                  </div>
                </div>
              </div>

              <div class="trc-actions-footer">
                <button type="button" class="btn btn-secondary btn-lg" id="btn-review-rerecord">
                  <span>🔄 Re-record Answer</span>
                </button>
                <button type="button" class="btn btn-outline btn-lg" id="btn-review-edit">
                  <span>✏️ Edit Transcript</span>
                </button>
                <button type="button" class="btn btn-primary btn-lg" id="btn-review-submit">
                  <span>🚀 Submit Answer →</span>
                </button>
              </div>
            </div>

            <!-- PER-QUESTION EVALUATION RESULT CARD -->
            <div class="card question-complete-card hidden" id="question-result-card">
              <div class="qrc-header">
                <div class="qrc-title-block">
                  <span class="badge badge-success">✓ EVALUATION COMPLETE</span>
                  <h3 class="qrc-title" id="qrc-heading">Answer Evaluation</h3>
                </div>
                <div class="qrc-score-badge">
                  <span class="qrc-score-lbl">Technical Score</span>
                  <span class="qrc-score-num"><strong id="per-q-score">0</strong> / 100</span>
                </div>
              </div>

              <div class="qrc-body">
                <div class="qrc-section">
                  <span class="qrc-sec-title">Final Submitted Answer</span>
                  <div class="qrc-transcript-scroll" id="per-q-transcript-box">
                    <p class="qrc-transcript-text" id="per-q-transcript">"..."</p>
                  </div>
                </div>

                <div class="qrc-section" id="per-q-concepts-section">
                  <span class="qrc-sec-title">Technical Concepts Assessment</span>
                  <div class="qrc-concepts-grid">
                    <div class="concept-group-col">
                      <span class="concept-group-title text-success">✓ Required Concepts Mastered:</span>
                      <div class="concept-chips-wrap" id="per-q-concepts-mastered">
                        <span class="badge badge-success-subtle">Core principles addressed</span>
                      </div>
                    </div>
                    <div class="concept-group-col">
                      <span class="concept-group-title text-warning">✗ Missing / Incomplete Concepts:</span>
                      <div class="concept-chips-wrap" id="per-q-concepts-missing">
                        <span class="badge badge-warning-subtle">None missing</span>
                      </div>
                    </div>
                  </div>
                  <div class="concept-misconceptions-wrap hidden" id="per-q-misconceptions-wrap">
                    <span class="concept-group-title text-danger">⚠️ Identified Misconceptions:</span>
                    <div class="concept-chips-wrap" id="per-q-misconceptions-list"></div>
                  </div>
                </div>

                <div class="qrc-section">
                  <span class="qrc-sec-title">Evaluation Explanation &amp; Rubric Analysis</span>
                  <p class="qrc-explanation-text" id="per-q-explanation">
                    Answer evaluated against the question specification.
                  </p>
                </div>

                <div class="qrc-section">
                  <span class="qrc-sec-title">Strengths &amp; Actionable Improvements</span>
                  <ul class="qrc-feedback-list" id="per-q-feedback-list"></ul>
                </div>

                <div class="qrc-section qrc-comm-section">
                  <span class="qrc-sec-title">Communication Fluency (Reported Separately)</span>
                  <div class="qrc-comm-badges" id="per-q-comm-badges">
                    <span class="comm-pill" id="per-q-comm-wpm">Pace: -- WPM</span>
                    <span class="comm-pill" id="per-q-comm-fillers">Fillers: 0</span>
                    <span class="comm-pill" id="per-q-comm-fluency">Fluency: --</span>
                  </div>
                </div>
              </div>

              <div class="qrc-footer">
                <button class="btn btn-secondary btn-lg" id="btn-per-q-retry">
                  <span>🔄 Re-record Answer</span>
                </button>
                <button class="btn btn-primary btn-lg" id="btn-per-q-next">
                  <span>Continue to Next Question →</span>
                </button>
              </div>
            </div>

          </section>

          <!-- RIGHT COLUMN: LIVE WEBCAM & ATTENTION ANALYSIS -->
          <section class="interview-cam-col">
            <div class="webcam-monitor-card" id="webcam-monitor-card">

              <!-- Top Bar inside Camera Card -->
              <div class="webcam-card-topbar">
                <div class="wct-left">
                  <div class="cam-badge cam-badge-live">
                    <span class="cam-dot-red"></span>
                    <span>LIVE FEED</span>
                  </div>
                  <div class="cam-badge cam-badge-active">
                    <span class="cam-dot-green"></span>
                    <span>ACTIVE</span>
                  </div>
                </div>
                <div class="wct-right">
                  <label for="interview-camera-dropdown" class="cam-switch-label" title="Switch Video Device">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                      <circle cx="12" cy="13" r="4"></circle>
                    </svg>
                    <span>Camera:</span>
                  </label>
                  <select id="interview-camera-dropdown" class="cam-select-input-sm" aria-label="Select Camera Device">
                    <option value="">Laptop Camera (Chicony U... ⌵</option>
                  </select>
                </div>
              </div>

              <!-- Camera Viewport Container with Mirroring and Real Overlays -->
              <div class="camera-viewport-container">
                <video id="live-camera-video" autoplay playsinline muted class="camera-stream-video"></video>

                <!-- Electric Blue Framing Guide Corners -->
                <div class="camera-framing-guide" aria-hidden="true">
                  <div class="guide-corner top-left"></div>
                  <div class="guide-corner top-right"></div>
                  <div class="guide-corner bottom-left"></div>
                  <div class="guide-corner bottom-right"></div>
                </div>

                <!-- Floating Center Attention Alert Banner -->
                <div class="face-detection-alert-banner hidden" id="face-alert-banner">
                  <span class="alert-icon">⚠️</span>
                  <span class="alert-msg">Please look at the camera.</span>
                </div>

                <!-- Bottom Telemetry HUD Overlays -->
                <div class="video-telemetry-hud" id="video-telemetry-hud">
                  <div class="hud-pill hud-face" id="video-face-tag">
                    <span class="hud-dot-blue"></span>
                    <span id="video-face-text">Face Detected • Eyes: Away</span>
                  </div>
                  <div class="hud-pill hud-pose" id="video-pose-tag">
                    <span class="hud-dot-green"></span>
                    <span id="video-pose-text">Head: RIGHT</span>
                  </div>
                </div>

                <!-- Camera Error Overlay -->
                <div class="camera-error-overlay hidden" id="camera-error-overlay">
                  <div class="error-icon">📷</div>
                  <h4 class="error-title">Camera Access Required</h4>
                  <p class="error-msg" id="camera-error-msg">Camera access is required for live presence analysis.</p>
                  <button class="btn btn-primary btn-sm btn-enable-cam" id="btn-enable-camera">Enable Camera</button>
                </div>
              </div>

            </div>
          </section>

        </main>

        <!-- FLOATING BOTTOM INTERVIEW CONTROL BAR -->
        <footer class="interview-bottombar" id="interview-bottombar">
          <!-- Left: State Indicator -->
          <div class="ibb-left">
            <div class="answer-state-bubble" id="answer-state-indicator">
              <div class="asi-icon-wrap">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#792FFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                </svg>
              </div>
              <span class="asi-label" id="asi-state-text">Ready to answer</span>
              <span class="asi-live-dot"></span>
            </div>
          </div>

          <!-- Center: Dynamic CTA Button -->
          <div class="ibb-center">
            <div class="action-btn-group" id="ctrl-state-idle">
              <button class="btn-gradient-start-answer" id="btn-start-record-action" type="button">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                  <path d="M19 10v1a7 7 0 0 1-14 0v-1"></path>
                  <line x1="12" y1="19" x2="12" y2="23"></line>
                  <line x1="8" y1="23" x2="16" y2="23"></line>
                </svg>
                <span>Start Answer →</span>
              </button>
              <button class="hidden" id="btn-start-mic"></button>
            </div>

            <div class="action-btn-group hidden" id="ctrl-state-recording">
              <button class="btn-danger-stop-answer" id="btn-stop-record-action" type="button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><rect x="4" y="4" width="16" height="16" rx="2"></rect></svg>
                <span>Finish Answer</span>
              </button>
              <button class="hidden" id="btn-pause-recording"></button>
            </div>

            <div class="action-btn-group hidden" id="ctrl-state-processing">
              <div class="processing-inline-badge">
                <div class="spinner-ring sm"></div>
                <div class="pib-text">
                  <span class="pib-title">Analyzing your answer...</span>
                  <span class="pib-sub" id="pib-step-label">Whisper transcription &amp; AI evaluation in progress</span>
                </div>
              </div>
            </div>

            <div class="action-btn-group hidden" id="ctrl-state-review">
              <button class="btn btn-secondary btn-lg" id="btn-ctrl-review-rerecord" type="button">
                <span>🔄 Re-record</span>
              </button>
              <button class="btn-gradient-start-answer" id="btn-ctrl-review-submit" type="button">
                <span>Submit Answer →</span>
              </button>
            </div>

            <div class="action-btn-group hidden" id="ctrl-state-saved">
              <button class="btn-gradient-start-answer" id="btn-next-question-action" type="button">
                <span>Next Question →</span>
              </button>
            </div>

            <div class="action-btn-group hidden" id="ctrl-state-error">
              <span class="text-danger font-sm mr-2" id="ctrl-error-text">No speech detected.</span>
              <button class="btn btn-secondary btn-sm" id="btn-ctrl-retry" type="button">Try Again</button>
            </div>
          </div>

          <!-- Right: Timer, Media Toggles, Fullscreen & End Interview -->
          <div class="ibb-right">
            <div class="answer-timer-box" id="answer-timer-box">
              <span class="atb-label">ANSWER TIME</span>
              <span class="atb-time" id="recording-timer">00:00</span>
            </div>

            <div class="ibb-util-group">
              <button class="btn-circle-util" id="btn-toggle-cam" title="Toggle Camera" type="button" aria-label="Toggle Camera">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="23 7 16 12 23 17 23 7"></polygon>
                  <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
                </svg>
              </button>
              <button class="btn-circle-util" id="btn-toggle-mic" title="Toggle Microphone" type="button" aria-label="Toggle Microphone">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                  <path d="M19 10v1a7 7 0 0 1-14 0v-1"></path>
                  <line x1="12" y1="19" x2="12" y2="23"></line>
                  <line x1="8" y1="23" x2="16" y2="23"></line>
                </svg>
              </button>
              <button class="btn-circle-util" id="btn-toggle-fullscreen" title="Toggle Fullscreen" type="button" aria-label="Toggle Fullscreen">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
                </svg>
              </button>
              <button class="btn-pill-end-interview" id="btn-exit-interview" title="End Interview" type="button">
                <span class="end-icon-square"></span>
                <span>End Interview</span>
              </button>
            </div>
          </div>
        </footer>

        <!-- HIDDEN BACKWARD-COMPATIBLE CARDS (Required for background evaluation metrics) -->
        <div class="hidden" id="results-card" style="display: none;">
          <span id="score-predicted-val">0</span>
          <span id="score-grade-badge"></span>
          <span id="metric-ref-sim"></span>
          <span id="metric-q-sim"></span>
          <span id="metric-concept-cov"></span>
          <span id="metric-completeness"></span>
          <span id="metric-ans-len"></span>
          <span id="stat-word-count"></span>
          <div id="bar-ref-sim"></div>
          <div id="bar-q-sim"></div>
          <div id="bar-concept-cov"></div>
          <div id="bar-completeness"></div>
          <span id="gauge-fill-circle"></span>
          <span id="transcript-text"></span>
          <div id="insights-list"></div>
          <div id="filler-breakdown-row"></div>
          <span id="comm-status-badge"></span>
          <span id="comm-val-time"></span>
          <span id="comm-val-wpm"></span>
          <span id="comm-val-fillers"></span>
          <span id="comm-val-fluency"></span>
          <span id="comm-val-conciseness"></span>
          <span id="comm-val-overall"></span>
          <button id="btn-copy-transcript"></button>
          <button id="btn-retry-question"></button>
          <button id="btn-next-question"></button>
          <button id="btn-prev-question"></button>
          <button id="btn-next-question-header"></button>
          <div id="state-idle" class="hidden"></div>
          <div id="state-recording" class="hidden"></div>
          <div id="state-saved" class="hidden"></div>
          <div id="state-recorded" class="hidden"></div>
          <div id="state-processing" class="hidden"></div>
          <div id="state-error" class="hidden"></div>
          <button id="btn-rerecord" class="hidden"></button>
          <button id="btn-submit-answer" class="hidden"></button>
          <button id="btn-error-retry" class="hidden"></button>
          <span id="error-message-text" class="hidden"></span>
          <span id="saved-state-hint" class="hidden"></span>
          <span id="proc-title" class="hidden"></span>
          <span id="proc-step-label" class="hidden"></span>
          <div id="rec-warning-box" class="hidden">
            <span id="warning-box-title"></span>
            <span id="warning-box-desc"></span>
          </div>
        </div>
'''

start_marker = '    <div class="view-panel" id="view-practice">'
end_marker = '        <!-- POST-INTERVIEW COMPREHENSIVE FINAL REPORT -->'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

assert start_idx != -1, "start_marker not found"
assert end_idx != -1, "end_marker not found"

updated_content = content[:start_idx] + new_practice_html + '\n        ' + content[end_idx:]

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("SUCCESS: frontend/index.html updated for live interview room!")

import re

landing_html = """    <!-- VIEW 0: PUBLIC LANDING PAGE -->
    <div class="view-panel active" id="view-landing">
      <div class="landing-page-wrapper" id="start-interview-card">

        <!-- 2. HERO SECTION -->
        <section class="landing-hero-section">
          <div class="hero-grid">
            <!-- Left Hero Content -->
            <div class="hero-left">
              <div class="hero-eyebrow">
                <span class="eyebrow-plus">+</span>
                <span>AI-POWERED INTERVIEW PRACTICE</span>
              </div>
              <h1 class="hero-title">
                Practice smarter.<br>
                <span class="text-gradient-hero">Interview better.</span>
              </h1>
              <p class="hero-subtitle">
                AI-powered interview practice that evaluates your answers, communication, and interview presence — then
                turns your performance into actionable feedback.
              </p>

              <div class="hero-cta-buttons">
                <button class="btn btn-primary btn-hero-gradient" id="btn-start-interview">
                  <span>Start Free Interview</span>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                  </svg>
                </button>
                <a href="#how-it-works" class="btn btn-hero-white" id="btn-view-demo">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                  </svg>
                  <span>See How It Works</span>
                </a>
              </div>

              <!-- Trust / Product Indicators -->
              <div class="hero-trust-indicators">
                <span class="trust-indicator-item">
                  <svg class="check-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16B981" stroke-width="3">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  AI-powered evaluation
                </span>
                <span class="trust-indicator-item">
                  <svg class="check-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16B981" stroke-width="3">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  Real-time analysis
                </span>
                <span class="trust-indicator-item">
                  <svg class="check-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16B981" stroke-width="3">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  Personalized feedback
                </span>
              </div>
            </div>

            <!-- Right Hero Composition -->
            <div class="hero-right">
              <div class="hero-visual-wrapper">
                <div class="hero-glow-backdrop"></div>
                <img src="assets/illustrations/ref_hero_composition.png" alt="Candidate AI Interview Analytics Scene" class="hero-composition-img">
              </div>
            </div>
          </div>
        </section>

        <!-- 3. FOUR FEATURE CARDS STRIP -->
        <section class="four-features-section">
          <div class="four-features-grid">
            <!-- Card 1 -->
            <div class="feature-capsule-card">
              <div class="feat-capsule-icon icon-blue">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                </svg>
              </div>
              <h4 class="feat-capsule-title">AI-Powered Evaluation</h4>
              <p class="feat-capsule-desc">Evaluate answer quality and relevance.</p>
              <button class="feat-circle-arrow" aria-label="Learn more about AI evaluation">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </button>
            </div>

            <!-- Card 2 -->
            <div class="feature-capsule-card">
              <div class="feat-capsule-icon icon-purple">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                  <line x1="12" y1="19" x2="12" y2="23"></line>
                </svg>
              </div>
              <h4 class="feat-capsule-title">Communication Analysis</h4>
              <p class="feat-capsule-desc">Analyze speaking pattern, clarity and delivery.</p>
              <button class="feat-circle-arrow" aria-label="Learn more about communication analysis">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </button>
            </div>

            <!-- Card 3 -->
            <div class="feature-capsule-card">
              <div class="feat-capsule-icon icon-cyan">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </div>
              <h4 class="feat-capsule-title">Visual Presence</h4>
              <p class="feat-capsule-desc">Analyze interview presence and attention.</p>
              <button class="feat-circle-arrow" aria-label="Learn more about visual presence">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </button>
            </div>

            <!-- Card 4 -->
            <div class="feature-capsule-card">
              <div class="feat-capsule-icon icon-purple">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
              <h4 class="feat-capsule-title">Personalized Interviews</h4>
              <p class="feat-capsule-desc">Generate interview practice based on the candidate's role.</p>
              <button class="feat-circle-arrow" aria-label="Learn more about personalized interviews">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </button>
            </div>
          </div>
        </section>

        <!-- 4. HOW IT WORKS SECTION -->
        <section class="landing-section-block" id="how-it-works">
          <div class="section-center-header">
            <span class="eyebrow-caps">HOW IT WORKS</span>
            <h2 class="section-heading">How your AI interview works</h2>
          </div>
          <div class="steps-connected-row">
            <!-- Step 1 -->
            <div class="step-connected-card">
              <span class="step-watermark-num">01</span>
              <div class="step-icon-bubble bubble-blue">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                  <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                </svg>
              </div>
              <h3 class="step-connected-title">Choose your role</h3>
              <p class="step-connected-desc">Select the role you want to practice for.</p>
            </div>

            <!-- Connector 1 -->
            <div class="step-arrow-connector">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#258BFF" stroke-width="2.5">
                <line x1="4" y1="12" x2="20" y2="12"></line>
                <polyline points="14 6 20 12 14 18"></polyline>
              </svg>
            </div>

            <!-- Step 2 -->
            <div class="step-connected-card">
              <span class="step-watermark-num">02</span>
              <div class="step-icon-bubble bubble-purple">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                  <line x1="12" y1="19" x2="12" y2="23"></line>
                </svg>
              </div>
              <h3 class="step-connected-title">Complete the interview</h3>
              <p class="step-connected-desc">Answer realistic questions while the AI analyzes your performance.</p>
            </div>

            <!-- Connector 2 -->
            <div class="step-arrow-connector">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#258BFF" stroke-width="2.5">
                <line x1="4" y1="12" x2="20" y2="12"></line>
                <polyline points="14 6 20 12 14 18"></polyline>
              </svg>
            </div>

            <!-- Step 3 -->
            <div class="step-connected-card">
              <span class="step-watermark-num">03</span>
              <div class="step-icon-bubble bubble-blue">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="20" x2="18" y2="10"></line>
                  <line x1="12" y1="20" x2="12" y2="4"></line>
                  <line x1="6" y1="20" x2="6" y2="14"></line>
                </svg>
              </div>
              <h3 class="step-connected-title">Get your performance report</h3>
              <p class="step-connected-desc">Receive structured feedback and actionable insights.</p>
            </div>
          </div>
        </section>

        <!-- 5. FEATURES SECTION -->
        <section class="landing-section-block" id="features">
          <div class="section-center-header">
            <span class="eyebrow-caps">FEATURES</span>
            <h2 class="section-heading">Everything you need to practice with confidence</h2>
          </div>
          <div class="features-two-by-two-grid">
            <div class="feat-row-card">
              <div class="feat-circle-icon icon-blue">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2a8 8 0 0 0-8 8c0 3.5 2 6 5 7.5V20a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1v-2.5c3-1.5 5-4 5-7.5a8 8 0 0 0-8-8z"></path>
                  <line x1="9" y1="17" x2="15" y2="17"></line>
                </svg>
              </div>
              <div class="feat-row-text">
                <h3 class="feat-row-title">Answer Intelligence</h3>
                <p class="feat-row-desc">Evaluate the clarity, depth and relevance of your answers.</p>
              </div>
            </div>

            <div class="feat-row-card">
              <div class="feat-circle-icon icon-purple">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
              </div>
              <div class="feat-row-text">
                <h3 class="feat-row-title">Communication Analysis</h3>
                <p class="feat-row-desc">Analyze speaking pace, clarity, filler words and delivery.</p>
              </div>
            </div>

            <div class="feat-row-card">
              <div class="feat-circle-icon icon-cyan">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </div>
              <div class="feat-row-text">
                <h3 class="feat-row-title">Visual Presence</h3>
                <p class="feat-row-desc">Evaluate interview presence and visual attention.</p>
              </div>
            </div>

            <div class="feat-row-card">
              <div class="feat-circle-icon icon-purple">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
              <div class="feat-row-text">
                <h3 class="feat-row-title">Personalized Questions</h3>
                <p class="feat-row-desc">Generate relevant questions based on the candidate's role and experience.</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 6. PERFORMANCE REPORT PREVIEW (MATCHING REFERENCE DESIGN) -->
        <section class="landing-section-block" id="performance-report">
          <div class="report-preview-master-wrapper">
            <!-- Left & Middle: The White Interview Report Card -->
            <div class="report-left-dashboard-card">
              <!-- Card Header -->
              <div class="rld-header-row">
                <div class="rld-title-group">
                  <span class="rld-badge-pill">INTERVIEW REPORT</span>
                  <h3 class="rld-role-heading" id="landing-report-role">Frontend Engineer — Round 1</h3>
                </div>
                <div class="rld-status-pill">
                  <span>COMPLETED</span>
                </div>
              </div>

              <!-- Card Main Content -->
              <div class="rld-content-grid">
                <!-- Sub-col 1: Gauge & Metric Bars -->
                <div class="rld-score-col">
                  <div class="rld-gauge-container">
                    <svg class="rld-gauge-svg" width="110" height="110" viewBox="0 0 120 120">
                      <circle class="rld-gauge-bg" cx="60" cy="60" r="50" fill="none" stroke="#EBF1FA" stroke-width="10"></circle>
                      <circle class="rld-gauge-prog" id="landing-report-circle-fill" cx="60" cy="60" r="50" fill="none" stroke="#258BFF" stroke-width="10" stroke-dasharray="314" stroke-dashoffset="270" stroke-linecap="round"></circle>
                    </svg>
                    <div class="rld-gauge-text">
                      <span class="rld-gauge-val" id="landing-report-score-num">14<span class="rld-pct">%</span></span>
                      <span class="rld-gauge-lbl">Overall Score</span>
                    </div>
                  </div>
                  <div class="rld-tier-badge" id="landing-report-score-pill">
                    <span>Needs Practice</span>
                  </div>

                  <!-- Metric Progress Bars -->
                  <div class="rld-bars-list">
                    <div class="rld-bar-item">
                      <div class="rld-bar-meta">
                        <span>Answer Quality</span>
                        <span class="rld-val-blue">92%</span>
                      </div>
                      <div class="rld-track"><div class="rld-fill fill-blue" style="width: 92%;"></div></div>
                    </div>
                    <div class="rld-bar-item">
                      <div class="rld-bar-meta">
                        <span>Communication</span>
                        <span class="rld-val-purple">87%</span>
                      </div>
                      <div class="rld-track"><div class="rld-fill fill-purple" style="width: 87%;"></div></div>
                    </div>
                    <div class="rld-bar-item">
                      <div class="rld-bar-meta">
                        <span>Visual Attention</span>
                        <span class="rld-val-cyan">94%</span>
                      </div>
                      <div class="rld-track"><div class="rld-fill fill-cyan" style="width: 94%;"></div></div>
                    </div>
                  </div>
                </div>

                <!-- Sub-col 2: Question Performance Grid & Feedback -->
                <div class="rld-questions-col">
                  <h4 class="rld-section-subtitle">Question Performance</h4>
                  <div class="rld-q-boxes-grid">
                    <div class="rld-q-box">
                      <span class="rld-qb-title">System Design</span>
                      <span class="rld-qb-score">89</span>
                    </div>
                    <div class="rld-q-box">
                      <span class="rld-qb-title">OOP Concepts</span>
                      <span class="rld-qb-score">94</span>
                    </div>
                    <div class="rld-q-box">
                      <span class="rld-qb-title">Data Structures</span>
                      <span class="rld-qb-score">78</span>
                    </div>
                    <div class="rld-q-box">
                      <span class="rld-qb-title">Problem Solving</span>
                      <span class="rld-qb-score">91</span>
                    </div>
                  </div>

                  <!-- AI Feedback Insight Box -->
                  <div class="rld-insight-callout">
                    <div class="rld-insight-header">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#792FFF" stroke-width="2.5">
                        <path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z"></path>
                        <line x1="9" y1="21" x2="15" y2="21"></line>
                      </svg>
                      <span>AI Feedback Insight:</span>
                    </div>
                    <p class="rld-insight-text">
                      Strong conceptual understanding across technical topics and clear architectural reasoning. Consider pacing system design explanations evenly.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Lavender/Blue Gradient Performance Report Panel -->
            <div class="report-right-gradient-panel">
              <div class="rrp-top-content">
                <span class="rrp-label">Performance Report</span>
                <h3 class="rrp-main-title">Know exactly where you stand.</h3>
                <p class="rrp-desc">
                  A complete breakdown of your interview performance — scored, categorized, and ready to act on.
                </p>
              </div>
              <div class="rrp-chart-illustration">
                <img src="assets/illustrations/ref_purple_chart.png" alt="Ascending Performance Chart" class="rrp-chart-img">
              </div>
            </div>
          </div>
        </section>

        <!-- 7. WHY AI INTERVIEW ANALYZER -->
        <section class="landing-section-block why-us-block">
          <div class="section-center-header">
            <span class="eyebrow-caps">WHY AI INTERVIEW ANALYZER</span>
            <h2 class="section-heading">More than just a mock interview.</h2>
          </div>
          <div class="why-us-four-grid">
            <div class="why-card-pill">
              <div class="why-check-circle">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1677FF" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
              <div class="why-card-content">
                <h4 class="why-card-title">Realistic interview practice</h4>
                <p class="why-card-desc">Practice with realistic questions and scenarios.</p>
              </div>
            </div>

            <div class="why-card-pill">
              <div class="why-check-circle">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1677FF" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
              <div class="why-card-content">
                <h4 class="why-card-title">Identify weak areas</h4>
                <p class="why-card-desc">Understand exactly where your performance needs improvement.</p>
              </div>
            </div>

            <div class="why-card-pill">
              <div class="why-check-circle">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1677FF" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
              <div class="why-card-content">
                <h4 class="why-card-title">Improve communication</h4>
                <p class="why-card-desc">Build confidence and communicate your answers clearly.</p>
              </div>
            </div>

            <div class="why-card-pill">
              <div class="why-check-circle">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1677FF" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
              <div class="why-card-content">
                <h4 class="why-card-title">Track interview readiness</h4>
                <p class="why-card-desc">See how your performance improves over time.</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 8. FINAL CTA SECTION (MATCHING REFERENCE DESIGN) -->
        <section class="landing-section-block final-cta-block">
          <div class="cta-banner-card">
            <!-- Left: Laptop visual -->
            <div class="cta-banner-left">
              <img src="assets/illustrations/ref_cta_laptop.png" alt="Online Interview with Feedback" class="cta-laptop-img">
            </div>

            <!-- Center: Headings & Buttons -->
            <div class="cta-banner-center">
              <h2 class="cta-banner-heading">Ready for your next interview?</h2>
              <p class="cta-banner-sub">
                Start your journey towards a <strong>better career</strong> with AI Interview Analyzer.
              </p>
              <div class="cta-banner-buttons">
                <button class="btn btn-primary btn-cta-gradient" id="btn-start-interview-footer">
                  <span>Start Your Interview</span>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                  </svg>
                </button>
                <button class="btn btn-cta-white" id="btn-view-demo-footer">
                  <span>View Demo</span>
                </button>
              </div>
            </div>

            <!-- Right: Script text -->
            <div class="cta-banner-right">
              <span class="cta-script-slogan">Better Interviews,<br>Brighter Future ⭐</span>
            </div>
          </div>
        </section>

        <!-- 9. LIGHT THEME LANDING FOOTER (MATCHING REFERENCE DESIGN) -->
        <footer class="app-footer landing-integrated-footer">
          <div class="footer-inner-card">
            <div class="footer-left-col">
              <div class="footer-brand-logo">
                <div class="brand-icon small">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                  </svg>
                </div>
                <span class="footer-brand-title">AI Interview Analyzer</span>
              </div>
              <p class="footer-brand-desc">AI-powered interview practice and feedback.</p>
            </div>

            <div class="footer-center-copyright">
              <span>© 2026 AI Interview Analyzer. All rights reserved.</span>
            </div>

            <div class="footer-right-links">
              <div class="footer-nav-col">
                <span class="footer-col-header">PRODUCT</span>
                <a href="#how-it-works" class="footer-link">How It Works</a>
                <a href="#features" class="footer-link">Features</a>
                <button class="footer-link-btn" id="btn-login-footer">Login</button>
              </div>
              <div class="footer-nav-col">
                <span class="footer-col-header">LEGAL</span>
                <a href="#" class="footer-link">Privacy</a>
                <a href="#" class="footer-link">Terms</a>
              </div>
            </div>
          </div>
        </footer>

      </div>
    </div>
"""

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '    <!-- VIEW 0: PUBLIC LANDING PAGE -->'
end_marker = '    <!-- VIEW 1: LIVE INTERVIEW WORKSPACE'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print('ERROR: Markers not found!')
else:
    new_content = content[:start_idx] + landing_html + '\n' + content[end_idx:]
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('SUCCESS: Updated landing page in frontend/index.html!')


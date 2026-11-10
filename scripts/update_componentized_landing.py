import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace hero-right with the multi-layered componentized hero stage
old_hero_right = """            <!-- Right Hero Composition -->
            <div class="hero-right">
              <div class="hero-visual-wrapper">
                <div class="hero-glow-backdrop"></div>
                <img src="assets/illustrations/ref_hero_composition.png" alt="Candidate AI Interview Analytics Scene" class="hero-composition-img">
              </div>
            </div>"""

new_hero_right = """            <!-- Right Hero Composition (Layered Frontend Components) -->
            <div class="hero-right">
              <div class="hero-composition-stage">
                <!-- 1. Ambient Glow Backdrop -->
                <div class="hero-glow-halo"></div>

                <!-- 2. Candidate with Laptop Illustration -->
                <div class="hero-candidate-layer">
                  <img src="assets/illustrations/hero_candidate_isolated_transparent.png" alt="Software Engineer Candidate" class="hero-candidate-char" onerror="this.src='assets/illustrations/hero_candidate_isolated.jpg'">
                </div>

                <!-- 3. Floating AI Robot Companion (Bottom Right) -->
                <div class="hero-robot-layer">
                  <img src="assets/illustrations/ai_robot_transparent.png" alt="AI Robot Assistant" class="hero-robot-avatar">
                </div>

                <!-- 4. Floating Glassmorphic Analytics Preview Card (Left Foreground) -->
                <div class="hero-analytics-floating-card">
                  <div class="hafc-header">
                    <div class="hafc-titles">
                      <h4 class="hafc-title">Interview Analytics Preview</h4>
                      <span class="hafc-subtitle" id="hero-preview-subtitle">Frontend Engineer Candidate</span>
                    </div>
                    <div class="hafc-status-pill">
                      <span class="hafc-pulse-dot"></span>
                      <span>AI Ready</span>
                    </div>
                  </div>

                  <div class="hafc-body">
                    <!-- Circular Gauge -->
                    <div class="hafc-gauge-box">
                      <svg class="hafc-gauge-svg" width="76" height="76" viewBox="0 0 100 100">
                        <circle class="hafc-gauge-track" cx="50" cy="50" r="40" fill="none" stroke="#EBF1FA" stroke-width="8"></circle>
                        <circle class="hafc-gauge-prog" cx="50" cy="50" r="40" fill="none" stroke="#258BFF" stroke-width="8" stroke-dasharray="251" stroke-dashoffset="216" stroke-linecap="round"></circle>
                      </svg>
                      <div class="hafc-gauge-val-wrap">
                        <span class="hafc-val-num" id="hero-preview-overall-score">14<span class="hafc-pct">%</span></span>
                        <span class="hafc-val-lbl">Overall Readiness</span>
                      </div>
                    </div>

                    <!-- Metric Bars -->
                    <div class="hafc-metrics-list">
                      <div class="hafc-metric-item">
                        <span class="hafc-m-lbl">Answer Quality</span>
                        <span class="hafc-m-val text-blue" id="hero-preview-answer-val">92%</span>
                      </div>
                      <div class="hafc-metric-item">
                        <span class="hafc-m-lbl">Communication</span>
                        <span class="hafc-m-val text-blue" id="hero-preview-comm-val">87%</span>
                      </div>
                      <div class="hafc-metric-item">
                        <span class="hafc-m-lbl">Visual Presence</span>
                        <span class="hafc-m-val text-blue" id="hero-preview-visual-val">94%</span>
                      </div>
                    </div>
                  </div>

                  <div class="hafc-footer">
                    <div class="hafc-feedback-pill">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="3">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                      <span>Actionable Feedback Ready</span>
                    </div>
                  </div>
                </div>

                <!-- 5. Floating Microphone Badge (Top Left) -->
                <div class="hero-float-icon icon-mic">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="23"></line>
                  </svg>
                </div>

                <!-- 6. Floating Analytics Bar Chart Badge (Top Right) -->
                <div class="hero-float-icon icon-analytics">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#792FFF" stroke-width="2.2">
                    <line x1="18" y1="20" x2="18" y2="10"></line>
                    <line x1="12" y1="20" x2="12" y2="4"></line>
                    <line x1="6" y1="20" x2="6" y2="14"></line>
                  </svg>
                </div>

                <!-- 7. Floating Sound Waveform Badge (Middle Right) -->
                <div class="hero-float-icon icon-waveform">
                  <svg width="24" height="14" viewBox="0 0 28 16" fill="none" stroke="#258BFF" stroke-width="2.2" stroke-linecap="round">
                    <line x1="2" y1="8" x2="2" y2="8"></line>
                    <line x1="6" y1="5" x2="6" y2="11"></line>
                    <line x1="10" y1="2" x2="10" y2="14"></line>
                    <line x1="14" y1="4" x2="14" y2="12"></line>
                    <line x1="18" y1="1" x2="18" y2="15"></line>
                    <line x1="22" y1="6" x2="22" y2="10"></line>
                    <line x1="26" y1="8" x2="26" y2="8"></line>
                  </svg>
                </div>
              </div>
            </div>"""

if old_hero_right in html:
    html = html.replace(old_hero_right, new_hero_right)
    print("SUCCESS: Replaced hero-right with componentized layout!")
else:
    print("Warning: old_hero_right string not found exactly, using regex...")
    pattern = re.compile(r'<!-- Right Hero Composition -->\s*<div class="hero-right">.*?</div>\s*</div>', re.DOTALL)
    html = pattern.sub(new_hero_right, html)

# Replace CTA banner left with componentized laptop stage & speech bubble
old_cta_left = """            <!-- Left: Laptop visual -->
            <div class="cta-banner-left">
              <img src="assets/illustrations/ref_cta_laptop.png" alt="Online Interview with Feedback" class="cta-laptop-img">
            </div>"""

new_cta_left = """            <!-- Left: Laptop visual with speech bubble -->
            <div class="cta-banner-left">
              <div class="cta-laptop-stage">
                <div class="cta-speech-bubble">
                  <span>You got this!</span>
                  <span class="cta-star">⭐</span>
                </div>
                <img src="assets/illustrations/cta_laptop_interview_transparent.png" alt="Online Interview with Feedback" class="cta-laptop-img" id="cta-laptop-img" onerror="this.src='assets/illustrations/cta_laptop_interview.jpg'">
              </div>
            </div>"""

if old_cta_left in html:
    html = html.replace(old_cta_left, new_cta_left)
    print("SUCCESS: Replaced cta-banner-left with componentized layout!")
else:
    pattern2 = re.compile(r'<!-- Left: Laptop visual -->\s*<div class="cta-banner-left">.*?</div>', re.DOTALL)
    html = pattern2.sub(new_cta_left, html)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("SUCCESS: Updated frontend/index.html with componentized visual architecture!")

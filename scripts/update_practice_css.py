css_replacement = '''/* --------------------------------------------------------------------------
   11. LIVE INTERVIEW ROOM — PIXEL-PERFECT SAAS THEME (EXACT REFERENCE DESIGN)
   -------------------------------------------------------------------------- */

/* Preserve floating navbar visibility in live interview */
body.in-interview .site-header,
body.in-interview .site-footer,
body.in-interview .app-footer,
body:has(#view-practice.active:not(.session-completed)) .site-header,
body:has(#view-practice.active:not(.session-completed)) .site-footer {
  display: none !important;
}

body.in-interview .navbar,
body:has(#view-practice.active:not(.session-completed)) .navbar {
  display: flex !important;
  position: relative !important;
  z-index: 50 !important;
}

body.in-interview .main-container,
body:has(#view-practice.active:not(.session-completed)) .main-container {
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100vw !important;
  width: 100vw !important;
  min-height: calc(100vh - 72px) !important;
  background: #F5F7FF !important;
}

#view-practice {
  display: none !important;
}

#view-practice.active {
  display: flex !important;
  min-height: calc(100vh - 72px);
  width: 100vw;
  background: #F5F7FF;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 24px;
}

#view-practice.active.session-completed,
#view-practice.session-completed,
#view-practice:has(#completion-card:not(.hidden)) {
  min-height: 100vh !important;
  overflow-y: auto !important;
  background: #F5F7FF !important;
}

#view-practice.session-completed .interview-progress-header,
#view-practice:has(#completion-card:not(.hidden)) .interview-progress-header,
#view-practice.session-completed .interview-bottombar,
#view-practice:has(#completion-card:not(.hidden)) .interview-bottombar,
#view-practice.session-completed .interview-main-stage,
#view-practice:has(#completion-card:not(.hidden)) .interview-main-stage {
  display: none !important;
}

/* Atmospheric Ambient Lighting Accents */
.interview-ambient-glow {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.55;
}

.glow-top-left {
  top: 10px;
  left: -80px;
  width: 480px;
  height: 480px;
  background: radial-gradient(circle, rgba(37, 139, 255, 0.12) 0%, rgba(121, 47, 255, 0.08) 50%, transparent 80%);
}

.glow-bottom-right {
  bottom: 40px;
  right: -100px;
  width: 520px;
  height: 520px;
  background: radial-gradient(circle, rgba(121, 47, 255, 0.12) 0%, rgba(18, 184, 240, 0.08) 50%, transparent 80%);
}

.interview-workspace-wrapper {
  position: relative;
  z-index: 1;
  width: min(1380px, calc(100% - 48px));
  margin-inline: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
}

/* QUESTION PROGRESS HEADER */
.interview-progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0 6px 0;
}

.iph-left {
  display: flex;
  align-items: center;
}

.iph-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.iph-counter-text {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #101B55;
  letter-spacing: -0.01em;
}

.iph-progress-track {
  width: 280px;
  height: 6px;
  background: #E2E8F0;
  border-radius: 999px;
  overflow: hidden;
}

.iph-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1677FF 0%, #258BFF 100%);
  border-radius: 999px;
  transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.iph-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.iph-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  font-size: 0.8125rem;
  font-weight: 600;
  padding: 6px 14px;
  user-select: none;
}

.iph-chip-headphones {
  background: #FFFFFF;
  border: 1.5px solid #E2E8F0;
  color: #53658F;
  box-shadow: 0 2px 6px rgba(16, 27, 85, 0.02);
}

.iph-chip-live {
  background: #FEE2E2;
  border: 1.5px solid #FECACA;
  color: #EF4444;
  font-weight: 800;
  letter-spacing: 0.04em;
  padding: 5px 14px;
}

.live-pulsing-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #EF4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.8);
  animation: pulseLiveDot 1.5s infinite;
}

@keyframes pulseLiveDot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

.iph-chip-timer {
  background: #FFFFFF;
  border: 1.5px solid #E2E8F0;
  color: #101B55;
  font-family: var(--font-mono);
  font-size: 0.875rem;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(16, 27, 85, 0.02);
}

/* MAIN TWO-COLUMN STAGE (54% Left, 44% Right) */
.interview-main-stage {
  display: grid;
  grid-template-columns: 1fr 0.82fr;
  gap: 24px;
  align-items: start;
}

.interview-qa-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* AI QUESTION CARD */
.question-card {
  background: #FFFFFF;
  border: 1.5px solid #EAF0FA;
  border-radius: 24px;
  padding: 26px 30px;
  box-shadow: 0 8px 30px rgba(16, 27, 85, 0.04);
  position: relative;
  transition: all 0.25s ease;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.qh-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.interviewer-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.interviewer-avatar-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1677FF 0%, #258BFF 100%);
  color: #FFFFFF;
  font-weight: 800;
  font-size: 0.72rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.3);
}

.interviewer-label {
  font-size: 0.8125rem;
  font-weight: 800;
  color: #101B55;
  letter-spacing: 0.04em;
}

.qh-track-chip {
  background: #F3E8FF;
  color: #792FFF;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 999px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  border: 1px solid rgba(121, 47, 255, 0.15);
}

.q-label-tag {
  background: #EAF2FF;
  color: #1677FF;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 999px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  border: 1px solid rgba(22, 119, 255, 0.15);
}

/* Question Body Row with 3D Illustration */
.question-body-row {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 20px;
}

.question-3d-visual-wrap {
  flex-shrink: 0;
  width: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.question-3d-bubble-img {
  width: 115px;
  height: auto;
  filter: drop-shadow(0 12px 24px rgba(121, 47, 255, 0.18));
  animation: floatCodeBubble 4s ease-in-out infinite;
}

@keyframes floatCodeBubble {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.question-text-wrap {
  flex: 1;
}

.question-title-text {
  font-size: 1.7rem;
  font-weight: 800;
  color: #101B55;
  line-height: 1.35;
  letter-spacing: -0.02em;
  margin: 0;
}

.question-subhint {
  color: #53658F;
  font-size: 0.9375rem;
  font-weight: 500;
  margin: 8px 0 0 0;
  line-height: 1.45;
}

/* LIVE REAL-TIME TRANSCRIPTION CARD (DARK NAVY) */
.live-transcript-panel {
  background: #0B132B;
  border: 1px solid rgba(37, 139, 255, 0.2);
  border-radius: 18px;
  padding: 18px 22px;
  box-shadow: 0 8px 26px rgba(11, 19, 43, 0.25);
  margin-top: 18px;
  transition: border-color 0.3s ease;
}

.live-transcript-panel.is-recording {
  border-color: rgba(37, 139, 255, 0.5);
  box-shadow: 0 8px 28px rgba(37, 139, 255, 0.18);
}

.ltp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.ltp-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ltp-title {
  color: #93C5FD;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.ltp-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #10B981;
  font-size: 0.78rem;
  font-weight: 700;
}

.ltp-pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 8px #10B981;
  animation: pulseGreenDot 1.5s infinite;
}

@keyframes pulseGreenDot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}

.ltp-body-row {
  display: flex;
  align-items: center;
  gap: 18px;
  padding-top: 14px;
}

.live-audio-waveform-bars {
  flex-shrink: 0;
  width: 80px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.transcription-canvas {
  width: 80px;
  height: 42px;
  border-radius: 6px;
}

.ltp-scroll-box {
  flex: 1;
  min-height: 42px;
  max-height: 85px;
  overflow-y: auto;
}

.ltp-placeholder {
  color: #94A3B8;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}

.ltp-content {
  color: #FFFFFF;
  font-size: 0.9375rem;
  font-weight: 500;
  line-height: 1.55;
  margin: 0;
}

/* Question Footer Badges */
.question-footer-badges {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 18px;
}

.q-meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  font-size: 0.8125rem;
  font-weight: 700;
  padding: 6px 16px;
}

.pill-purple {
  background: #F5F3FF;
  color: #7C3AED;
  border: 1.5px solid #EDE9FE;
}

.pill-blue {
  background: #EFF6FF;
  color: #2563EB;
  border: 1.5px solid #DBEAFE;
}

.pill-green {
  background: #ECFDF5;
  color: #059669;
  border: 1.5px solid #D1FAE5;
}

/* RIGHT COLUMN: LIVE WEBCAM & ATTENTION ANALYSIS */
.interview-cam-col {
  display: flex;
  flex-direction: column;
}

.webcam-monitor-card {
  background: #0B132B;
  border: 2px solid #1677FF;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 12px 36px rgba(16, 27, 85, 0.16);
  display: flex;
  flex-direction: column;
}

.webcam-card-topbar {
  background: #0B132B;
  padding: 13px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.wct-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cam-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 4px 10px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.cam-badge-live {
  background: rgba(239, 68, 68, 0.16);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #EF4444;
}

.cam-dot-red {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #EF4444;
  box-shadow: 0 0 6px #EF4444;
}

.cam-badge-active {
  background: rgba(16, 185, 129, 0.16);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: #10B981;
}

.cam-dot-green {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 6px #10B981;
}

.wct-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cam-switch-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #94A3B8;
  font-size: 0.8125rem;
  font-weight: 600;
}

.cam-select-input-sm {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 10px;
  color: #FFFFFF;
  font-size: 0.8125rem;
  font-weight: 600;
  padding: 5px 12px;
  outline: none;
  cursor: pointer;
  max-width: 200px;
}

.cam-select-input-sm option {
  background: #0B132B;
  color: #FFFFFF;
}

.camera-viewport-container {
  position: relative;
  height: 410px;
  background: #050B1E;
  overflow: hidden;
}

.camera-stream-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
  display: block;
}

/* Framing Corner Brackets */
.camera-framing-guide {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.guide-corner {
  position: absolute;
  width: 22px;
  height: 22px;
  border-color: #258BFF;
  border-style: solid;
}

.guide-corner.top-left {
  top: 14px;
  left: 14px;
  border-width: 2.5px 0 0 2.5px;
  border-top-left-radius: 6px;
}

.guide-corner.top-right {
  top: 14px;
  right: 14px;
  border-width: 2.5px 2.5px 0 0;
  border-top-right-radius: 6px;
}

.guide-corner.bottom-left {
  bottom: 14px;
  left: 14px;
  border-width: 0 0 2.5px 2.5px;
  border-bottom-left-radius: 6px;
}

.guide-corner.bottom-right {
  bottom: 14px;
  right: 14px;
  border-width: 0 2.5px 2.5px 0;
  border-bottom-right-radius: 6px;
}

/* Floating Center Attention Alert Banner */
.face-detection-alert-banner {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(239, 68, 68, 0.92);
  backdrop-filter: blur(8px);
  color: #FFFFFF;
  padding: 8px 20px;
  border-radius: 999px;
  font-size: 0.8125rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 18px rgba(239, 68, 68, 0.45);
  z-index: 10;
  white-space: nowrap;
  animation: bannerShake 0.4s ease;
}

@keyframes bannerShake {
  0%, 100% { transform: translateX(-50%); }
  25% { transform: translateX(calc(-50% - 4px)); }
  75% { transform: translateX(calc(-50% + 4px)); }
}

/* Bottom Telemetry HUD Overlays */
.video-telemetry-hud {
  position: absolute;
  bottom: 16px;
  left: 18px;
  right: 18px;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
  z-index: 10;
}

.hud-pill {
  background: rgba(11, 19, 43, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 999px;
  padding: 7px 18px;
  color: #FFFFFF;
  font-size: 0.8rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.hud-face {
  border: 1px solid rgba(37, 139, 255, 0.4);
}

.hud-dot-blue {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #258BFF;
  box-shadow: 0 0 8px #258BFF;
}

.hud-pose {
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.hud-dot-green {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 8px #10B981;
}

/* FLOATING BOTTOM INTERVIEW CONTROL BAR */
.interview-bottombar {
  background: #FFFFFF;
  border: 1.5px solid #EAF0FA;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(16, 27, 85, 0.08);
  padding: 14px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14px;
}

.ibb-left {
  display: flex;
  align-items: center;
}

.answer-state-bubble {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.asi-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #F3E8FF;
  color: #792FFF;
  display: flex;
  align-items: center;
  justify-content: center;
}

.asi-label {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #101B55;
}

.asi-live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 8px #10B981;
}

.ibb-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-gradient-start-answer {
  background: linear-gradient(135deg, #1677FF 0%, #792FFF 100%) !important;
  color: #FFFFFF !important;
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  padding: 14px 38px !important;
  border-radius: 14px !important;
  box-shadow: 0 8px 24px rgba(22, 119, 255, 0.35) !important;
  border: none !important;
  cursor: pointer !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 10px !important;
}

.btn-gradient-start-answer:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(22, 119, 255, 0.45) !important;
}

.btn-danger-stop-answer {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
  color: #FFFFFF !important;
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  padding: 14px 38px !important;
  border-radius: 14px !important;
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.35) !important;
  border: none !important;
  cursor: pointer !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 10px !important;
  animation: pulseDanger 2s infinite;
}

@keyframes pulseDanger {
  0%, 100% { box-shadow: 0 8px 24px rgba(239, 68, 68, 0.35); }
  50% { box-shadow: 0 8px 30px rgba(239, 68, 68, 0.55); }
}

.ibb-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.answer-timer-box {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.atb-label {
  color: #53658F;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.atb-time {
  color: #101B55;
  font-size: 1.35rem;
  font-weight: 800;
  font-family: var(--font-mono);
  line-height: 1.1;
}

.ibb-util-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-circle-util {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: #F8FAFC;
  border: 1.5px solid #E2E8F0;
  color: #1677FF;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(16, 27, 85, 0.03);
}

.btn-circle-util:hover {
  background: #EAF2FF;
  border-color: #1677FF;
  transform: translateY(-1px);
}

.btn-circle-util.muted {
  background: #FEE2E2;
  border-color: #FCA5A5;
  color: #EF4444;
}

.btn-pill-end-interview {
  background: #FEE2E2;
  border: 1.5px solid #FCA5A5;
  color: #DC2626;
  font-size: 0.8125rem;
  font-weight: 700;
  padding: 10px 18px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-pill-end-interview:hover {
  background: #FED7D7;
  transform: translateY(-1px);
}

.end-icon-square {
  width: 9px;
  height: 9px;
  background: #DC2626;
  border-radius: 2px;
}

/* RESPONSIVE DESIGN BREAKPOINTS */
@media (max-width: 1100px) {
  .interview-main-stage {
    grid-template-columns: 1fr;
  }

  .camera-viewport-container {
    height: 360px;
  }

  .question-3d-visual-wrap {
    width: 90px;
  }

  .question-3d-bubble-img {
    width: 85px;
  }

  .question-title-text {
    font-size: 1.4rem;
  }
}

@media (max-width: 768px) {
  .interview-progress-header {
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;
  }

  .iph-center {
    order: 3;
    width: 100%;
  }

  .iph-progress-track {
    width: 100%;
  }

  .interview-bottombar {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }

  .ibb-right {
    width: 100%;
    justify-content: space-between;
  }

  .question-body-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
'''

with open('frontend/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

start_marker = '/* --------------------------------------------------------------------------\n   11. LIVE INTERVIEW ROOM — SINGLE VIEWPORT (100VH NO-SCROLL LAYOUT)'
end_marker = '/* --------------------------------------------------------------------------\n   12. POST-INTERVIEW COMPREHENSIVE REPORT STYLES (LIGHT SAAS THEME)'

start_idx = css.find(start_marker)
end_idx = css.find(end_marker)

assert start_idx != -1, "start_marker not found in style.css"
assert end_idx != -1, "end_marker not found in style.css"

updated_css = css[:start_idx] + css_replacement + '\n\n' + css[end_idx:]

with open('frontend/style.css', 'w', encoding='utf-8') as f:
    f.write(updated_css)

print("SUCCESS: frontend/style.css live interview room styles updated!")

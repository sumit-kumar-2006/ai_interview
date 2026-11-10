css_replacement = '''/* --------------------------------------------------------------------------
   9. INTERVIEW SETUP WORKSPACE STYLES (LIGHT SAAS THEME - PIXEL-PERFECT)
   -------------------------------------------------------------------------- */
#view-interview-setup {
  background: #F5F7FF;
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
}

/* Atmospheric Ambient Glows */
.setup-ambient-glow {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.65;
}

.setup-glow-top-right {
  top: 40px;
  right: -100px;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(121, 47, 255, 0.12) 0%, rgba(37, 139, 255, 0.08) 60%, transparent 80%);
}

.setup-glow-bottom-left {
  bottom: 100px;
  left: -80px;
  width: 450px;
  height: 450px;
  background: radial-gradient(circle, rgba(37, 139, 255, 0.12) 0%, rgba(22, 185, 129, 0.06) 60%, transparent 80%);
}

.setup-wrapper {
  position: relative;
  z-index: 1;
  width: min(1240px, calc(100% - 48px));
  margin-inline: auto;
  padding-top: 24px;
  padding-bottom: 60px;
}

/* Two-Column Hero Header with 3D Laptop Interviewer */
.setup-hero-split {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 32px;
  margin-bottom: 28px;
}

.setup-hero-content {
  flex: 1;
  max-width: 620px;
}

.btn-back-link {
  background: #FFFFFF;
  border: 1.5px solid #E2E8F0;
  border-radius: 999px;
  padding: 6px 14px;
  color: #53658F;
  font-size: 0.8125rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  cursor: pointer;
  margin-bottom: 16px;
  box-shadow: 0 2px 6px rgba(16, 27, 85, 0.03);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-back-link:hover {
  color: #1677FF;
  border-color: #1677FF;
  background: #F0F6FF;
  transform: translateX(-2px);
}

.setup-hero-title {
  font-size: 2.75rem;
  font-weight: 800;
  color: #101B55;
  margin: 0 0 6px 0;
  letter-spacing: -0.025em;
  line-height: 1.15;
}

.setup-hero-title .gradient-text {
  background: linear-gradient(135deg, #1677FF 0%, #792FFF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.setup-hero-subtitle-wrap {
  position: relative;
  display: inline-block;
}

.setup-hero-subtitle {
  font-size: 1.05rem;
  color: #53658F;
  margin: 0;
  font-weight: 500;
  line-height: 1.5;
}

.setup-title-wave {
  display: block;
  margin-top: 4px;
  opacity: 0.85;
}

/* Laptop Stage in Header */
.setup-hero-stage {
  flex-shrink: 0;
  position: relative;
}

.setup-laptop-card {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.setup-hero-laptop-img {
  width: 290px;
  height: auto;
  filter: drop-shadow(0 16px 28px rgba(16, 27, 85, 0.12));
  transition: transform 0.4s ease;
}

.setup-laptop-card:hover .setup-hero-laptop-img {
  transform: translateY(-3px) scale(1.02);
}

/* Speech Bubble above laptop */
.setup-speech-bubble {
  position: absolute;
  top: -12px;
  right: -8px;
  background: #FFFFFF;
  border-radius: 999px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 8px 24px rgba(16, 27, 85, 0.1);
  border: 1px solid rgba(22, 119, 255, 0.1);
  font-size: 0.8125rem;
  font-weight: 700;
  color: #101B55;
  white-space: nowrap;
  z-index: 3;
  animation: floatBubble 3.5s ease-in-out infinite;
}

@keyframes floatBubble {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.setup-speech-bubble .speech-star {
  font-size: 0.9rem;
}

/* Floating Mic Badge to the left of laptop */
.setup-floating-mic {
  position: absolute;
  left: -14px;
  top: 36px;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1677FF 0%, #258BFF 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 18px rgba(22, 119, 255, 0.38);
  z-index: 3;
  animation: pulseMic 3s infinite ease-in-out;
}

@keyframes pulseMic {
  0%, 100% { transform: scale(1); box-shadow: 0 6px 18px rgba(22, 119, 255, 0.38); }
  50% { transform: scale(1.06); box-shadow: 0 8px 24px rgba(22, 119, 255, 0.55); }
}

/* MAIN TWO-COLUMN LAYOUT */
.setup-main-grid {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 28px;
  align-items: start;
}

.setup-config-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Individual Setup Card */
.setup-card {
  background: #FFFFFF;
  border: 1.5px solid #EAF0FA;
  border-radius: 20px;
  padding: 24px 26px;
  box-shadow: 0 4px 20px rgba(16, 27, 85, 0.03);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.setup-card:hover {
  box-shadow: 0 8px 26px rgba(16, 27, 85, 0.06);
  border-color: #DCE7F7;
}

/* Card Header */
.setup-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.setup-card-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.setup-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.setup-card-icon.icon-blue {
  background: #EAF2FF;
  color: #1677FF;
}

.setup-card-icon.icon-purple {
  background: #F3E8FF;
  color: #8B42FF;
}

.setup-card-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #101B55;
  margin: 0;
  letter-spacing: -0.01em;
}

.setup-card-hint {
  font-size: 0.8125rem;
  color: #53658F;
  margin: 2px 0 0 0;
  line-height: 1.45;
}

/* AI Personalized Badge */
.badge-ai-personalized {
  background: #E8FDF5;
  border: 1px solid #A7F3D0;
  color: #059669;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 5px 12px;
  border-radius: 999px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.badge-ai-personalized .b-check {
  font-weight: 900;
  color: #10B981;
}

/* CARD 1: RESUME UPLOAD & PREVIEW */
.res-file-bar {
  background: #F8FAFC;
  border: 1.5px solid #E2E8F0;
  border-radius: 14px;
  padding: 12px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.res-file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.res-check-circle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #10B981;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.res-file-text {
  display: flex;
  flex-direction: column;
}

.res-filename {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #101B55;
}

.res-meta-stats {
  font-size: 0.8rem;
  color: #53658F;
  font-weight: 500;
  margin-top: 1px;
}

.btn-change-file {
  background: #FFFFFF;
  border: 1.5px solid #E2E8F0;
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 0.8125rem;
  font-weight: 700;
  color: #101B55;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-change-file:hover {
  border-color: #1677FF;
  color: #1677FF;
  background: #F0F6FF;
}

/* Skill Chips Grid */
.setup-skills-chips-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.skill-tag-chip {
  background: #EAF2FF;
  border: 1px solid #D6E4FF;
  color: #1677FF;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 6px 13px;
  border-radius: 8px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  transition: all 0.2s ease;
  user-select: none;
}

.skill-tag-chip:hover {
  background: #DCEBFF;
  transform: translateY(-1px);
}

/* Featured Projects */
.setup-featured-projects-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  margin-bottom: 16px;
  padding-left: 2px;
}

.sfp-icon {
  font-size: 1.1rem;
}

.sfp-label {
  color: #53658F;
  font-weight: 500;
}

.sfp-name {
  color: #101B55;
  font-weight: 700;
}

/* Collapsible Skills Accordion */
.setup-skills-accordion {
  border-top: 1px solid #EAF0FA;
  padding-top: 12px;
}

.setup-accordion-header {
  background: none;
  border: none;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #53658F;
  cursor: pointer;
  padding: 4px 0;
  transition: color 0.2s;
  text-align: left;
}

.setup-accordion-header:hover {
  color: #1677FF;
}

.accordion-arrow-icon {
  transition: transform 0.25s ease;
}

.setup-accordion-header.active .accordion-arrow-icon {
  transform: rotate(180deg);
}

.setup-accordion-body {
  display: none;
  margin-top: 12px;
}

.setup-accordion-body.open {
  display: block;
}

.setup-skills-edit-bar {
  display: flex;
  gap: 10px;
}

.setup-skills-input {
  flex: 1;
  padding: 9px 14px;
  border-radius: 10px;
  border: 1.5px solid #E2E8F0;
  font-size: 0.875rem;
  color: #101B55;
  background: #F8FAFC;
  outline: none;
  transition: border-color 0.2s;
}

.setup-skills-input:focus {
  border-color: #1677FF;
  background: #FFFFFF;
}

.btn-update-skills {
  white-space: nowrap;
  border-radius: 10px;
}

/* CARD 2: TARGET ROLE (HORIZONTAL ROW) */
.setup-role-header {
  margin-bottom: 0;
}

.setup-select-container {
  min-width: 220px;
}

.setup-custom-dropdown {
  padding: 10px 18px;
  border-radius: 12px;
  border: 1.5px solid #E2E8F0;
  background: #FFFFFF;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #101B55;
  width: 100%;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.setup-custom-dropdown:focus {
  border-color: #1677FF;
  box-shadow: 0 0 0 3px rgba(22, 119, 255, 0.12);
}

/* OPTION CARD GRIDS (Experience, Difficulty, Questions, Mode) */
.setup-grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.setup-opt-card {
  position: relative;
  background: #FFFFFF;
  border: 1.5px solid #E2E8F0;
  border-radius: 14px;
  padding: 16px 14px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}

.setup-opt-card:hover {
  border-color: #A3C7FF;
  background: #F8FAFF;
}

.setup-opt-card.active {
  background: #EAF2FF;
  border: 2px solid #1677FF;
  box-shadow: 0 4px 14px rgba(22, 119, 255, 0.12);
}

.opt-check-bubble {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #1677FF;
  display: none;
  align-items: center;
  justify-content: center;
}

.setup-opt-card.active .opt-check-bubble {
  display: flex;
}

.soc-title {
  display: block;
  font-size: 0.9375rem;
  font-weight: 700;
  color: #101B55;
}

.setup-opt-card.active .soc-title {
  color: #1677FF;
}

.soc-sub {
  display: block;
  font-size: 0.775rem;
  color: #53658F;
  margin-top: 3px;
  font-weight: 500;
}

/* CARD 4: INTERVIEW TYPE */
.type-card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.setup-type-card {
  position: relative;
  background: #FFFFFF;
  border: 1.5px solid #E2E8F0;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}

.setup-type-card:hover {
  border-color: #A3C7FF;
  background: #F8FAFF;
}

.setup-type-card.active {
  background: #F0F6FF;
  border: 2px solid #1677FF;
  box-shadow: 0 6px 18px rgba(22, 119, 255, 0.12);
}

.stc-badge-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stc-pill {
  font-size: 0.72rem;
  font-weight: 700;
  color: #53658F;
  background: #F1F5F9;
  padding: 3px 10px;
  border-radius: 999px;
}

.pill-recommended {
  background: #EAF2FF;
  color: #1677FF;
  border: 1px solid #D6E4FF;
}

.setup-type-card.active .stc-badge-row .opt-check-bubble {
  display: flex;
  position: static;
}

.stc-title {
  font-size: 1rem;
  font-weight: 700;
  color: #101B55;
  margin: 0 0 6px 0;
}

.stc-desc {
  font-size: 0.8125rem;
  color: #53658F;
  line-height: 1.45;
  margin: 0;
}

/* DIFFICULTY & QUESTION COUNT PILLS */
.option-pill-grid.trio {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

/* CARD 7: INTERVIEW MODE */
.option-pill-grid.duo.setup-mode-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.setup-mode-card {
  text-align: left;
  padding: 18px 20px;
}

.smc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.smc-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.smc-icon {
  color: #1677FF;
  flex-shrink: 0;
}

/* RIGHT COLUMN: STICKY INTERVIEW SUMMARY */
.setup-summary-col {
  position: sticky;
  top: 92px;
}

.summary-sticky-card {
  background: #FFFFFF;
  border: 1.5px solid #EAF0FA;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 30px rgba(16, 27, 85, 0.05);
}

.ssc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #EAF0FA;
  padding-bottom: 14px;
  margin-bottom: 18px;
}

.ssc-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ssc-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
}

.ssc-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #101B55;
  margin: 0;
}

.ssc-chip {
  font-size: 0.6875rem;
  font-weight: 800;
  color: #10B981;
  background: #E6F9F2;
  border: 1px solid #A7F3D0;
  padding: 3px 10px;
  border-radius: 999px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.ssc-body-rows {
  display: flex;
  flex-direction: column;
  gap: 11px;
  margin-bottom: 20px;
}

.ssc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  padding-bottom: 8px;
  border-bottom: 1px solid #F1F5F9;
}

.ssc-row-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #53658F;
  font-weight: 500;
}

.ssc-row-icon {
  font-size: 0.95rem;
}

.ssc-val {
  font-weight: 700;
  color: #101B55;
}

.sum-resume-val-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}

.res-truncate {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-view-resume-eye {
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #53658F;
  transition: color 0.2s;
}

.btn-view-resume-eye:hover {
  color: #1677FF;
}

/* Personalization Info Callout */
.personalized-info-box {
  background: #EBF9F5;
  border: 1.5px solid #D1FAE5;
  border-radius: 14px;
  padding: 14px 16px;
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.pib-sparkle {
  font-size: 1.25rem;
  line-height: 1;
}

.pib-text strong {
  display: block;
  font-size: 0.8125rem;
  font-weight: 700;
  color: #047857;
  margin-bottom: 3px;
}

.pib-text p {
  font-size: 0.775rem;
  color: #065F46;
  margin: 0;
  line-height: 1.4;
}

/* Continue Button */
.btn-gradient-continue {
  background: linear-gradient(135deg, #1677FF 0%, #792FFF 100%) !important;
  border: none !important;
  border-radius: 14px !important;
  padding: 16px 24px !important;
  color: #FFFFFF !important;
  font-size: 1rem !important;
  font-weight: 700 !important;
  width: 100% !important;
  cursor: pointer !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 0 6px 20px rgba(22, 119, 255, 0.28) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.btn-gradient-continue:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(22, 119, 255, 0.38) !important;
}

/* 3D Microphone Artwork Stage */
.setup-mic-stage {
  position: relative;
  margin-top: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}

.setup-mic-glow {
  position: absolute;
  width: 220px;
  height: 220px;
  background: radial-gradient(circle, rgba(37, 139, 255, 0.2) 0%, rgba(121, 47, 255, 0.08) 50%, transparent 70%);
  filter: blur(30px);
  pointer-events: none;
  z-index: 1;
}

.setup-mic-img {
  position: relative;
  z-index: 2;
  max-width: 260px;
  width: 100%;
  height: auto;
  filter: drop-shadow(0 15px 25px rgba(16, 27, 85, 0.1));
  transition: transform 0.4s ease;
}

.setup-mic-stage:hover .setup-mic-img {
  transform: translateY(-4px) scale(1.02);
}

/* Footer on Setup Page */
.setup-footer {
  margin-top: 48px;
}

/* Responsive Breakpoints */
@media (max-width: 1100px) {
  .setup-hero-split {
    flex-direction: column;
    align-items: flex-start;
  }

  .setup-hero-stage {
    align-self: center;
    margin-top: 10px;
  }

  .setup-main-grid {
    grid-template-columns: 1fr;
  }

  .setup-summary-col {
    position: static;
  }

  .setup-mic-stage {
    display: none;
  }
}

@media (max-width: 768px) {
  .setup-hero-title {
    font-size: 2.2rem;
  }

  .setup-grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }

  .type-card-grid {
    grid-template-columns: 1fr;
  }

  .option-pill-grid.trio {
    grid-template-columns: 1fr;
  }

  .option-pill-grid.duo.setup-mode-grid {
    grid-template-columns: 1fr;
  }

  .setup-card-header.setup-role-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }

  .setup-select-container {
    width: 100%;
  }
}
'''

with open('frontend/style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

start_marker = '/* --------------------------------------------------------------------------\n   9. INTERVIEW SETUP WORKSPACE STYLES (LIGHT SAAS THEME)'
end_marker = '/* --------------------------------------------------------------------------\n   10. CAMERA & MICROPHONE DEVICE CHECK STYLES (LIGHT SAAS THEME)'

start_idx = css_content.find(start_marker)
end_idx = css_content.find(end_marker)

assert start_idx != -1, 'Start marker not found in style.css'
assert end_idx != -1, 'End marker not found in style.css'

updated_css = css_content[:start_idx] + css_replacement + '\n\n' + css_content[end_idx:]

with open('frontend/style.css', 'w', encoding='utf-8') as f:
    f.write(updated_css)

print('SUCCESS: frontend/style.css setup workspace styles updated successfully!')


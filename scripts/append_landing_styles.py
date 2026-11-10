landing_css = """
/* ========================================================================== */
/* PIXEL-PERFECT 2026 AI SAAS LANDING PAGE (MATCHING REFERENCE SPECIFICATION) */
/* ========================================================================== */

/* 1. Global Page Background & Typography */
body {
  font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #101B55;
  background-color: #F8FAFD;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.landing-page-wrapper {
  background: radial-gradient(ellipse 90% 60% at 50% -5%, #EAF2FF 0%, #F5F8FF 45%, #FFFFFF 85%);
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 20px;
}

/* Ambient Dot Matrix Patterns */
.landing-page-wrapper::before {
  content: '';
  position: absolute;
  top: 600px;
  left: 20px;
  width: 120px;
  height: 120px;
  background-image: radial-gradient(#CBD8F0 2px, transparent 2px);
  background-size: 16px 16px;
  opacity: 0.6;
  pointer-events: none;
  z-index: 0;
}

.landing-page-wrapper::after {
  content: '';
  position: absolute;
  top: 1050px;
  right: 20px;
  width: 120px;
  height: 120px;
  background-image: radial-gradient(#CBD8F0 2px, transparent 2px);
  background-size: 16px 16px;
  opacity: 0.6;
  pointer-events: none;
  z-index: 0;
}

/* 2. Top Navigation Pill */
.navbar {
  position: sticky;
  top: 16px;
  z-index: 100;
  width: 100%;
  padding: 0 20px;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  height: 64px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(226, 235, 250, 0.95);
  border-radius: 9999px;
  box-shadow: 0 8px 30px -4px rgba(22, 119, 255, 0.07), 0 2px 6px -1px rgba(16, 27, 85, 0.03);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px 8px 24px;
  transition: all 0.3s ease;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-brand .brand-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #1677FF;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.3);
}

.nav-brand .brand-title {
  font-size: 15px;
  font-weight: 700;
  color: #101B55;
  letter-spacing: -0.3px;
}

.landing-nav-links {
  display: flex;
  align-items: center;
  gap: 32px;
}

.landing-nav-item {
  font-size: 14px;
  font-weight: 500;
  color: #53658F;
  text-decoration: none;
  transition: color 0.2s ease;
}

.landing-nav-item:hover {
  color: #1677FF;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.api-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  border-radius: 9999px;
  padding: 5px 13px;
  font-size: 12px;
  font-weight: 600;
  color: #065F46;
}

.api-status-badge .status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.6);
}

.btn-theme-toggle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #F0F4FC;
  border: 1px solid #E2EAF8;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #101B55;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-theme-toggle:hover {
  background: #E4ECFB;
}

.unauth-nav-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-nav-login {
  background: transparent;
  border: none;
  font-size: 14px;
  font-weight: 600;
  color: #101B55;
  padding: 8px 14px;
  cursor: pointer;
  border-radius: 9999px;
  transition: background 0.2s;
}

.btn-nav-login:hover {
  background: #F0F4FC;
}

.btn-nav-start {
  background: linear-gradient(135deg, #258BFF 0%, #792FFF 100%) !important;
  color: #FFFFFF !important;
  border-radius: 9999px !important;
  padding: 9px 20px !important;
  font-size: 13.5px !important;
  font-weight: 600 !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  border: none !important;
  box-shadow: 0 6px 18px rgba(37, 139, 255, 0.35) !important;
  cursor: pointer !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
}

.btn-nav-start:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 22px rgba(37, 139, 255, 0.45) !important;
}

/* 3. Hero Section */
.landing-hero-section {
  max-width: 1200px;
  margin: 40px auto 48px;
  padding: 0 20px;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 40px;
}

.hero-left {
  max-width: 540px;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #EAF2FF;
  border: 1px solid #C9E0FF;
  border-radius: 9999px;
  padding: 5px 14px;
  font-size: 11px;
  font-weight: 700;
  color: #1677FF;
  letter-spacing: 0.6px;
  margin-bottom: 20px;
}

.hero-eyebrow .eyebrow-plus {
  font-size: 13px;
  font-weight: 800;
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  color: #101B55;
  line-height: 1.12;
  letter-spacing: -1.8px;
  margin-bottom: 20px;
}

.text-gradient-hero {
  background: linear-gradient(135deg, #258BFF 0%, #792FFF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.hero-subtitle {
  font-size: 16px;
  line-height: 1.65;
  color: #53658F;
  margin-bottom: 32px;
}

.hero-cta-buttons {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}

.btn-hero-gradient {
  background: linear-gradient(135deg, #258BFF 0%, #792FFF 100%) !important;
  color: #FFFFFF !important;
  border-radius: 9999px !important;
  padding: 14px 28px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 10px !important;
  border: none !important;
  box-shadow: 0 10px 24px rgba(37, 139, 255, 0.35) !important;
  cursor: pointer !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
}

.btn-hero-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 30px rgba(37, 139, 255, 0.45) !important;
}

.btn-hero-white {
  background: #FFFFFF !important;
  border: 1px solid #E2E8F6 !important;
  color: #101B55 !important;
  border-radius: 9999px !important;
  padding: 14px 26px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  box-shadow: 0 4px 14px rgba(16, 27, 85, 0.04) !important;
  text-decoration: none !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
}

.btn-hero-white:hover {
  background: #F8FAFD !important;
  border-color: #D2DFEE !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 27, 85, 0.08) !important;
}

.hero-trust-indicators {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.trust-indicator-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  font-weight: 500;
  color: #53658F;
}

.trust-indicator-item .check-icon {
  flex-shrink: 0;
}

/* Hero Right Visual */
.hero-right {
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-visual-wrapper {
  position: relative;
  width: 100%;
  max-width: 580px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-glow-backdrop {
  position: absolute;
  width: 440px;
  height: 440px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(37, 139, 255, 0.25) 0%, rgba(121, 47, 255, 0.15) 45%, transparent 70%);
  filter: blur(28px);
  z-index: 0;
  pointer-events: none;
}

.hero-composition-img {
  position: relative;
  z-index: 1;
  width: 100%;
  height: auto;
  border-radius: 24px;
  box-shadow: 0 16px 45px -8px rgba(37, 139, 255, 0.18), 0 4px 14px rgba(16, 27, 85, 0.05);
  animation: heroFloat 5s ease-in-out infinite;
  transition: transform 0.3s;
}

@keyframes heroFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-7px);
  }
}

/* 4. Section 3: Four Feature Cards */
.four-features-section {
  max-width: 1200px;
  margin: 36px auto 60px;
  padding: 0 20px;
}

.four-features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.feature-capsule-card {
  background: #FFFFFF;
  border-radius: 18px;
  padding: 24px 20px 32px;
  border: 1px solid #EBF1FA;
  box-shadow: 0 4px 18px rgba(22, 119, 255, 0.03);
  position: relative;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.feature-capsule-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 14px 30px rgba(22, 119, 255, 0.08);
  border-color: #D6E4FA;
}

.feat-capsule-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.feat-capsule-icon.icon-blue {
  background: #EAF2FF;
  color: #1677FF;
}

.feat-capsule-icon.icon-purple {
  background: #F3EEFF;
  color: #792FFF;
}

.feat-capsule-icon.icon-cyan {
  background: #E6F8FF;
  color: #0099FF;
}

.feat-capsule-title {
  font-size: 16px;
  font-weight: 700;
  color: #101B55;
  margin-bottom: 8px;
}

.feat-capsule-desc {
  font-size: 13px;
  line-height: 1.55;
  color: #53658F;
}

.feat-circle-arrow {
  position: absolute;
  right: 18px;
  bottom: 18px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #F0F5FF;
  border: 1px solid #DCE7FC;
  color: #1677FF;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.feature-capsule-card:hover .feat-circle-arrow {
  background: #1677FF;
  color: #FFFFFF;
  border-color: #1677FF;
}

/* 5. Section 4: How It Works */
.landing-section-block {
  max-width: 1200px;
  margin: 64px auto;
  padding: 0 20px;
}

.section-center-header {
  text-align: center;
  margin-bottom: 40px;
}

.eyebrow-caps {
  display: inline-block;
  background: #EAF2FF;
  color: #1677FF;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.6px;
  padding: 4px 14px;
  border-radius: 9999px;
  margin-bottom: 10px;
}

.section-heading {
  font-size: 32px;
  font-weight: 800;
  color: #101B55;
  letter-spacing: -0.8px;
}

.steps-connected-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.step-connected-card {
  flex: 1;
  background: #FFFFFF;
  border-radius: 20px;
  padding: 28px 24px;
  border: 1px solid #EBF1FA;
  box-shadow: 0 4px 20px rgba(22, 119, 255, 0.04);
  position: relative;
  overflow: hidden;
  transition: all 0.25s;
}

.step-connected-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(22, 119, 255, 0.08);
}

.step-watermark-num {
  position: absolute;
  top: 16px;
  right: 20px;
  font-size: 42px;
  font-weight: 800;
  color: #E4EEFB;
  line-height: 1;
  pointer-events: none;
}

.step-icon-bubble {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.step-icon-bubble.bubble-blue {
  background: #EAF2FF;
  color: #1677FF;
}

.step-icon-bubble.bubble-purple {
  background: #F3EEFF;
  color: #792FFF;
}

.step-connected-title {
  font-size: 17px;
  font-weight: 700;
  color: #101B55;
  margin-bottom: 8px;
}

.step-connected-desc {
  font-size: 13.5px;
  line-height: 1.5;
  color: #53658F;
}

.step-arrow-connector {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  flex-shrink: 0;
  color: #258BFF;
}

/* 6. Section 5: Features 2x2 Grid */
.features-two-by-two-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.feat-row-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #FFFFFF;
  border-radius: 18px;
  padding: 22px 26px;
  border: 1px solid #EBF1FA;
  box-shadow: 0 4px 18px rgba(22, 119, 255, 0.03);
  transition: all 0.25s;
}

.feat-row-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(22, 119, 255, 0.06);
}

.feat-circle-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feat-circle-icon.icon-blue {
  background: #EAF2FF;
  color: #1677FF;
}

.feat-circle-icon.icon-purple {
  background: #F3EEFF;
  color: #792FFF;
}

.feat-circle-icon.icon-cyan {
  background: #E6F8FF;
  color: #0099FF;
}

.feat-row-title {
  font-size: 16.5px;
  font-weight: 700;
  color: #101B55;
  margin-bottom: 4px;
}

.feat-row-desc {
  font-size: 13.5px;
  line-height: 1.5;
  color: #53658F;
}

/* 7. Section 6: Performance Report Preview */
.report-preview-master-wrapper {
  display: flex;
  gap: 24px;
  align-items: stretch;
}

.report-left-dashboard-card {
  flex: 1.65;
  background: #FFFFFF;
  border-radius: 24px;
  padding: 32px 36px;
  border: 1px solid #E2EAF8;
  box-shadow: 0 10px 30px rgba(22, 119, 255, 0.05);
}

.rld-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #F0F4FA;
}

.rld-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rld-badge-pill {
  background: #E8F8F0;
  color: #10B981;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 9999px;
}

.rld-role-heading {
  font-size: 18px;
  font-weight: 700;
  color: #101B55;
}

.rld-status-pill {
  background: #10B981;
  color: #FFFFFF;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 9999px;
}

.rld-content-grid {
  display: grid;
  grid-template-columns: 210px 1fr;
  gap: 32px;
  align-items: flex-start;
}

.rld-gauge-container {
  position: relative;
  width: 110px;
  height: 110px;
  margin: 0 auto 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rld-gauge-svg {
  transform: rotate(-90deg);
}

.rld-gauge-text {
  position: absolute;
  text-align: center;
}

.rld-gauge-val {
  font-size: 26px;
  font-weight: 800;
  color: #101B55;
  display: block;
  line-height: 1;
}

.rld-pct {
  font-size: 14px;
}

.rld-gauge-lbl {
  font-size: 10.5px;
  font-weight: 600;
  color: #8B9BB4;
  margin-top: 4px;
  display: block;
}

.rld-tier-badge {
  display: block;
  background: #EAF9F2;
  color: #10B981;
  font-size: 11.5px;
  font-weight: 700;
  padding: 3px 12px;
  border-radius: 9999px;
  margin-bottom: 20px;
  text-align: center;
}

.rld-bars-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rld-bar-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  color: #53658F;
  margin-bottom: 5px;
}

.rld-val-blue { color: #1677FF; }
.rld-val-purple { color: #792FFF; }
.rld-val-cyan { color: #00B4D8; }

.rld-track {
  width: 100%;
  height: 6px;
  background: #EEF3FA;
  border-radius: 9999px;
  overflow: hidden;
}

.rld-fill {
  height: 100%;
  border-radius: 9999px;
}

.rld-fill.fill-blue { background: linear-gradient(90deg, #258BFF, #1677FF); }
.rld-fill.fill-purple { background: linear-gradient(90deg, #8B42FF, #792FFF); }
.rld-fill.fill-cyan { background: linear-gradient(90deg, #00D2D3, #00B4D8); }

.rld-section-subtitle {
  font-size: 14px;
  font-weight: 700;
  color: #101B55;
  margin-bottom: 12px;
}

.rld-q-boxes-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 16px;
}

.rld-q-box {
  background: #F4F7FC;
  border-radius: 10px;
  padding: 10px 14px;
  display: flex;
  justify-content: space-between;
  font-size: 12.5px;
  font-weight: 600;
  color: #101B55;
}

.rld-insight-callout {
  background: #F4EEFF;
  border: 1px solid #E8DCFF;
  border-radius: 14px;
  padding: 14px 16px;
}

.rld-insight-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #792FFF;
  font-size: 12.5px;
  font-weight: 700;
  margin-bottom: 6px;
}

.rld-insight-text {
  font-size: 12px;
  line-height: 1.55;
  color: #53658F;
}

/* Right Gradient Panel */
.report-right-gradient-panel {
  flex: 1;
  background: linear-gradient(145deg, #EEF4FF 0%, #E6E2FF 100%);
  border-radius: 24px;
  padding: 36px 32px;
  border: 1px solid #DFE7FB;
  box-shadow: 0 10px 30px rgba(121, 47, 255, 0.06);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}

.rrp-label {
  font-size: 16px;
  font-weight: 700;
  color: #101B55;
}

.rrp-main-title {
  font-size: 26px;
  font-weight: 800;
  color: #101B55;
  line-height: 1.25;
  margin: 8px 0 14px;
}

.rrp-desc {
  font-size: 13.5px;
  line-height: 1.6;
  color: #53658F;
}

.rrp-chart-illustration {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

.rrp-chart-img {
  width: 90px;
  height: auto;
  filter: drop-shadow(0 4px 12px rgba(121, 47, 255, 0.2));
}

/* 8. Section 7: Why AI Interview Analyzer */
.why-us-four-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}

.why-card-pill {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #FFFFFF;
  border-radius: 16px;
  padding: 20px 18px;
  border: 1px solid #EBF1FA;
  box-shadow: 0 4px 18px rgba(22, 119, 255, 0.03);
  transition: all 0.25s;
}

.why-card-pill:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(22, 119, 255, 0.06);
}

.why-check-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #EAF2FF;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.why-card-title {
  font-size: 14.5px;
  font-weight: 700;
  color: #101B55;
  margin-bottom: 4px;
}

.why-card-desc {
  font-size: 12.5px;
  line-height: 1.45;
  color: #53658F;
}

/* 9. Section 8: Call to Action Banner */
.cta-banner-card {
  max-width: 1200px;
  margin: 48px auto;
  border-radius: 28px;
  padding: 36px 44px;
  background: linear-gradient(105deg, #DCE9FF 0%, #E2E8FF 45%, #792FFF 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 16px 45px -8px rgba(37, 139, 255, 0.25);
  position: relative;
  overflow: hidden;
}

.cta-banner-left {
  flex-shrink: 0;
}

.cta-laptop-img {
  width: 180px;
  height: auto;
  border-radius: 10px;
  filter: drop-shadow(0 10px 20px rgba(16, 27, 85, 0.15));
}

.cta-banner-center {
  text-align: center;
  max-width: 480px;
}

.cta-banner-heading {
  font-size: 28px;
  font-weight: 800;
  color: #101B55;
  letter-spacing: -0.6px;
  margin-bottom: 8px;
}

.cta-banner-sub {
  font-size: 14px;
  color: #53658F;
  margin-bottom: 22px;
}

.cta-banner-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
}

.btn-cta-gradient {
  background: linear-gradient(135deg, #258BFF 0%, #792FFF 100%) !important;
  color: #FFFFFF !important;
  border-radius: 9999px !important;
  padding: 12px 24px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  border: none !important;
  cursor: pointer !important;
  box-shadow: 0 6px 18px rgba(37, 139, 255, 0.4) !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
}

.btn-cta-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(37, 139, 255, 0.5) !important;
}

.btn-cta-white {
  background: #FFFFFF !important;
  color: #101B55 !important;
  border-radius: 9999px !important;
  padding: 12px 22px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  border: 1px solid #E2E8F6 !important;
  cursor: pointer !important;
  box-shadow: 0 4px 12px rgba(16, 27, 85, 0.04) !important;
  transition: all 0.2s !important;
}

.btn-cta-white:hover {
  background: #F8FAFD !important;
  transform: translateY(-2px);
}

.cta-banner-right {
  flex-shrink: 0;
  text-align: right;
}

.cta-script-slogan {
  color: #FFFFFF;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.3;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  display: block;
  transform: rotate(-3deg);
}

/* 10. Section 9: Footer */
.landing-integrated-footer {
  max-width: 1200px;
  margin: 0 auto 36px;
  padding: 0 20px;
  background: transparent;
  border: none;
}

.footer-inner-card {
  background: #FFFFFF;
  border-radius: 22px;
  border: 1px solid #EBF1FA;
  box-shadow: 0 6px 24px rgba(22, 119, 255, 0.04);
  padding: 32px 48px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.footer-brand-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-brand-logo .brand-icon.small {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: #1677FF;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
}

.footer-brand-title {
  font-size: 15px;
  font-weight: 700;
  color: #101B55;
}

.footer-brand-desc {
  font-size: 12.5px;
  color: #53658F;
}

.footer-center-copyright {
  font-size: 13px;
  color: #8B9BB4;
}

.footer-right-links {
  display: flex;
  gap: 48px;
}

.footer-nav-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-col-header {
  font-size: 11px;
  font-weight: 700;
  color: #8B9BB4;
  letter-spacing: 0.6px;
  margin-bottom: 2px;
}

.footer-link {
  font-size: 13px;
  color: #53658F;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-link:hover {
  color: #1677FF;
}

.footer-link-btn {
  background: transparent;
  border: none;
  padding: 0;
  font-size: 13px;
  color: #53658F;
  cursor: pointer;
  text-align: left;
  transition: color 0.2s;
}

.footer-link-btn:hover {
  color: #1677FF;
}

/* 11. Responsive Media Queries */
@media (max-width: 1024px) {
  .hero-grid {
    grid-template-columns: 1fr;
    text-align: center;
  }
  .hero-left {
    max-width: 100%;
    margin: 0 auto;
  }
  .hero-subtitle {
    margin: 0 auto 30px;
  }
  .hero-cta-buttons, .hero-trust-indicators {
    justify-content: center;
  }
  .four-features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .steps-connected-row {
    flex-direction: column;
  }
  .step-arrow-connector {
    transform: rotate(90deg);
  }
  .report-preview-master-wrapper {
    flex-direction: column;
  }
  .why-us-four-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .cta-banner-card {
    flex-direction: column;
    text-align: center;
    gap: 24px;
  }
  .cta-script-slogan {
    text-align: center;
    transform: none;
  }
  .footer-inner-card {
    flex-direction: column;
    gap: 24px;
    text-align: center;
  }
  .footer-brand-logo {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 40px;
  }
  .features-two-by-two-grid {
    grid-template-columns: 1fr;
  }
  .four-features-grid {
    grid-template-columns: 1fr;
  }
  .why-us-four-grid {
    grid-template-columns: 1fr;
  }
  .rld-content-grid {
    grid-template-columns: 1fr;
  }
  .landing-nav-links {
    display: none;
  }
}
"""

with open('frontend/style.css', 'a', encoding='utf-8') as f:
    f.write(landing_css)

print('SUCCESS: Appended pixel-perfect landing styles to frontend/style.css!')


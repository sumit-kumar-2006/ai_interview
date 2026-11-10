component_css = """
/* ========================================================================== */
/* COMPONENTIZED MULTI-LAYER HERO & CTA STAGES                                */
/* ========================================================================== */

.hero-composition-stage {
  position: relative;
  width: 100%;
  max-width: 580px;
  height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-glow-halo {
  position: absolute;
  width: 440px;
  height: 440px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(37, 139, 255, 0.22) 0%, rgba(121, 47, 255, 0.12) 45%, transparent 70%);
  filter: blur(28px);
  z-index: 1;
  pointer-events: none;
}

.hero-candidate-layer {
  position: absolute;
  right: 10px;
  bottom: 0;
  width: 420px;
  height: 380px;
  z-index: 2;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
}

.hero-candidate-char {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: right bottom;
  filter: drop-shadow(0 14px 32px rgba(16, 27, 85, 0.14));
}

.hero-robot-layer {
  position: absolute;
  right: -15px;
  bottom: -5px;
  width: 165px;
  height: 175px;
  z-index: 4;
}

.hero-robot-avatar {
  width: 100%;
  height: 100%;
  object-fit: contain;
  animation: floatRobot 4s ease-in-out infinite;
  filter: drop-shadow(0 10px 24px rgba(37, 139, 255, 0.35));
}

@keyframes floatRobot {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-8px) rotate(1.5deg);
  }
}

/* Floating Glassmorphic Analytics Preview Card */
.hero-analytics-floating-card {
  position: absolute;
  left: -20px;
  bottom: 25px;
  width: 310px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(226, 235, 250, 0.95);
  border-radius: 20px;
  padding: 18px 20px;
  box-shadow: 0 16px 40px -8px rgba(22, 119, 255, 0.16), 0 4px 14px rgba(16, 27, 85, 0.04);
  z-index: 5;
  animation: floatCard 5.5s ease-in-out infinite;
}

@keyframes floatCard {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

.hafc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}

.hafc-title {
  font-size: 13.5px;
  font-weight: 700;
  color: #101B55;
  margin: 0 0 2px;
  line-height: 1.2;
}

.hafc-subtitle {
  font-size: 11px;
  font-weight: 500;
  color: #53658F;
}

.hafc-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  border-radius: 9999px;
  padding: 3px 8px;
  font-size: 10.5px;
  font-weight: 600;
  color: #065F46;
}

.hafc-pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.6);
}

.hafc-body {
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 14px;
  align-items: center;
  margin-bottom: 14px;
}

.hafc-gauge-box {
  position: relative;
  width: 76px;
  height: 76px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hafc-gauge-svg {
  transform: rotate(-90deg);
}

.hafc-gauge-val-wrap {
  position: absolute;
  text-align: center;
}

.hafc-val-num {
  font-size: 20px;
  font-weight: 800;
  color: #101B55;
  line-height: 1;
  display: block;
}

.hafc-pct {
  font-size: 12px;
  font-weight: 700;
}

.hafc-val-lbl {
  font-size: 8px;
  font-weight: 600;
  color: #8B9BB4;
  margin-top: 2px;
  display: block;
  line-height: 1.1;
}

.hafc-metrics-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.hafc-metric-item {
  display: flex;
  justify-content: space-between;
  font-size: 11.5px;
  font-weight: 600;
  color: #53658F;
  border-bottom: 1px solid #F4F7FC;
  padding-bottom: 3px;
}

.hafc-m-val.text-blue {
  color: #1677FF;
  font-weight: 700;
}

.hafc-footer {
  display: flex;
}

.hafc-feedback-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #EAF9F2;
  border-radius: 9999px;
  padding: 4px 12px;
  font-size: 11px;
  font-weight: 600;
  color: #10B981;
}

/* Floating Badges */
.hero-float-icon {
  position: absolute;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(22, 119, 255, 0.15);
  z-index: 3;
}

.hero-float-icon.icon-mic {
  top: 24px;
  left: 60px;
  width: 44px;
  height: 44px;
  background: #1677FF;
  color: #FFFFFF;
  animation: floatIcon1 4s ease-in-out infinite;
}

.hero-float-icon.icon-analytics {
  top: 14px;
  right: 40px;
  width: 44px;
  height: 44px;
  background: #FFFFFF;
  border: 1px solid #EBF1FA;
  color: #792FFF;
  animation: floatIcon2 4.6s ease-in-out infinite;
}

.hero-float-icon.icon-waveform {
  top: 190px;
  right: -15px;
  width: 48px;
  height: 32px;
  border-radius: 9999px;
  background: #FFFFFF;
  border: 1px solid #EBF1FA;
  color: #258BFF;
  animation: floatIcon3 3.8s ease-in-out infinite;
}

@keyframes floatIcon1 {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-7px); }
}

@keyframes floatIcon2 {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-9px); }
}

@keyframes floatIcon3 {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

/* CTA Laptop Stage */
.cta-laptop-stage {
  position: relative;
  display: inline-block;
}

.cta-speech-bubble {
  position: absolute;
  top: -14px;
  right: 15px;
  background: #FFFFFF;
  border-radius: 9999px;
  padding: 5px 14px;
  box-shadow: 0 6px 18px rgba(16, 27, 85, 0.15);
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 700;
  color: #101B55;
  z-index: 5;
  animation: floatSpeech 3.5s ease-in-out infinite;
}

@keyframes floatSpeech {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.cta-laptop-img {
  width: 250px;
  height: auto;
  display: block;
  filter: drop-shadow(0 14px 28px rgba(16, 27, 85, 0.22));
}
"""

with open('frontend/style.css', 'a', encoding='utf-8') as f:
    f.write(component_css)

print("SUCCESS: Appended componentized CSS to frontend/style.css!")

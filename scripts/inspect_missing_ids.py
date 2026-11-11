import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
with open('frontend/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

missing_ids = [
  'landing-ai-feedback-insight', 'btn-device-back-setup', 'landing-bar-comm-fill',
  'val-face-status', 'live-cv-status', 'landing-bar-comm-val', 'mic-icon-dot',
  'ref-btn-text', 'btn-retake-interview', 'live-webcam-video', 'reference-drawer',
  'landing-bar-answer-fill', 'landing-bar-visual-val', 'dir-right', 'dir-left',
  'footer-login-btn', 'landing-bar-answer-val', 'recording-card', 'video-overlay-text',
  'print-meta-text', 'interview-question-card', 'api-status-dot', 'val-head-pose',
  'webcam-status-badge', 'video-active-badge', 'landing-bar-visual-fill', 'sb-dot',
  'waveform-wrap', 'btn-quick-switch-audio', 'btn-quick-retry-cam', 'dir-center',
  'landing-qp-grid-list', 'btn-start-interview-final', 'cam-btn-text', 'mic-btn-icon',
  'toggle-ref-btn', 'waveform-canvas', 'asi-mic-icon', 'sb-status-msg', 'api-status-text',
  'btn-repeat-question', 'cam-btn-icon', 'itb-track-label', 'val-user-presence',
  'mic-btn-text', 'val-camera-attention', 'video-mic-text'
]

print(f"Analyzing {len(missing_ids)} missing IDs...")

for mid in missing_ids:
    usages = []
    for line_num, line in enumerate(js.splitlines(), 1):
        if mid in line:
            usages.append((line_num, line.strip()))
    
    print(f"\n--- ID: '{mid}' ({len(usages)} usages) ---")
    for ln, l in usages[:5]:
        print(f"  Line {ln}: {l}")


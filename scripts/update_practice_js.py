with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add generator function question at start of QUESTIONS if not present
if "Explain what a generator function is in JavaScript." not in text:
    old_q = "const QUESTIONS = ["
    new_q = """const QUESTIONS = [
  {
    id: 100,
    question: "Explain what a generator function is in JavaScript.",
    category: "Frontend & Web Development",
    difficulty: "Medium",
    targetTime: "45-90 sec",
    track: "Frontend & Web Development Track"
  },"""
    assert old_q in text, "Could not find const QUESTIONS = ["
    text = text.replace(old_q, new_q, 1)

# 2. Update loadQuestion to set qh-track-chip nicely
old_load_track = "if (document.getElementById('question-category')) {"
new_load_track = """  if (document.getElementById('qh-track-chip')) {
    const role = (currentInterviewConfig.target_role || 'Frontend & Web Development').toLowerCase();
    const track = (role.includes('front') || role.includes('web')) 
      ? 'FRONTEND & WEB DEVELOPMENT TRACK' 
      : `${(currentInterviewConfig.target_role || 'Technical').toUpperCase()} TRACK`;
    document.getElementById('qh-track-chip').innerHTML = `&lt;/&gt; ${track}`;
  }
  if (document.getElementById('question-category')) {"""

if old_load_track in text and "qh-track-chip" not in text[text.find("function loadQuestion("):text.find("function loadQuestion(") + 2000]:
    text = text.replace(old_load_track, new_load_track, 1)

# 3. Update drawWaveform to also animate transcription-waveform-canvas
old_draw = """function drawWaveform() {
  const canvas = document.getElementById('waveform-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');"""

new_draw = """function drawWaveform() {
  const canvas = document.getElementById('waveform-canvas');
  const transCanvas = document.getElementById('transcription-waveform-canvas');
  if (!canvas && !transCanvas) return;
  const ctx = canvas ? canvas.getContext('2d') : null;
  const tCtx = transCanvas ? transCanvas.getContext('2d') : null;"""

if old_draw in text:
    text = text.replace(old_draw, new_draw, 1)

old_render = """    ctx.clearRect(0, 0, width, height);

    const barWidth = (width / bufferLength) * 2;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (dataArray[i] / 255) * height * 0.8;
      const gradient = ctx.createLinearGradient(0, height, 0, 0);
      gradient.addColorStop(0, '#6366F1');
      gradient.addColorStop(1, '#818CF8');

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.roundRect(x, (height - barHeight) / 2, barWidth - 3, barHeight, 4);
      ctx.fill();

      x += barWidth + 2;
    }"""

new_render = """    if (ctx && canvas) {
      ctx.clearRect(0, 0, width, height);
      const barWidth = (width / bufferLength) * 2;
      let x = 0;
      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * height * 0.8;
        const gradient = ctx.createLinearGradient(0, height, 0, 0);
        gradient.addColorStop(0, '#1677FF');
        gradient.addColorStop(1, '#258BFF');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.roundRect(x, (height - barHeight) / 2, barWidth - 3, barHeight, 4);
        ctx.fill();
        x += barWidth + 2;
      }
    }

    if (tCtx && transCanvas) {
      const tW = transCanvas.width;
      const tH = transCanvas.height;
      tCtx.clearRect(0, 0, tW, tH);
      const numBars = 7;
      const tBarW = 5;
      const gap = 6;
      const totalW = numBars * tBarW + (numBars - 1) * gap;
      let startX = (tW - totalW) / 2;

      for (let i = 0; i < numBars; i++) {
        const binIdx = Math.floor((i / numBars) * bufferLength);
        const val = dataArray[binIdx] || 0;
        let bHeight = (val / 255) * tH * 0.85;
        if (bHeight < 6) {
          // Gentle resting pulse when quiet
          bHeight = 8 + Math.sin(Date.now() / 250 + i * 0.8) * 5;
        }
        bHeight = Math.max(6, Math.min(tH - 4, bHeight));

        const tGrad = tCtx.createLinearGradient(0, tH, 0, 0);
        tGrad.addColorStop(0, '#1677FF');
        tGrad.addColorStop(0.5, '#258BFF');
        tGrad.addColorStop(1, '#12B8F0');
        tCtx.fillStyle = tGrad;
        tCtx.beginPath();
        tCtx.roundRect(startX, (tH - bHeight) / 2, tBarW, bHeight, 3);
        tCtx.fill();
        startX += tBarW + gap;
      }
    }"""

if old_render in text:
    text = text.replace(old_render, new_render, 1)

# 4. Bind btn-toggle-fullscreen and btn-interview-back-questions and nav-analytics-btn
old_bind = "const exitBtn = document.getElementById('btn-exit-interview');\n  if (exitBtn) exitBtn.onclick = confirmEndInterview;"
new_bind = """const exitBtn = document.getElementById('btn-exit-interview');
  if (exitBtn) exitBtn.onclick = confirmEndInterview;

  const fullscreenBtn = document.getElementById('btn-toggle-fullscreen');
  if (fullscreenBtn && !fullscreenBtn._bound) {
    fullscreenBtn._bound = true;
    fullscreenBtn.onclick = () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
        fullscreenBtn.classList.add('active');
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen().catch(() => {});
          fullscreenBtn.classList.remove('active');
        }
      }
    };
  }

  const backQuestionsBtn = document.getElementById('btn-interview-back-questions');
  if (backQuestionsBtn && !backQuestionsBtn._bound) {
    backQuestionsBtn._bound = true;
    backQuestionsBtn.onclick = () => {
      if (confirm('Return to interview setup? Your current session progress will be preserved.')) {
        navigateToView('interview-setup');
      }
    };
  }

  const navAnalyticsBtn = document.getElementById('nav-analytics-btn');
  if (navAnalyticsBtn && !navAnalyticsBtn._bound) {
    navAnalyticsBtn._bound = true;
    navAnalyticsBtn.onclick = () => navigateToView('history');
  }"""

if old_bind in text:
    text = text.replace(old_bind, new_bind, 1)

# 5. Update processMediaPipeLandmarks telemetry tags to match reference screenshot
old_hud_tags = """      if (videoFaceTag) videoFaceTag.textContent = 'Face Not Detected';
      if (videoCamTag) videoCamTag.textContent = 'Head: Unknown';"""

new_hud_tags = """      if (videoFaceTag) videoFaceTag.textContent = 'Face Not Detected • Eyes: Away';
      if (videoCamTag) videoCamTag.textContent = 'Head: Unknown';"""

if old_hud_tags in text:
    text = text.replace(old_hud_tags, new_hud_tags, 1)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS: frontend/script.js updated with new controls, waveform animation, and questions!")

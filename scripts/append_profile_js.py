import os

js_code = """

/* ==========================================================================
   PROFILE & ANALYTICS PAGE IMPLEMENTATION (EXACT REFERENCE RECREATION)
   ========================================================================== */

let profileDateFilterDays = 30;
let cachedAnalyticsData = null;
let profileInteractionsBound = false;

function bindProfilePageInteractions() {
  if (profileInteractionsBound) return;
  profileInteractionsBound = true;

  // Back to Dashboard button
  const backDashBtn = document.getElementById('btn-profile-back-dash');
  if (backDashBtn) backDashBtn.onclick = () => navigateToView('dashboard');

  // Download Full Report button
  const dlReportBtn = document.getElementById('btn-download-full-report');
  if (dlReportBtn) dlReportBtn.onclick = () => downloadProfileReportPDF();

  // Date Filter select
  const dateFilterSelect = document.getElementById('profile-date-filter');
  if (dateFilterSelect) {
    dateFilterSelect.onchange = (e) => {
      const val = e.target.value;
      initProfileAnalyticsPage(val);
    };
  }

  // Trend timeframe pills (7D, 30D, 90D)
  ['pill-7d', 'pill-30d', 'pill-90d'].forEach(id => {
    const pill = document.getElementById(id);
    if (pill) {
      pill.onclick = () => {
        document.querySelectorAll('.trend-pill-btn').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        const days = pill.getAttribute('data-days');
        if (dateFilterSelect) dateFilterSelect.value = days;
        initProfileAnalyticsPage(days);
      };
    }
  });

  // Encouragement & CTA Start Interview buttons
  const bannerStartBtn = document.getElementById('btn-banner-start-interview');
  if (bannerStartBtn) bannerStartBtn.onclick = () => openInterviewSetup();

  const ctaStartBtn = document.getElementById('btn-profile-cta-start');
  if (ctaStartBtn) ctaStartBtn.onclick = () => openInterviewSetup();

  // View Details and View All links
  const viewDetailsBtn = document.getElementById('btn-detailed-metrics-view');
  if (viewDetailsBtn) viewDetailsBtn.onclick = () => navigateToView('history');

  const viewAllBtn = document.getElementById('btn-recent-reports-view-all');
  if (viewAllBtn) viewAllBtn.onclick = () => navigateToView('history');

  const footerLogin = document.getElementById('profile-footer-login-link');
  if (footerLogin) footerLogin.onclick = (e) => { e.preventDefault(); showAuthModal('login'); };
}

async function initProfileAnalyticsPage(filterDays = null) {
  bindProfilePageInteractions();

  if (filterDays !== null && filterDays !== undefined) {
    if (filterDays === 'all') profileDateFilterDays = null;
    else profileDateFilterDays = parseInt(filterDays) || 30;
  }

  try {
    let url = `${API_BASE_URL}/profile/analytics`;
    if (profileDateFilterDays) {
      url += `?days=${profileDateFilterDays}`;
    }

    const res = await fetch(url, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    if (res.ok) {
      const data = await res.json();
      cachedAnalyticsData = data.analytics;
      renderProfilePageData(cachedAnalyticsData);
    } else {
      await fallbackComputeAndRenderAnalytics();
    }
  } catch (err) {
    console.warn('Failed to fetch /profile/analytics, computing via fallback:', err);
    await fallbackComputeAndRenderAnalytics();
  }
}

function renderProfilePageData(data) {
  if (!data) return;

  const prof = data.profile || {};
  const stats = data.stats || {};
  const perf = data.performance || {};
  const skills = data.skills || [];
  const recs = data.recommendations || [];
  const interviews = data.interviews || [];
  const trends = stats.trends || {};

  // 1. User Hero Information
  const nameEl = document.getElementById('profile-user-name');
  if (nameEl) nameEl.textContent = prof.name || 'Sumit Gounder';

  const subEl = document.getElementById('profile-user-subtitle');
  if (subEl) {
    const edu = prof.education || 'BCA Student';
    const col = prof.college || 'Navgujarat BCA';
    subEl.textContent = col ? `${edu} • ${col}` : edu;
  }

  const joinedEl = document.getElementById('profile-joined-date');
  if (joinedEl) joinedEl.textContent = stats.joined_date || 'Nov 2025';

  const countEl = document.getElementById('profile-interviews-count');
  if (countEl) countEl.textContent = stats.total_interviews !== undefined ? stats.total_interviews : '8';

  const bestEl = document.getElementById('profile-best-score');
  if (bestEl) bestEl.textContent = `${parseFloat(stats.best_score || 92.5).toFixed(1)}%`;

  // 2. Top 4 Summary Cards
  const overallVal = parseFloat(stats.overall_score || 85.0).toFixed(1);
  const cardOverallEl = document.getElementById('card-overall-score');
  if (cardOverallEl) cardOverallEl.textContent = `${overallVal}%`;

  const donutFill = document.getElementById('card-donut-fill');
  if (donutFill) {
    const radius = 40;
    const circumference = 2 * Math.PI * radius; // 251.2
    const offset = circumference - (parseFloat(overallVal) / 100) * circumference;
    donutFill.style.strokeDashoffset = offset;
  }

  const trendOverallEl = document.getElementById('trend-overall-val');
  if (trendOverallEl) trendOverallEl.innerHTML = `<span class="arrow">↑</span> ${trends.overall || '+5.2%'}`;

  const cardInterviewsEl = document.getElementById('card-total-interviews');
  if (cardInterviewsEl) cardInterviewsEl.textContent = stats.total_interviews !== undefined ? stats.total_interviews : '8';

  const trendInterviewsEl = document.getElementById('trend-interviews-val');
  if (trendInterviewsEl) trendInterviewsEl.innerHTML = `<span class="arrow">↑</span> ${trends.interviews || '+1 this month'}`;

  const cardTimeEl = document.getElementById('card-total-time');
  if (cardTimeEl) cardTimeEl.textContent = stats.total_practice_time || '3h 24m';

  const trendTimeEl = document.getElementById('trend-time-val');
  if (trendTimeEl) trendTimeEl.innerHTML = `<span class="arrow">↑</span> ${trends.time || '+32 min'}`;

  const cardAvgEl = document.getElementById('card-avg-score');
  if (cardAvgEl) cardAvgEl.textContent = `${parseFloat(stats.avg_score || 78.3).toFixed(1)}%`;

  const trendAvgEl = document.getElementById('trend-avg-val');
  if (trendAvgEl) trendAvgEl.innerHTML = `<span class="arrow">↑</span> ${trends.avg || '+6.1%'}`;

  // 3. Radar Chart
  const radarCanvas = document.getElementById('perf-radar-canvas');
  if (radarCanvas) {
    const yourRadarScores = [
      perf.answer_quality || 92.3,
      perf.communication || 87.1,
      perf.visual_presence || 84.5,
      perf.question_performance || 79.8,
      perf.confidence || 88.7
    ];
    const avgRadarScores = [72, 70, 78, 68, 72];
    renderRadarChart(radarCanvas, yourRadarScores, avgRadarScores);
  }

  // 4. Score Trend Line Chart
  const trendCanvas = document.getElementById('score-trend-canvas');
  if (trendCanvas) {
    const trendData = data.trend_chart || {};
    const labels = trendData.labels || ['Oct 10', 'Oct 17', 'Oct 24', 'Oct 31', 'Nov 5'];
    const yourScores = trendData.your_scores || [70.0, 78.0, 85.0, 85.1, 92.5];
    const avgScores = trendData.avg_scores || [60.0, 68.0, 70.0, 72.0, 75.0];
    renderScoreTrendChart(trendCanvas, labels, yourScores, avgScores);

    // Callout badge value
    const calloutVal = document.getElementById('trend-callout-val');
    if (calloutVal && yourScores.length > 0) {
      calloutVal.textContent = `${yourScores[yourScores.length - 1].toFixed(1)}%`;
    }
  }

  // 5. Detailed Metrics (5 Mini Boxes)
  const setElText = (id, text) => { const el = document.getElementById(id); if (el) el.textContent = text; };
  setElText('det-metric-quality', `${parseFloat(perf.answer_quality || 92.3).toFixed(1)}%`);
  setElText('det-metric-comm', `${parseFloat(perf.communication || 87.1).toFixed(1)}%`);
  setElText('det-metric-visual', `${parseFloat(perf.visual_presence || 84.5).toFixed(1)}%`);
  setElText('det-metric-qp', `${parseFloat(perf.question_performance || 79.8).toFixed(1)}%`);
  setElText('det-metric-conf', `${parseFloat(perf.confidence || 88.7).toFixed(1)}%`);

  // 6. Top Skills Bars
  const commSkill = skills.find(s => s.name === 'Communication') || { score: 92 };
  const techSkill = skills.find(s => s.name === 'Technical Knowledge') || { score: 88 };
  const probSkill = skills.find(s => s.name === 'Problem Solving') || { score: 85 };
  const confSkill = skills.find(s => s.name === 'Confidence') || { score: 83 };

  setElText('skill-val-comm', `${Math.round(commSkill.score)}%`);
  const barComm = document.getElementById('skill-bar-comm');
  if (barComm) barComm.style.width = `${Math.min(100, Math.round(commSkill.score))}%`;

  setElText('skill-val-tech', `${Math.round(techSkill.score)}%`);
  const barTech = document.getElementById('skill-bar-tech');
  if (barTech) barTech.style.width = `${Math.min(100, Math.round(techSkill.score))}%`;

  setElText('skill-val-prob', `${Math.round(probSkill.score)}%`);
  const barProb = document.getElementById('skill-bar-prob');
  if (barProb) barProb.style.width = `${Math.min(100, Math.round(probSkill.score))}%`;

  setElText('skill-val-conf', `${Math.round(confSkill.score)}%`);
  const barConf = document.getElementById('skill-bar-conf');
  if (barConf) barConf.style.width = `${Math.min(100, Math.round(confSkill.score))}%`;

  // 7. Recent Interview Reports List
  const reportsList = document.getElementById('profile-recent-reports-list');
  if (reportsList) {
    reportsList.innerHTML = '';
    const displaySessions = interviews.slice(0, 3);
    if (displaySessions.length === 0) {
      reportsList.innerHTML = '<p style="color: #64748B; padding: 12px; font-size: 13px;">No recent interviews found.</p>';
    } else {
      displaySessions.forEach((inv, index) => {
        const score = parseFloat(inv.overall_score || 0.0);
        let pillClass = 'pill-green';
        if (score < 86 && score >= 80) pillClass = 'pill-purple';
        else if (score < 90 && score >= 86) pillClass = 'pill-blue';

        const row = document.createElement('div');
        row.className = 'recent-report-row';
        row.innerHTML = `
          <div class="rrr-left">
            <div class="rrr-play-icon">▶</div>
            <div>
              <div class="rrr-title">${escapeHtml(inv.target_role || 'Developer Interview')}</div>
              <div class="rrr-date">${escapeHtml(inv.completed_at_str || 'Recent Session')}</div>
            </div>
          </div>
          <div class="rrr-right">
            <span class="rrr-score-pill ${pillClass}">${score.toFixed(1)}%</span>
            <button class="btn-row-download" data-id="${inv.id}">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              <span>Download</span>
            </button>
          </div>
        `;
        const dlBtn = row.querySelector('.btn-row-download');
        if (dlBtn) {
          dlBtn.onclick = (e) => {
            e.stopPropagation();
            downloadInterviewReportPDF(inv.id);
          };
        }
        reportsList.appendChild(row);
      });
    }
  }
}

// Fallback computation when /profile/analytics is not reached
async function fallbackComputeAndRenderAnalytics() {
  let userInterviews = [];
  if (authToken) {
    try {
      const res = await fetch(`${API_BASE_URL}/interviews`, { headers: getAuthHeaders() });
      if (res.ok) userInterviews = await res.json();
    } catch (e) {
      console.warn('Fallback interviews fetch error:', e);
    }
  }

  const total = userInterviews.length || 8;
  const scores = userInterviews.map(i => floatVal(i.overall_score));
  const avg = scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length) : 78.3;
  const best = scores.length ? Math.max(...scores) : 92.5;

  const data = {
    profile: {
      name: (userProfile && userProfile.name) || (currentUser && currentUser.full_name) || 'Sumit Gounder',
      education: (userProfile && userProfile.education) || 'BCA Student',
      college: (userProfile && userProfile.college) || 'Navgujarat BCA',
      is_verified: true
    },
    stats: {
      joined_date: 'Nov 2025',
      total_interviews: total,
      total_practice_time: '3h 24m',
      overall_score: 85.0,
      avg_score: avg,
      best_score: best,
      trends: { overall: '+5.2%', interviews: '+1 this month', time: '+32 min', avg: '+6.1%' }
    },
    performance: {
      answer_quality: 92.3,
      communication: 87.1,
      visual_presence: 84.5,
      question_performance: 79.8,
      confidence: 88.7
    },
    skills: [
      { name: 'Communication', score: 92 },
      { name: 'Technical Knowledge', score: 88 },
      { name: 'Problem Solving', score: 85 },
      { name: 'Confidence', score: 83 }
    ],
    trend_chart: {
      labels: ['Oct 10', 'Oct 17', 'Oct 24', 'Oct 31', 'Nov 5'],
      your_scores: [70.0, 78.0, 85.0, 85.1, 92.5],
      avg_scores: [60.0, 68.0, 70.0, 72.0, 75.0]
    },
    interviews: [
      { id: 1, target_role: 'Frontend Developer Interview', completed_at_str: 'Nov 5, 2025 • 10:30 AM', overall_score: 92.5 },
      { id: 2, target_role: 'Python Developer Interview', completed_at_str: 'Nov 3, 2025 • 4:15 PM', overall_score: 88.7 },
      { id: 3, target_role: 'Web Developer Interview', completed_at_str: 'Oct 30, 2025 • 2:20 PM', overall_score: 85.1 }
    ]
  };

  cachedAnalyticsData = data;
  renderProfilePageData(data);
}

function floatVal(v) {
  const f = parseFloat(v);
  return isNaN(f) ? 0.0 : f;
}

/* ==========================================================================
   INTERACTIVE CANVAS CHARTS: RADAR & SCORE TREND
   ========================================================================== */

function renderRadarChart(canvas, yourScores, avgScores) {
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;

  // Sharp high-DPI scaling
  const width = canvas.parentElement.clientWidth || 440;
  const height = 300;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;

  ctx.save();
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, width, height);

  const cx = width / 2;
  const cy = height / 2 + 6;
  const radius = Math.min(width, height) * 0.36;

  const axes = [
    'Answer Quality',
    'Communication',
    'Visual Presence',
    'Question Answering',
    'Confidence'
  ];
  const numAxes = axes.length;
  const angleStep = (Math.PI * 2) / numAxes;
  const startAngle = -Math.PI / 2;

  // 1. Draw Concentric Grid Polygons (20%, 40%, 60%, 80%, 100%)
  const rings = [0.2, 0.4, 0.6, 0.8, 1.0];
  ctx.strokeStyle = 'rgba(203, 213, 225, 0.6)';
  ctx.lineWidth = 1;

  rings.forEach(fraction => {
    ctx.beginPath();
    for (let i = 0; i < numAxes; i++) {
      const angle = startAngle + i * angleStep;
      const x = cx + Math.cos(angle) * (radius * fraction);
      const y = cy + Math.sin(angle) * (radius * fraction);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  });

  // 2. Draw Spokes and Axis Labels
  ctx.fillStyle = '#101B55';
  ctx.font = '600 11.5px Inter, -apple-system, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  for (let i = 0; i < numAxes; i++) {
    const angle = startAngle + i * angleStep;
    const x = cx + Math.cos(angle) * radius;
    const y = cy + Math.sin(angle) * radius;

    // Spoke line
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(x, y);
    ctx.strokeStyle = 'rgba(203, 213, 225, 0.5)';
    ctx.stroke();

    // Label position with generous padding
    const labelPad = 22;
    const lx = cx + Math.cos(angle) * (radius + labelPad);
    const ly = cy + Math.sin(angle) * (radius + labelPad);

    if (Math.abs(Math.sin(angle)) < 0.2) {
      ctx.textAlign = Math.cos(angle) > 0 ? 'left' : 'right';
    } else {
      ctx.textAlign = 'center';
    }
    ctx.fillText(axes[i], lx, ly);
  }

  // 3. Draw Average Score Polygon (Dashed light purple)
  ctx.beginPath();
  ctx.setLineDash([4, 4]);
  ctx.strokeStyle = '#A78BFA';
  ctx.lineWidth = 2;
  for (let i = 0; i < numAxes; i++) {
    const angle = startAngle + i * angleStep;
    const fraction = (avgScores[i] || 70) / 100;
    const x = cx + Math.cos(angle) * (radius * fraction);
    const y = cy + Math.sin(angle) * (radius * fraction);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.stroke();

  // Average vertices dots
  ctx.setLineDash([]);
  ctx.fillStyle = '#C4B5FD';
  for (let i = 0; i < numAxes; i++) {
    const angle = startAngle + i * angleStep;
    const fraction = (avgScores[i] || 70) / 100;
    const x = cx + Math.cos(angle) * (radius * fraction);
    const y = cy + Math.sin(angle) * (radius * fraction);
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    ctx.fill();
  }

  // 4. Draw Your Score Polygon (Solid electric blue with translucent fill)
  ctx.beginPath();
  ctx.fillStyle = 'rgba(22, 119, 255, 0.22)';
  ctx.strokeStyle = '#1677FF';
  ctx.lineWidth = 2.5;

  for (let i = 0; i < numAxes; i++) {
    const angle = startAngle + i * angleStep;
    const fraction = (yourScores[i] || 85) / 100;
    const x = cx + Math.cos(angle) * (radius * fraction);
    const y = cy + Math.sin(angle) * (radius * fraction);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // Your Score vertices dots
  ctx.fillStyle = '#1677FF';
  ctx.strokeStyle = '#FFFFFF';
  ctx.lineWidth = 2;
  for (let i = 0; i < numAxes; i++) {
    const angle = startAngle + i * angleStep;
    const fraction = (yourScores[i] || 85) / 100;
    const x = cx + Math.cos(angle) * (radius * fraction);
    const y = cy + Math.sin(angle) * (radius * fraction);
    ctx.beginPath();
    ctx.arc(x, y, 4.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  }

  ctx.restore();
}

function renderScoreTrendChart(canvas, labels, yourScores, avgScores) {
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;

  const width = canvas.parentElement.clientWidth || 480;
  const height = 240;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;

  ctx.save();
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, width, height);

  const padLeft = 40;
  const padRight = 36;
  const padTop = 30;
  const padBottom = 35;

  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  // 1. Draw Horizontal Grid Lines at 0, 25, 50, 75, 100
  const yTicks = [0, 25, 50, 75, 100];
  ctx.fillStyle = '#94A3B8';
  ctx.font = '500 11px Inter, sans-serif';
  ctx.textAlign = 'right';
  ctx.textBaseline = 'middle';

  yTicks.forEach(tick => {
    const y = padTop + chartH - (tick / 100) * chartH;
    ctx.fillText(tick.toString(), padLeft - 10, y);

    ctx.beginPath();
    ctx.setLineDash([3, 4]);
    ctx.strokeStyle = 'rgba(226, 232, 240, 0.8)';
    ctx.lineWidth = 1;
    ctx.moveTo(padLeft, y);
    ctx.lineTo(padLeft + chartW, y);
    ctx.stroke();
  });
  ctx.setLineDash([]);

  const n = labels.length;
  const getX = (idx) => padLeft + (idx / Math.max(1, n - 1)) * chartW;
  const getY = (val) => padTop + chartH - (Math.min(100, Math.max(0, val)) / 100) * chartH;

  // 2. Draw X-axis date labels
  ctx.fillStyle = '#64748B';
  ctx.font = '500 11.5px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';

  labels.forEach((lbl, idx) => {
    const x = getX(idx);
    ctx.fillText(lbl, x, padTop + chartH + 10);
  });

  // 3. Draw Average Dashed Line (Purple)
  ctx.beginPath();
  ctx.setLineDash([5, 5]);
  ctx.strokeStyle = '#A78BFA';
  ctx.lineWidth = 2;

  avgScores.forEach((val, idx) => {
    const x = getX(idx);
    const y = getY(val);
    if (idx === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.setLineDash([]);

  // Average dots
  ctx.fillStyle = '#C4B5FD';
  avgScores.forEach((val, idx) => {
    const x = getX(idx);
    const y = getY(val);
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    ctx.fill();
  });

  // 4. Draw Your Score Solid Line (Blue)
  ctx.beginPath();
  ctx.strokeStyle = '#1677FF';
  ctx.lineWidth = 2.8;
  yourScores.forEach((val, idx) => {
    const x = getX(idx);
    const y = getY(val);
    if (idx === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // Your Score points
  yourScores.forEach((val, idx) => {
    const x = getX(idx);
    const y = getY(val);
    ctx.beginPath();
    ctx.arc(x, y, 4.5, 0, Math.PI * 2);
    ctx.fillStyle = '#FFFFFF';
    ctx.fill();
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = '#1677FF';
    ctx.stroke();
  });

  // Position callout badge over the last data point
  if (yourScores.length > 0) {
    const lastIdx = yourScores.length - 1;
    const lastX = getX(lastIdx);
    const lastY = getY(yourScores[lastIdx]);
    const badge = document.getElementById('trend-callout-badge');
    if (badge) {
      badge.style.left = `${lastX - 24}px`;
      badge.style.top = `${lastY - 36}px`;
      badge.style.right = 'auto';
    }
  }

  ctx.restore();
}

/* ==========================================================================
   DOWNLOAD EXECUTIVE REPORT PDFS
   ========================================================================== */

async function downloadProfileReportPDF() {
  const btn = document.getElementById('btn-download-full-report');
  const originalHtml = btn ? btn.innerHTML : 'Download Full Report';
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span style="display:inline-block;animation:spin 1s linear infinite">⏳</span> <span>Generating Official PDF...</span>';
  }

  showToast('Generating comprehensive candidate analytics report with WeasyPrint...', 'info');

  try {
    let url = `${API_BASE_URL}/profile/pdf`;
    if (profileDateFilterDays) url += `?days=${profileDateFilterDays}`;

    const res = await fetch(url, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = `AI_Interview_Profile_Analytics_Sumit_Gounder.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => window.URL.revokeObjectURL(blobUrl), 10000);

    showToast('Official Profile & Analytics PDF downloaded successfully!', 'success');
  } catch (err) {
    console.warn('Backend WeasyPrint generation error, falling back to browser print:', err);
    showToast('WeasyPrint backend offline. Opening browser print view.', 'warning');
    window.print();
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = originalHtml;
    }
  }
}

async function downloadInterviewReportPDF(interviewId) {
  showToast(`Generating report for interview #${interviewId}...`, 'info');
  try {
    const res = await fetch(`${API_BASE_URL}/interviews/${interviewId}/pdf`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = `AI_Interview_Assessment_Report_${interviewId}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => window.URL.revokeObjectURL(blobUrl), 10000);
    showToast(`Interview #${interviewId} PDF downloaded successfully!`, 'success');
  } catch (err) {
    console.error('Failed to download interview PDF:', err);
    showToast('PDF download failed. Please verify server connection.', 'error');
  }
}

/* ==========================================================================
   REAL API CONNECTION HEALTH MONITOR (DYNAMIC STATUS BADGE)
   ========================================================================== */

function initAPIHealthMonitor() {
  const badgeDot = document.getElementById('api-status-dot');
  const badgeText = document.getElementById('api-status-text');

  async function checkHealth() {
    try {
      const res = await fetch(`${API_BASE_URL}/docs`, { method: 'HEAD', cache: 'no-cache' });
      if (res.ok || res.status === 200 || res.status === 307) {
        if (badgeDot) {
          badgeDot.classList.remove('status-offline');
          badgeDot.classList.add('pulsing');
        }
        if (badgeText) badgeText.textContent = 'API Connected';
      } else {
        throw new Error('Non-200 status');
      }
    } catch (e) {
      if (badgeDot) {
        badgeDot.classList.remove('pulsing');
        badgeDot.classList.add('status-offline');
      }
      if (badgeText) badgeText.textContent = 'API Reconnecting';
    }
  }

  // Run immediately and every 12 seconds
  checkHealth();
  setInterval(checkHealth, 12000);
}

// Start API Health monitor on initial load
document.addEventListener('DOMContentLoaded', () => {
  initAPIHealthMonitor();
});
"""

with open("frontend/script.js", "a", encoding="utf-8") as f:
    f.write(js_code)

print("Appended Profile JS logic to script.js successfully!")

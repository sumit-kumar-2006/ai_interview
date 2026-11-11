# Script to apply frontend fixes to frontend/script.js
import sys

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace initNavigation
old_nav = """function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  const viewPanels = document.querySelectorAll('.view-panel');

  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      const targetView = link.getAttribute('data-view');

      if ((targetView === 'dashboard' || targetView === 'history') && !authToken) {
        showToast(`Please sign in to access your ${targetView === 'dashboard' ? 'Dashboard' : 'Interview History'}.`, 'warning');
        showAuthModal('login');
        return;
      }

      navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');

      viewPanels.forEach(panel => {
        if (panel.id === `view-${targetView}`) {
          panel.classList.add('active');
        } else {
          panel.classList.remove('active');
        }
      });

      if (targetView === 'dashboard') {
        updateDashboardStats();
      } else if (targetView === 'history') {
        loadInterviewHistory();
      }
    });
  });
}"""

new_nav = """function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');

  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetView = link.getAttribute('data-view');
      if (targetView) {
        navigateToView(targetView);
      }
    });
  });

  // Handle browser back/forward buttons
  window.addEventListener('popstate', (e) => {
    const urlParams = new URLSearchParams(window.location.search);
    const viewParam = urlParams.get('view') || (e.state && e.state.view) || 'landing';
    navigateToView(viewParam, false);
  });

  // Handle in-page anchors smoothly across views
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    const href = anchor.getAttribute('href');
    if (!href || href === '#' || href.startsWith('#login') || href.startsWith('#reg')) return;
    anchor.addEventListener('click', (e) => {
      const targetId = href.substring(1);
      const targetEl = document.getElementById(targetId);
      if (targetEl) {
        e.preventDefault();
        const activeView = document.querySelector('.view-panel.active');
        if (activeView && activeView.id !== 'view-landing') {
          navigateToView('landing', false);
          setTimeout(() => {
            targetEl.scrollIntoView({ behavior: 'smooth' });
          }, 100);
        } else {
          targetEl.scrollIntoView({ behavior: 'smooth' });
        }
      }
    });
  });
}"""

assert old_nav in content, "old_nav not found"
content = content.replace(old_nav, new_nav)

# 2. Replace navigateToView
old_navigate = """function navigateToView(viewName) {
  // Protected Routes Check
  const protectedViews = ['dashboard', 'practice', 'history', 'report', 'interview-setup', 'device-check', 'profile', 'analytics'];
  if (protectedViews.includes(viewName) && !authToken) {
    showToast('Please log in to access candidate workspace.', 'warning');
    showAuthModal('login');
    viewName = 'landing';
  }

  if (viewName === 'practice') {
    document.body.classList.add('in-interview');
  } else {
    document.body.classList.remove('in-interview');
  }

  // Safety Cleanup for Device Check MediaStreams when leaving device-check
  if (viewName !== 'device-check' && typeof stopDeviceCheckStreams === 'function') {
    stopDeviceCheckStreams();
  }

  const viewPanels = document.querySelectorAll('.view-panel');
  const navLinks = document.querySelectorAll('.nav-link');

  navLinks.forEach(link => {
    if (link.getAttribute('data-view') === viewName) link.classList.add('active');
    else link.classList.remove('active');
  });

  const navDashBtn = document.getElementById('nav-dash-btn');
  const navPracticeBtn = document.getElementById('nav-practice-btn');
  const navProfileBtn = document.getElementById('nav-profile-btn');
  const navAnalyticsBtn = document.getElementById('nav-analytics-btn');
  if (navDashBtn) {
    if (viewName === 'dashboard') navDashBtn.classList.add('active');
    else navDashBtn.classList.remove('active');
  }
  if (navPracticeBtn) {
    if (viewName === 'interview-setup' || viewName === 'practice' || viewName === 'device-check') navPracticeBtn.classList.add('active');
    else navPracticeBtn.classList.remove('active');
  }
  if (navProfileBtn) {
    if (viewName === 'profile') navProfileBtn.classList.add('active');
    else navProfileBtn.classList.remove('active');
  }
  if (navAnalyticsBtn) {
    if (viewName === 'analytics') navAnalyticsBtn.classList.add('active');
    else navAnalyticsBtn.classList.remove('active');
  }

  const targetPanelId = (viewName === 'analytics') ? 'view-profile' : `view-${viewName}`;

  viewPanels.forEach(panel => {
    if (panel.id === targetPanelId) {
      panel.classList.add('active');
    } else {
      panel.classList.remove('active');
    }
  });

  if (viewName === 'dashboard') {
    updateDashboardStats();
  } else if (viewName === 'profile' || viewName === 'analytics') {
    initProfileAnalyticsPage();
    if (viewName === 'analytics') {
      setTimeout(() => {
        const chartsSection = document.getElementById('profile-analytics-charts');
        if (chartsSection) chartsSection.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    }
  } else if (viewName === 'history') {
    loadInterviewHistory();
  } else if (viewName === 'interview-setup') {
    initInterviewSetupPage();
  } else if (viewName === 'device-check') {
    initDeviceCheckPage();
  }
}"""

new_navigate = """function navigateToView(viewName, pushState = true) {
  // Protected Routes Check
  const protectedViews = ['dashboard', 'practice', 'history', 'report', 'interview-setup', 'device-check', 'profile', 'analytics', 'admin'];
  if (protectedViews.includes(viewName) && !authToken) {
    showToast('Please log in to access candidate workspace.', 'warning');
    showAuthModal('login');
    viewName = 'landing';
  }

  // Admin Route Authorization Check
  if (viewName === 'admin' && (!currentUser || !currentUser.is_admin)) {
    showToast('Access denied: Administrator privileges required.', 'error');
    viewName = 'dashboard';
  }

  if (viewName === 'practice') {
    document.body.classList.add('in-interview');
  } else {
    document.body.classList.remove('in-interview');
  }

  // Safety Cleanup for Device Check MediaStreams when leaving device-check
  if (viewName !== 'device-check' && typeof stopDeviceCheckStreams === 'function') {
    stopDeviceCheckStreams();
  }

  const viewPanels = document.querySelectorAll('.view-panel');
  const navLinks = document.querySelectorAll('.nav-link');

  navLinks.forEach(link => {
    if (link.getAttribute('data-view') === viewName) link.classList.add('active');
    else link.classList.remove('active');
  });

  const navDashBtn = document.getElementById('nav-dash-btn');
  const navPracticeBtn = document.getElementById('nav-practice-btn');
  const navProfileBtn = document.getElementById('nav-profile-btn');
  const navAnalyticsBtn = document.getElementById('nav-analytics-btn');
  const navAdminBtn = document.getElementById('nav-admin-btn');
  if (navDashBtn) {
    if (viewName === 'dashboard') navDashBtn.classList.add('active');
    else navDashBtn.classList.remove('active');
  }
  if (navPracticeBtn) {
    if (viewName === 'interview-setup' || viewName === 'practice' || viewName === 'device-check') navPracticeBtn.classList.add('active');
    else navPracticeBtn.classList.remove('active');
  }
  if (navProfileBtn) {
    if (viewName === 'profile') navProfileBtn.classList.add('active');
    else navProfileBtn.classList.remove('active');
  }
  if (navAnalyticsBtn) {
    if (viewName === 'analytics') navAnalyticsBtn.classList.add('active');
    else navAnalyticsBtn.classList.remove('active');
  }
  if (navAdminBtn) {
    if (viewName === 'admin') navAdminBtn.classList.add('active');
    else navAdminBtn.classList.remove('active');
  }

  const targetPanelId = (viewName === 'analytics') ? 'view-profile' : `view-${viewName}`;

  viewPanels.forEach(panel => {
    if (panel.id === targetPanelId) {
      panel.classList.add('active');
    } else {
      panel.classList.remove('active');
    }
  });

  if (pushState && window.history && window.history.pushState) {
    try {
      const url = new URL(window.location);
      url.searchParams.set('view', viewName);
      window.history.pushState({ view: viewName }, '', url.toString());
    } catch (err) {
      console.debug('History pushState error:', err);
    }
  }

  if (viewName === 'dashboard') {
    updateDashboardStats();
  } else if (viewName === 'profile' || viewName === 'analytics') {
    initProfileAnalyticsPage();
    if (viewName === 'analytics') {
      setTimeout(() => {
        const chartsSection = document.getElementById('profile-analytics-charts');
        if (chartsSection) chartsSection.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    }
  } else if (viewName === 'history') {
    loadInterviewHistory();
  } else if (viewName === 'interview-setup') {
    initInterviewSetupPage();
  } else if (viewName === 'device-check') {
    initDeviceCheckPage();
  } else if (viewName === 'admin') {
    initAdminPage();
  }
}"""

assert old_navigate in content, "old_navigate not found"
content = content.replace(old_navigate, new_navigate)

# 3. Call initLegalModals in initQuestionWorkspace
old_workspace_end = """  const backHomeBtn = document.getElementById('btn-back-home');
  if (backHomeBtn) backHomeBtn.addEventListener('click', goBackHome);
}"""

new_workspace_end = """  const backHomeBtn = document.getElementById('btn-back-home');
  if (backHomeBtn) backHomeBtn.addEventListener('click', goBackHome);

  initLegalModals();
}"""

assert old_workspace_end in content, "old_workspace_end not found"
content = content.replace(old_workspace_end, new_workspace_end)

# 4. Fix goBackHome toast
old_goback = """  if (authToken) {
    navigateToView('dashboard');
  } else {
    navigateToView('landing');
  }
  showToast('Returned to Dashboard.', 'info');"""

new_goback = """  if (authToken) {
    navigateToView('dashboard');
  } else {
    navigateToView('landing');
  }
  showToast(authToken ? 'Returned to Dashboard.' : 'Returned to Home.', 'info');"""

assert old_goback in content, "old_goback not found"
content = content.replace(old_goback, new_goback)

# 5. Fix validateAuthSession requestedView
old_val = """      const requestedView = urlParams.get('view') || (window.location.hash ? window.location.hash.replace('#', '') : null);
      if (requestedView && ['dashboard', 'practice', 'history', 'report', 'interview-setup', 'device-check', 'landing', 'profile', 'analytics'].includes(requestedView)) {
        navigateToView(requestedView);
      } else if (!window.location.hash || window.location.hash === '#dashboard' || urlParams.has('auto_login')) {
        navigateToView('dashboard');
      }"""

new_val = """      const requestedView = urlParams.get('view') || (window.location.hash ? window.location.hash.replace('#', '') : null);
      if (requestedView && ['dashboard', 'practice', 'history', 'report', 'interview-setup', 'device-check', 'landing', 'profile', 'analytics', 'admin'].includes(requestedView)) {
        navigateToView(requestedView, false);
      } else if (!window.location.hash || window.location.hash === '#dashboard' || urlParams.has('auto_login')) {
        navigateToView('dashboard', false);
      }"""

assert old_val in content, "old_val not found"
content = content.replace(old_val, new_val)

# 6. Update updateAuthWidget with admin links
old_auth_widget = """    const logoutBtn = document.getElementById('nav-logout-btn');
    if (logoutBtn) logoutBtn.onclick = () => handleLogout();"""

new_auth_widget = """    const logoutBtn = document.getElementById('nav-logout-btn');
    if (logoutBtn) logoutBtn.onclick = () => handleLogout();

    // Admin Navigation button and dropdown item
    const navAdminBtn = document.getElementById('nav-admin-btn');
    const npmdItemAdmin = document.getElementById('npmd-item-admin');
    if (currentUser && currentUser.is_admin) {
      if (navAdminBtn) {
        navAdminBtn.classList.remove('hidden');
        navAdminBtn.onclick = () => navigateToView('admin');
      }
      if (npmdItemAdmin) {
        npmdItemAdmin.classList.remove('hidden');
        npmdItemAdmin.onclick = () => { closeNavProfileDropdown(); navigateToView('admin'); };
      }
    } else {
      if (navAdminBtn) navAdminBtn.classList.add('hidden');
      if (npmdItemAdmin) npmdItemAdmin.classList.add('hidden');
    }"""

assert old_auth_widget in content, "old_auth_widget not found"
content = content.replace(old_auth_widget, new_auth_widget)

# Also in else block of updateAuthWidget
old_auth_else = """  } else {
    if (mainNav) mainNav.classList.remove('hidden');
    if (authNav) authNav.classList.add('hidden');
    if (unauthActions) unauthActions.classList.remove('hidden');
    if (authActions) authActions.classList.add('hidden');
  }"""

new_auth_else = """  } else {
    if (mainNav) mainNav.classList.remove('hidden');
    if (authNav) authNav.classList.add('hidden');
    if (unauthActions) unauthActions.classList.remove('hidden');
    if (authActions) authActions.classList.add('hidden');

    const navAdminBtn = document.getElementById('nav-admin-btn');
    const npmdItemAdmin = document.getElementById('npmd-item-admin');
    if (navAdminBtn) navAdminBtn.classList.add('hidden');
    if (npmdItemAdmin) npmdItemAdmin.classList.add('hidden');
  }"""

assert old_auth_else in content, "old_auth_else not found"
content = content.replace(old_auth_else, new_auth_else)

# 7. Fix renderProfilePageData and fallbackComputeAndRenderAnalytics
old_prof_render = """  const countEl = document.getElementById('profile-interviews-count');
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
  setElText('det-metric-conf', `${parseFloat(perf.confidence || 88.7).toFixed(1)}%`);"""

new_prof_render = """  const countEl = document.getElementById('profile-interviews-count');
  const totalCount = stats.total_interviews !== undefined ? stats.total_interviews : 0;
  if (countEl) countEl.textContent = totalCount;

  const bestScoreVal = stats.best_score !== undefined ? parseFloat(stats.best_score) : 0.0;
  const bestEl = document.getElementById('profile-best-score');
  if (bestEl) bestEl.textContent = `${bestScoreVal.toFixed(1)}%`;

  // 2. Top 4 Summary Cards
  const overallValNum = stats.overall_score !== undefined ? parseFloat(stats.overall_score) : 0.0;
  const overallVal = overallValNum.toFixed(1);
  const cardOverallEl = document.getElementById('card-overall-score');
  if (cardOverallEl) cardOverallEl.textContent = `${overallVal}%`;

  const donutFill = document.getElementById('card-donut-fill');
  if (donutFill) {
    const radius = 40;
    const circumference = 2 * Math.PI * radius; // 251.2
    const offset = circumference - (overallValNum / 100) * circumference;
    donutFill.style.strokeDashoffset = offset;
  }

  const trendOverallEl = document.getElementById('trend-overall-val');
  if (trendOverallEl) trendOverallEl.innerHTML = `<span class=\"arrow\">↑</span> ${trends.overall || '+0.0%'}`;

  const cardInterviewsEl = document.getElementById('card-total-interviews');
  if (cardInterviewsEl) cardInterviewsEl.textContent = totalCount;

  const trendInterviewsEl = document.getElementById('trend-interviews-val');
  if (trendInterviewsEl) trendInterviewsEl.innerHTML = `<span class=\"arrow\">↑</span> ${trends.interviews || `${totalCount} total`}`;

  const cardTimeEl = document.getElementById('card-total-time');
  if (cardTimeEl) cardTimeEl.textContent = stats.total_practice_time || '0m';

  const trendTimeEl = document.getElementById('trend-time-val');
  if (trendTimeEl) trendTimeEl.innerHTML = `<span class=\"arrow\">↑</span> ${trends.time || '0m'}`;

  const avgScoreNum = stats.avg_score !== undefined ? parseFloat(stats.avg_score) : 0.0;
  const cardAvgEl = document.getElementById('card-avg-score');
  if (cardAvgEl) cardAvgEl.textContent = `${avgScoreNum.toFixed(1)}%`;

  const trendAvgEl = document.getElementById('trend-avg-val');
  if (trendAvgEl) trendAvgEl.innerHTML = `<span class=\"arrow\">↑</span> ${trends.avg || '+0.0%'}`;

  // 3. Radar Chart
  const radarCanvas = document.getElementById('perf-radar-canvas');
  if (radarCanvas) {
    const hasData = totalCount > 0;
    const yourRadarScores = hasData ? [
      perf.answer_quality || 0.0,
      perf.communication || 0.0,
      perf.visual_presence || 0.0,
      perf.question_performance || 0.0,
      perf.confidence || 0.0
    ] : [0, 0, 0, 0, 0];
    const avgRadarScores = [70, 70, 70, 70, 70];
    renderRadarChart(radarCanvas, yourRadarScores, avgRadarScores);
  }

  // 4. Score Trend Line Chart
  const trendCanvas = document.getElementById('score-trend-canvas');
  if (trendCanvas) {
    const trendData = data.trend_chart || {};
    const labels = trendData.labels || [];
    const yourScores = trendData.your_scores || [];
    const avgScores = trendData.avg_scores || [];
    renderScoreTrendChart(trendCanvas, labels, yourScores, avgScores);

    // Callout badge value
    const calloutVal = document.getElementById('trend-callout-val');
    if (calloutVal) {
      if (yourScores.length > 0) {
        calloutVal.textContent = `${yourScores[yourScores.length - 1].toFixed(1)}%`;
      } else {
        calloutVal.textContent = '0.0%';
      }
    }
  }

  // 5. Detailed Metrics (5 Mini Boxes)
  const setElText = (id, text) => { const el = document.getElementById(id); if (el) el.textContent = text; };
  setElText('det-metric-quality', `${parseFloat(perf.answer_quality || 0.0).toFixed(1)}%`);
  setElText('det-metric-comm', `${parseFloat(perf.communication || 0.0).toFixed(1)}%`);
  setElText('det-metric-visual', `${parseFloat(perf.visual_presence || 0.0).toFixed(1)}%`);
  setElText('det-metric-qp', `${parseFloat(perf.question_performance || 0.0).toFixed(1)}%`);
  setElText('det-metric-conf', `${parseFloat(perf.confidence || 0.0).toFixed(1)}%`);"""

assert old_prof_render in content, "old_prof_render not found"
content = content.replace(old_prof_render, new_prof_render)

# Fallback compute replacement
old_fallback = """// Fallback computation when /profile/analytics is not reached
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
}"""

new_fallback = """// Fallback computation when /profile/analytics is not reached
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

  const total = userInterviews.length;
  const scores = userInterviews.map(i => parseFloat(i.overall_score || 0)).filter(s => s > 0);
  const avg = scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length) : 0.0;
  const best = scores.length ? Math.max(...scores) : 0.0;

  const data = {
    profile: {
      name: (userProfile && userProfile.name) || (currentUser && currentUser.full_name) || 'Candidate',
      education: (userProfile && userProfile.education) || 'Degree Candidate',
      college: (userProfile && userProfile.college) || '',
      is_verified: true
    },
    stats: {
      joined_date: 'Active',
      total_interviews: total,
      total_practice_time: `${Math.round(total * 8)}m`,
      overall_score: avg,
      avg_score: avg,
      best_score: best,
      trends: { overall: '+0.0%', interviews: `${total} total`, time: `${Math.round(total * 8)}m`, avg: '+0.0%' }
    },
    performance: {
      answer_quality: avg,
      communication: avg,
      visual_presence: avg,
      question_performance: avg,
      confidence: avg
    },
    skills: [
      { name: 'Communication', score: avg },
      { name: 'Technical Knowledge', score: avg },
      { name: 'Problem Solving', score: avg },
      { name: 'Confidence', score: avg }
    ],
    trend_chart: {
      labels: userInterviews.slice(-5).map(i => i.completed_at ? i.completed_at.slice(5, 10) : 'Session'),
      your_scores: userInterviews.slice(-5).map(i => parseFloat(i.overall_score || 0)),
      avg_scores: userInterviews.slice(-5).map(() => 75.0)
    },
    interviews: userInterviews.slice(0, 3).map(inv => ({
      id: inv.id,
      target_role: inv.target_role || 'Technical Interview',
      completed_at_str: inv.completed_at ? inv.completed_at.slice(0, 16).replace('T', ' ') : 'Recent Session',
      overall_score: parseFloat(inv.overall_score || 0)
    }))
  };

  cachedAnalyticsData = data;
  renderProfilePageData(data);
}"""

assert old_fallback in content, "old_fallback not found"
content = content.replace(old_fallback, new_fallback)

# 8. Append Admin Panel & Legal Modals Module to end
admin_and_modals_module = """

/* ==========================================================================
   LEGAL MODALS & FEATURE CTA WIREUP
   ========================================================================== */

function initLegalModals() {
  const privacyModal = document.getElementById('privacy-modal');
  const termsModal = document.getElementById('terms-modal');
  
  // Privacy Links
  document.querySelectorAll('.policy-privacy-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      if (privacyModal) privacyModal.classList.remove('hidden');
    });
  });

  const privacyClose = document.getElementById('privacy-modal-close');
  if (privacyClose) privacyClose.onclick = () => { if (privacyModal) privacyModal.classList.add('hidden'); };
  const privacyAgree = document.getElementById('btn-privacy-agree');
  if (privacyAgree) privacyAgree.onclick = () => { if (privacyModal) privacyModal.classList.add('hidden'); };

  // Terms Links
  document.querySelectorAll('.policy-terms-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      if (termsModal) termsModal.classList.remove('hidden');
    });
  });

  const termsClose = document.getElementById('terms-modal-close');
  if (termsClose) termsClose.onclick = () => { if (termsModal) termsModal.classList.add('hidden'); };
  const termsAgree = document.getElementById('btn-terms-agree');
  if (termsAgree) termsAgree.onclick = () => { if (termsModal) termsModal.classList.add('hidden'); };

  // Setup footer login link
  const setupFooterLogin = document.getElementById('setup-footer-login-link');
  if (setupFooterLogin) {
    setupFooterLogin.onclick = (e) => {
      e.preventDefault();
      showAuthModal('login');
    };
  }

  // Feature circular arrow buttons
  document.querySelectorAll('.feat-circle-arrow').forEach(btn => {
    btn.onclick = (e) => {
      e.preventDefault();
      handleStartInterviewClick();
    };
  });
}

/* ==========================================================================
   ADMIN PANEL MODULE (ROLE-BASED GOVERNANCE & RECORD MANAGEMENT)
   ========================================================================== */

let adminUsersCurrentPage = 1;
let adminUsersSearchQuery = '';
let adminUsersTotalCount = 0;

let adminInvCurrentPage = 1;
let adminInvSearchQuery = '';
let adminInvRoleFilter = 'All';
let adminInvTotalCount = 0;

let adminPendingDeleteAction = null;

function initAdminPage() {
  loadAdminStats();
  loadAdminUsers(adminUsersCurrentPage, adminUsersSearchQuery);
  loadAdminInterviews(adminInvCurrentPage, adminInvSearchQuery, adminInvRoleFilter);
  setupAdminEventListeners();
}

function setupAdminEventListeners() {
  // Refresh & Back to Dashboard
  const refreshBtn = document.getElementById('btn-admin-refresh');
  if (refreshBtn) refreshBtn.onclick = () => {
    loadAdminStats();
    loadAdminUsers(adminUsersCurrentPage, adminUsersSearchQuery);
    loadAdminInterviews(adminInvCurrentPage, adminInvSearchQuery, adminInvRoleFilter);
    showToast('Admin metrics refreshed from database.', 'success');
  };

  const backDashBtn = document.getElementById('btn-admin-back-dash');
  if (backDashBtn) backDashBtn.onclick = () => navigateToView('dashboard');

  // Tabs
  const tabUsersBtn = document.getElementById('admin-tab-users-btn');
  const tabInvBtn = document.getElementById('admin-tab-interviews-btn');
  const panelUsers = document.getElementById('admin-panel-users');
  const panelInv = document.getElementById('admin-panel-interviews');

  if (tabUsersBtn && tabInvBtn) {
    tabUsersBtn.onclick = () => {
      tabUsersBtn.classList.add('active');
      tabInvBtn.classList.remove('active');
      if (panelUsers) panelUsers.classList.remove('hidden');
      if (panelInv) panelInv.classList.add('hidden');
    };
    tabInvBtn.onclick = () => {
      tabInvBtn.classList.add('active');
      tabUsersBtn.classList.remove('active');
      if (panelInv) panelInv.classList.remove('hidden');
      if (panelUsers) panelUsers.classList.add('hidden');
    };
  }

  // Users Tab Search & Pagination
  const searchUsersInput = document.getElementById('admin-users-search-input');
  const searchUsersBtn = document.getElementById('btn-admin-search-users');
  const clearUsersBtn = document.getElementById('btn-admin-clear-users');
  const prevUsersBtn = document.getElementById('btn-admin-users-prev');
  const nextUsersBtn = document.getElementById('btn-admin-users-next');

  if (searchUsersBtn && searchUsersInput) {
    searchUsersBtn.onclick = () => {
      adminUsersSearchQuery = searchUsersInput.value.trim();
      adminUsersCurrentPage = 1;
      loadAdminUsers(adminUsersCurrentPage, adminUsersSearchQuery);
    };
    searchUsersInput.onkeydown = (e) => {
      if (e.key === 'Enter') {
        adminUsersSearchQuery = searchUsersInput.value.trim();
        adminUsersCurrentPage = 1;
        loadAdminUsers(adminUsersCurrentPage, adminUsersSearchQuery);
      }
    };
  }

  if (clearUsersBtn && searchUsersInput) {
    clearUsersBtn.onclick = () => {
      searchUsersInput.value = '';
      adminUsersSearchQuery = '';
      adminUsersCurrentPage = 1;
      loadAdminUsers(adminUsersCurrentPage, '');
    };
  }

  if (prevUsersBtn) {
    prevUsersBtn.onclick = () => {
      if (adminUsersCurrentPage > 1) {
        adminUsersCurrentPage--;
        loadAdminUsers(adminUsersCurrentPage, adminUsersSearchQuery);
      }
    };
  }

  if (nextUsersBtn) {
    nextUsersBtn.onclick = () => {
      const maxPages = Math.ceil(adminUsersTotalCount / 10) || 1;
      if (adminUsersCurrentPage < maxPages) {
        adminUsersCurrentPage++;
        loadAdminUsers(adminUsersCurrentPage, adminUsersSearchQuery);
      }
    };
  }

  // Interviews Tab Search, Filter & Pagination
  const searchInvInput = document.getElementById('admin-inv-search-input');
  const filterInvRole = document.getElementById('admin-inv-role-filter');
  const searchInvBtn = document.getElementById('btn-admin-search-inv');
  const prevInvBtn = document.getElementById('btn-admin-inv-prev');
  const nextInvBtn = document.getElementById('btn-admin-inv-next');

  if (searchInvBtn && searchInvInput && filterInvRole) {
    const doFilter = () => {
      adminInvSearchQuery = searchInvInput.value.trim();
      adminInvRoleFilter = filterInvRole.value;
      adminInvCurrentPage = 1;
      loadAdminInterviews(adminInvCurrentPage, adminInvSearchQuery, adminInvRoleFilter);
    };
    searchInvBtn.onclick = doFilter;
    filterInvRole.onchange = doFilter;
    searchInvInput.onkeydown = (e) => {
      if (e.key === 'Enter') doFilter();
    };
  }

  if (prevInvBtn) {
    prevInvBtn.onclick = () => {
      if (adminInvCurrentPage > 1) {
        adminInvCurrentPage--;
        loadAdminInterviews(adminInvCurrentPage, adminInvSearchQuery, adminInvRoleFilter);
      }
    };
  }

  if (nextInvBtn) {
    nextInvBtn.onclick = () => {
      const maxPages = Math.ceil(adminInvTotalCount / 10) || 1;
      if (adminInvCurrentPage < maxPages) {
        adminInvCurrentPage++;
        loadAdminInterviews(adminInvCurrentPage, adminInvSearchQuery, adminInvRoleFilter);
      }
    };
  }

  // Delete modal dialog buttons
  const modalClose = document.getElementById('admin-delete-modal-close');
  const cancelBtn = document.getElementById('btn-admin-cancel-delete');
  const confirmBtn = document.getElementById('btn-admin-confirm-delete');
  const deleteModal = document.getElementById('admin-delete-modal');

  const closeDeleteModal = () => {
    if (deleteModal) deleteModal.classList.add('hidden');
    adminPendingDeleteAction = null;
  };

  if (modalClose) modalClose.onclick = closeDeleteModal;
  if (cancelBtn) cancelBtn.onclick = closeDeleteModal;
  if (confirmBtn) {
    confirmBtn.onclick = async () => {
      if (typeof adminPendingDeleteAction === 'function') {
        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Deleting...';
        try {
          await adminPendingDeleteAction();
        } finally {
          confirmBtn.disabled = false;
          confirmBtn.textContent = 'Confirm Delete';
          closeDeleteModal();
        }
      }
    };
  }
}

async function loadAdminStats() {
  try {
    const res = await fetch(`${API_BASE_URL}/admin/stats`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      if (res.status === 403) {
        showToast('Admin access forbidden.', 'error');
        navigateToView('dashboard');
      }
      return;
    }
    const stats = await res.json();
    const elUsers = document.getElementById('admin-stat-users');
    const elInv = document.getElementById('admin-stat-interviews');
    const elAvg = document.getElementById('admin-stat-avg-score');
    const elHours = document.getElementById('admin-stat-hours');

    if (elUsers) elUsers.textContent = stats.total_users ?? 0;
    if (elInv) elInv.textContent = stats.total_interviews ?? 0;
    if (elAvg) elAvg.textContent = `${(stats.average_score ?? 0).toFixed(1)}%`;
    if (elHours) elHours.textContent = `${(stats.total_practice_hours ?? 0).toFixed(1)} hrs`;
  } catch (err) {
    console.error('Failed to load admin stats:', err);
  }
}

async function loadAdminUsers(page = 1, search = '') {
  const tbody = document.getElementById('admin-users-tbody');
  const pageInfo = document.getElementById('admin-users-page-info');
  const prevBtn = document.getElementById('btn-admin-users-prev');
  const nextBtn = document.getElementById('btn-admin-users-next');

  if (tbody) tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4">Loading candidates...</td></tr>';

  try {
    const params = new URLSearchParams({ page: page, limit: 10 });
    if (search) params.append('search', search);

    const res = await fetch(`${API_BASE_URL}/admin/users?${params.toString()}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch admin users');

    const data = await res.json();
    adminUsersTotalCount = data.total || 0;
    const users = data.users || [];

    if (tbody) {
      if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4" style="color: #64748B;">No candidates found matching the query.</td></tr>';
      } else {
        tbody.innerHTML = '';
        users.forEach(u => {
          const tr = document.createElement('tr');
          const isCurrentUser = currentUser && currentUser.id === u.id;
          const roleBadge = u.is_admin 
            ? '<span class="admin-role-badge admin">Admin</span>' 
            : '<span class="admin-role-badge candidate">Candidate</span>';
          
          const toggleRoleBtnHtml = isCurrentUser ? '' : `
            <button class="btn btn-secondary btn-xs btn-toggle-role" data-id="${u.id}" data-admin="${u.is_admin ? 0 : 1}" title="Toggle role">
              ${u.is_admin ? 'Demote' : 'Make Admin'}
            </button>
          `;
          const deleteBtnHtml = isCurrentUser ? '' : `
            <button class="btn btn-danger btn-xs btn-del-user" data-id="${u.id}" data-email="${escapeHtml(u.email)}" title="Delete candidate">
              Delete
            </button>
          `;

          tr.innerHTML = `
            <td>#${u.id}</td>
            <td>
              <div class="user-cell">
                <span class="user-cell-name">${escapeHtml(u.full_name || 'Candidate')}</span>
                <span class="user-cell-email">${escapeHtml(u.email)}</span>
              </div>
            </td>
            <td>${escapeHtml(u.target_role || 'General Software')}</td>
            <td>${u.interview_count}</td>
            <td><strong>${u.average_score.toFixed(1)}%</strong></td>
            <td>${roleBadge}</td>
            <td><span class="date-sub">${escapeHtml(u.created_at ? u.created_at.slice(0, 10) : 'Recent')}</span></td>
            <td style="text-align: right; white-space: nowrap;">
              ${toggleRoleBtnHtml}
              ${deleteBtnHtml}
            </td>
          `;

          // Event handlers
          const roleBtn = tr.querySelector('.btn-toggle-role');
          if (roleBtn) {
            roleBtn.onclick = () => handleAdminToggleRole(u.id, !u.is_admin);
          }
          const delBtn = tr.querySelector('.btn-del-user');
          if (delBtn) {
            delBtn.onclick = () => openAdminDeleteUserModal(u.id, u.email);
          }

          tbody.appendChild(tr);
        });
      }
    }

    // Update pagination
    const maxPages = Math.ceil(adminUsersTotalCount / 10) || 1;
    const startIdx = adminUsersTotalCount === 0 ? 0 : (page - 1) * 10 + 1;
    const endIdx = Math.min(page * 10, adminUsersTotalCount);
    if (pageInfo) pageInfo.textContent = `Showing ${startIdx} to ${endIdx} of ${adminUsersTotalCount} candidates (Page ${page}/${maxPages})`;
    if (prevBtn) prevBtn.disabled = page <= 1;
    if (nextBtn) nextBtn.disabled = page >= maxPages;

  } catch (err) {
    console.error('Failed to load admin users:', err);
    if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4" style="color: #DC2626;">Error: ${err.message}</td></tr>`;
  }
}

async function handleAdminToggleRole(userId, newIsAdmin) {
  try {
    const res = await fetch(`${API_BASE_URL}/admin/users/${userId}/role`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify({ is_admin: newIsAdmin })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to update user role');
    }
    showToast(`User role updated to ${newIsAdmin ? 'Admin' : 'Candidate'}.`, 'success');
    loadAdminUsers(adminUsersCurrentPage, adminUsersSearchQuery);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function openAdminDeleteUserModal(userId, email) {
  const modal = document.getElementById('admin-delete-modal');
  const msgEl = document.getElementById('admin-delete-msg');
  if (msgEl) {
    msgEl.innerHTML = `Are you sure you want to permanently delete candidate <strong>${escapeHtml(email)}</strong> (ID #${userId})?<br><br>This will cascade and remove all associated interviews, question responses, and profile records.`;
  }
  adminPendingDeleteAction = async () => {
    const res = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to delete user');
    }
    showToast(`Candidate #${userId} deleted successfully.`, 'success');
    loadAdminStats();
    loadAdminUsers(adminUsersCurrentPage, adminUsersSearchQuery);
  };
  if (modal) modal.classList.remove('hidden');
}

async function loadAdminInterviews(page = 1, search = '', role = 'All') {
  const tbody = document.getElementById('admin-inv-tbody');
  const pageInfo = document.getElementById('admin-inv-page-info');
  const prevBtn = document.getElementById('btn-admin-inv-prev');
  const nextBtn = document.getElementById('btn-admin-inv-next');

  if (tbody) tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4">Loading interview records...</td></tr>';

  try {
    const params = new URLSearchParams({ page: page, limit: 10 });
    if (search) params.append('search', search);
    if (role && role !== 'All') params.append('role', role);

    const res = await fetch(`${API_BASE_URL}/admin/interviews?${params.toString()}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch admin interviews');

    const data = await res.json();
    adminInvTotalCount = data.total || 0;
    const interviews = data.interviews || [];

    if (tbody) {
      if (interviews.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4" style="color: #64748B;">No interview sessions found matching the filter.</td></tr>';
      } else {
        tbody.innerHTML = '';
        interviews.forEach(inv => {
          const tr = document.createElement('tr');
          const score = inv.overall_score ?? 0;
          let scoreBadge = `<span class="score-badge badge-green">${score.toFixed(1)}%</span>`;
          if (score < 70) scoreBadge = `<span class="score-badge badge-amber">${score.toFixed(1)}%</span>`;
          else if (score < 85) scoreBadge = `<span class="score-badge badge-blue">${score.toFixed(1)}%</span>`;

          tr.innerHTML = `
            <td>#${inv.id}</td>
            <td>
              <div class="user-cell">
                <span class="user-cell-name">${escapeHtml(inv.candidate_name || 'Candidate')}</span>
                <span class="user-cell-email">${escapeHtml(inv.candidate_email || '')}</span>
              </div>
            </td>
            <td>${escapeHtml(inv.target_role || 'Developer')}</td>
            <td>${inv.question_count} Qs</td>
            <td>${inv.duration_minutes}m</td>
            <td>${scoreBadge}</td>
            <td><span class="date-sub">${escapeHtml(inv.completed_at ? inv.completed_at.slice(0, 16).replace('T', ' ') : 'Recent')}</span></td>
            <td style="text-align: right; white-space: nowrap;">
              <button class="btn btn-secondary btn-xs btn-view-pdf" data-id="${inv.id}" title="Download PDF Report">
                PDF
              </button>
              <button class="btn btn-danger btn-xs btn-del-inv" data-id="${inv.id}" title="Delete session">
                Delete
              </button>
            </td>
          `;

          // Handlers
          const pdfBtn = tr.querySelector('.btn-view-pdf');
          if (pdfBtn) {
            pdfBtn.onclick = () => downloadInterviewReportPDF(inv.id);
          }
          const delBtn = tr.querySelector('.btn-del-inv');
          if (delBtn) {
            delBtn.onclick = () => openAdminDeleteInterviewModal(inv.id);
          }

          tbody.appendChild(tr);
        });
      }
    }

    // Update pagination
    const maxPages = Math.ceil(adminInvTotalCount / 10) || 1;
    const startIdx = adminInvTotalCount === 0 ? 0 : (page - 1) * 10 + 1;
    const endIdx = Math.min(page * 10, adminInvTotalCount);
    if (pageInfo) pageInfo.textContent = `Showing ${startIdx} to ${endIdx} of ${adminInvTotalCount} sessions (Page ${page}/${maxPages})`;
    if (prevBtn) prevBtn.disabled = page <= 1;
    if (nextBtn) nextBtn.disabled = page >= maxPages;

  } catch (err) {
    console.error('Failed to load admin interviews:', err);
    if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4" style="color: #DC2626;">Error: ${err.message}</td></tr>`;
  }
}

function openAdminDeleteInterviewModal(interviewId) {
  const modal = document.getElementById('admin-delete-modal');
  const msgEl = document.getElementById('admin-delete-msg');
  if (msgEl) {
    msgEl.innerHTML = `Are you sure you want to permanently delete interview session <strong>#${interviewId}</strong>?<br><br>All evaluated question audio records and scores under this session will be permanently removed.`;
  }
  adminPendingDeleteAction = async () => {
    const res = await fetch(`${API_BASE_URL}/admin/interviews/${interviewId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to delete interview');
    }
    showToast(`Interview #${interviewId} deleted successfully.`, 'success');
    loadAdminStats();
    loadAdminInterviews(adminInvCurrentPage, adminInvSearchQuery, adminInvRoleFilter);
  };
  if (modal) modal.classList.remove('hidden');
}
"""

content += admin_and_modals_module

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully applied frontend script fixes!")


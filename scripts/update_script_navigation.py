import os
import sys

with open("frontend/script.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Add intendedViewAfterLogin global variable
if "let intendedViewAfterLogin" not in js:
    js = js.replace("let currentUploadedResume = null;", "let currentUploadedResume = null;\nlet intendedViewAfterLogin = 'dashboard';")
    print("Added intendedViewAfterLogin global variable.")

# 2. Update navigateToView in script.js
old_nav_code = '''  // Protected Routes Check
  const protectedViews = ['dashboard', 'practice', 'history', 'report', 'interview-setup', 'device-check', 'profile', 'analytics', 'admin'];
  if (protectedViews.includes(viewName) && !authToken) {
    showToast('Please log in to access candidate workspace.', 'warning');
    showAuthModal('login');
    viewName = 'landing';
  }'''

new_nav_code = '''  // Protected Routes Check
  const protectedViews = ['dashboard', 'practice', 'history', 'report', 'interview-setup', 'device-check', 'profile', 'analytics', 'admin'];
  if (protectedViews.includes(viewName) && !authToken) {
    intendedViewAfterLogin = viewName;
    showToast('Please log in to access candidate workspace.', 'warning');
    showAuthModal('login');
    viewName = 'landing';
  }'''

if old_nav_code in js:
    js = js.replace(old_nav_code, new_nav_code, 1)
    print("Updated protected routes check in navigateToView.")
else:
    print("WARNING: old_nav_code not found in script.js")

# 3. Update nav button highlighting in navigateToView
old_nav_highlighting = '''  const navDashBtn = document.getElementById('nav-dash-btn');
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
  } else if (viewName === 'history') {'''

new_nav_highlighting = '''  const navHomeBtn = document.getElementById('nav-home-btn');
  const navDashBtn = document.getElementById('nav-dash-btn');
  const navPracticeBtn = document.getElementById('nav-practice-btn');
  const navProfileBtn = document.getElementById('nav-profile-btn');
  const navAnalyticsBtn = document.getElementById('nav-analytics-btn');
  const navAdminBtn = document.getElementById('nav-admin-btn');
  if (navHomeBtn) {
    if (viewName === 'landing') navHomeBtn.classList.add('active');
    else navHomeBtn.classList.remove('active');
  }
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

  // Dedicated panel resolution for Profile, Analytics and all views
  const targetPanelId = `view-${viewName}`;

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
  } else if (viewName === 'profile') {
    initProfilePage();
  } else if (viewName === 'analytics') {
    initAnalyticsPage();
  } else if (viewName === 'history') {'''

if old_nav_highlighting in js:
    js = js.replace(old_nav_highlighting, new_nav_highlighting, 1)
    print("Updated panel switching and nav highlighting in navigateToView.")
else:
    print("WARNING: old_nav_highlighting not found in script.js")

# 4. Update initNavigation to bind all buttons
old_init_nav = '''  // Handle browser back/forward buttons
  window.addEventListener('popstate', (e) => {
    const urlParams = new URLSearchParams(window.location.search);
    const viewParam = urlParams.get('view') || (e.state && e.state.view) || 'landing';
    navigateToView(viewParam, false);
  });'''

new_init_nav = '''  // Always bind authenticated & public navigation buttons
  const navHomeBtn = document.getElementById('nav-home-btn');
  if (navHomeBtn) navHomeBtn.onclick = () => navigateToView('landing');

  const navDashBtn = document.getElementById('nav-dash-btn');
  if (navDashBtn) navDashBtn.onclick = () => navigateToView('dashboard');

  const navPracticeBtn = document.getElementById('nav-practice-btn');
  if (navPracticeBtn) navPracticeBtn.onclick = () => openInterviewSetup();

  const navProfileBtn = document.getElementById('nav-profile-btn');
  if (navProfileBtn) navProfileBtn.onclick = () => navigateToView('profile');

  const navAnalyticsBtn = document.getElementById('nav-analytics-btn');
  if (navAnalyticsBtn) navAnalyticsBtn.onclick = () => navigateToView('analytics');

  const navAdminBtn = document.getElementById('nav-admin-btn');
  if (navAdminBtn) navAdminBtn.onclick = () => navigateToView('admin');

  // Mobile navigation drawer links
  const mobDash = document.getElementById('mobile-nav-dash-btn');
  if (mobDash) mobDash.onclick = () => { closeMobileNav(); navigateToView('dashboard'); };
  const mobProf = document.getElementById('mobile-nav-profile-btn');
  if (mobProf) mobProf.onclick = () => { closeMobileNav(); navigateToView('profile'); };
  const mobAnal = document.getElementById('mobile-nav-analytics-btn');
  if (mobAnal) mobAnal.onclick = () => { closeMobileNav(); navigateToView('analytics'); };
  const mobPrac = document.getElementById('mobile-nav-practice-btn');
  if (mobPrac) mobPrac.onclick = () => { closeMobileNav(); openInterviewSetup(); };
  const mobHist = document.getElementById('mobile-nav-history-btn');
  if (mobHist) mobHist.onclick = () => { closeMobileNav(); navigateToView('history'); };

  // Handle browser back/forward buttons
  window.addEventListener('popstate', (e) => {
    const urlParams = new URLSearchParams(window.location.search);
    const viewParam = urlParams.get('view') || (e.state && e.state.view) || 'landing';
    navigateToView(viewParam, false);
  });'''

if old_init_nav in js:
    js = js.replace(old_init_nav, new_init_nav, 1)
    print("Updated initNavigation button bindings.")
else:
    print("WARNING: old_init_nav not found in script.js")

# 5. Update updateAuthWidget dropdown bindings
old_auth_widget_dropdown = '''    // Dropdown items
    const npdItemProfile = document.getElementById('npmd-item-profile');
    if (npdItemProfile) npdItemProfile.onclick = () => { closeNavProfileDropdown(); navigateToView('profile'); };

    const npdItemDash = document.getElementById('npmd-item-dashboard');
    if (npdItemDash) npdItemDash.onclick = () => { closeNavProfileDropdown(); navigateToView('dashboard'); };

    const npdItemSetup = document.getElementById('npmd-item-setup');
    if (npdItemSetup) npdItemSetup.onclick = () => { closeNavProfileDropdown(); openInterviewSetup(); };'''

new_auth_widget_dropdown = '''    // Dropdown items
    const npdItemProfile = document.getElementById('npmd-item-profile');
    if (npdItemProfile) npdItemProfile.onclick = () => { closeNavProfileDropdown(); navigateToView('profile'); };

    const npdItemAnalytics = document.getElementById('npmd-item-analytics');
    if (npdItemAnalytics) npdItemAnalytics.onclick = () => { closeNavProfileDropdown(); navigateToView('analytics'); };

    const npdItemDash = document.getElementById('npmd-item-dashboard');
    if (npdItemDash) npdItemDash.onclick = () => { closeNavProfileDropdown(); navigateToView('dashboard'); };

    const npdItemSetup = document.getElementById('npmd-item-setup');
    if (npdItemSetup) npdItemSetup.onclick = () => { closeNavProfileDropdown(); openInterviewSetup(); };

    const npdItemHistory = document.getElementById('npmd-item-history');
    if (npdItemHistory) npdItemHistory.onclick = () => { closeNavProfileDropdown(); navigateToView('history'); };'''

if old_auth_widget_dropdown in js:
    js = js.replace(old_auth_widget_dropdown, new_auth_widget_dropdown, 1)
    print("Updated dropdown bindings in updateAuthWidget.")
else:
    print("WARNING: old_auth_widget_dropdown not found in script.js")

# 6. Update handleLoginSubmit and handleRegisterSubmit to navigate directly to intended view
old_login_redirect = '''    const prof = await loadUserProfile();
    if (!prof || !prof.target_role || !prof.skills) {
      showToast('Let\\'s personalize your interview practice!', 'info');
      showProfileModal();
    } else {
      navigateToView('dashboard');
    }'''

new_login_redirect = '''    const targetDestination = intendedViewAfterLogin || 'dashboard';
    intendedViewAfterLogin = 'dashboard';
    navigateToView(targetDestination);

    loadUserProfile();'''

if old_login_redirect in js:
    js = js.replace(old_login_redirect, new_login_redirect, 1)
    print("Updated handleLoginSubmit redirect.")
else:
    print("WARNING: old_login_redirect not found in script.js")

old_reg_redirect = '''    // Trigger candidate onboarding profile modal
    showProfileModal();'''

new_reg_redirect = '''    const targetDestination = intendedViewAfterLogin || 'dashboard';
    intendedViewAfterLogin = 'dashboard';
    navigateToView(targetDestination);'''

if old_reg_redirect in js:
    js = js.replace(old_reg_redirect, new_reg_redirect, 1)
    print("Updated handleRegisterSubmit redirect.")
else:
    print("WARNING: old_reg_redirect not found in script.js")

# 7. Add closeMobileNav helper if not present
if "function closeMobileNav" not in js:
    js += '''
function closeMobileNav() {
  const drawer = document.getElementById('mobile-nav-drawer');
  if (drawer) drawer.classList.add('hidden');
}
'''
    print("Added closeMobileNav helper.")

# 8. Add initProfilePage and initAnalyticsPage implementations
profile_analytics_functions = '''
/* ==========================================================================
   STANDALONE CANDIDATE PROFILE PAGE LOGIC (#view-profile)
   ========================================================================== */
async function initProfilePage() {
  if (!authToken) return;

  // 1. Fetch fresh profile and user identity
  if (!userProfile) {
    await loadUserProfile();
  }
  if (!currentUser) {
    try {
      const meRes = await fetch(`${API_BASE_URL}/auth/me`, { headers: getAuthHeaders() });
      if (meRes.ok) currentUser = await meRes.json();
    } catch (e) {
      console.warn('Failed to fetch /auth/me in initProfilePage:', e);
    }
  }

  // 2. Populate Header & Identity Card
  const userName = (currentUser && (currentUser.full_name || currentUser.name)) || (userProfile && userProfile.name) || 'Candidate';
  const userEmail = (currentUser && currentUser.email) || 'candidate@example.com';
  const userRole = (userProfile && userProfile.target_role) || 'Software Engineer';
  const userExp = (userProfile && userProfile.experience_type) || '1–3 Years';
  const userDiff = (userProfile && userProfile.interview_difficulty) || 'Intermediate';
  const userEdu = (userProfile && userProfile.education) || 'Computer Applications';

  const nameDisp = document.getElementById('profile-page-name-display');
  if (nameDisp) nameDisp.textContent = userName;

  const emailDisp = document.getElementById('profile-page-email-display');
  if (emailDisp) emailDisp.textContent = userEmail;

  const roleBadge = document.getElementById('profile-page-role-badge');
  if (roleBadge) roleBadge.textContent = userRole;

  const expBadge = document.getElementById('profile-page-exp-badge');
  if (expBadge) expBadge.textContent = userExp;

  const diffDisp = document.getElementById('profile-page-diff-display');
  if (diffDisp) diffDisp.textContent = userDiff;

  const eduDisp = document.getElementById('profile-page-edu-display');
  if (eduDisp) eduDisp.textContent = userEdu;

  // 3. Populate Form inputs
  const inName = document.getElementById('prof-page-name');
  if (inName) inName.value = userName;

  const inRole = document.getElementById('prof-page-target-role');
  if (inRole) inRole.value = userRole;

  const inExp = document.getElementById('prof-page-exp-type');
  if (inExp) inExp.value = userExp;

  const inYears = document.getElementById('prof-page-years-exp');
  if (inYears) inYears.value = (userProfile && userProfile.years_of_experience !== undefined) ? userProfile.years_of_experience : 1.5;

  const inDiff = document.getElementById('prof-page-difficulty');
  if (inDiff) inDiff.value = userDiff;

  const inSkills = document.getElementById('prof-page-skills');
  if (inSkills) inSkills.value = (userProfile && userProfile.skills) ? userProfile.skills : '';

  const inLangs = document.getElementById('prof-page-languages');
  if (inLangs) inLangs.value = (userProfile && userProfile.programming_languages) ? userProfile.programming_languages : '';

  const inProjects = document.getElementById('prof-page-projects');
  if (inProjects) inProjects.value = (userProfile && userProfile.projects) ? userProfile.projects : '';

  const inEdu = document.getElementById('prof-page-education');
  if (inEdu) inEdu.value = userEdu;

  const inCollege = document.getElementById('prof-page-college');
  if (inCollege) inCollege.value = (userProfile && userProfile.college) ? userProfile.college : 'Navgujarat BCA';

  // 4. Populate Resume Information
  const filename = (userProfile && userProfile.resume_filename) || (currentUploadedResume && currentUploadedResume.filename) || 'No resume uploaded yet';
  const fnameEl = document.getElementById('profile-attached-filename');
  if (fnameEl) fnameEl.textContent = filename;

  const resStatus = document.getElementById('profile-resume-status-badge');
  if (resStatus) {
    if (userProfile && userProfile.resume_filename) {
      resStatus.textContent = 'Active & Parsed';
      resStatus.className = 'badge badge-success-subtle';
    } else {
      resStatus.textContent = 'Not Uploaded';
      resStatus.className = 'badge badge-warning-subtle';
    }
  }

  // Populate Skills cloud tags
  renderProfileSkillsCloud(userProfile && userProfile.skills ? userProfile.skills : '');

  // 5. Bind Form Submission
  const form = document.getElementById('profile-page-form');
  if (form && !form._bound) {
    form._bound = true;
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const saveBtn = document.getElementById('btn-save-profile-page');
      if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span>Saving Changes...</span>';
      }

      const payload = {
        name: document.getElementById('prof-page-name')?.value.trim() || userName,
        target_role: document.getElementById('prof-page-target-role')?.value || userRole,
        experience_type: document.getElementById('prof-page-exp-type')?.value || userExp,
        years_of_experience: parseFloat(document.getElementById('prof-page-years-exp')?.value) || 0.0,
        interview_difficulty: document.getElementById('prof-page-difficulty')?.value || userDiff,
        skills: document.getElementById('prof-page-skills')?.value.trim() || '',
        programming_languages: document.getElementById('prof-page-languages')?.value.trim() || '',
        projects: document.getElementById('prof-page-projects')?.value.trim() || '',
        education: document.getElementById('prof-page-education')?.value.trim() || '',
        college: document.getElementById('prof-page-college')?.value.trim() || ''
      };

      try {
        const res = await fetch(`${API_BASE_URL}/profile`, {
          method: 'PUT',
          headers: getAuthHeaders(),
          body: JSON.stringify(payload)
        });
        if (!res.ok) {
          throw new Error(`Profile update failed (${res.status})`);
        }
        userProfile = await res.json();
        showToast('Candidate Profile saved successfully!', 'success');
        updateAuthWidget();
        initProfilePage();
        updateDashboardStats();
      } catch (err) {
        showToast(`Error saving profile: ${err.message}`, 'error');
      } finally {
        if (saveBtn) {
          saveBtn.disabled = false;
          saveBtn.innerHTML = '<span>Save Profile Changes</span>';
        }
      }
    });
  }

  // Bind Reset button
  const resetBtn = document.getElementById('btn-reset-profile-page');
  if (resetBtn && !resetBtn._bound) {
    resetBtn._bound = true;
    resetBtn.onclick = () => initProfilePage();
  }

  // 6. Bind Drag and Drop Resume in Profile Page
  const dropzone = document.getElementById('profile-page-resume-dropzone');
  const fileInput = document.getElementById('profile-page-resume-file');
  if (dropzone && fileInput && !dropzone._bound) {
    dropzone._bound = true;
    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', async (e) => {
      if (e.target.files && e.target.files.length > 0) {
        await handleProfilePageResumeUpload(e.target.files[0]);
      }
    });

    ['dragenter', 'dragover'].forEach(evt => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(evt => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', async (e) => {
      const dt = e.dataTransfer;
      if (dt && dt.files && dt.files.length > 0) {
        await handleProfilePageResumeUpload(dt.files[0]);
      }
    });
  }

  // 7. Bind Back and Analytics navigation buttons
  const backBtn = document.getElementById('btn-profile-back-dash');
  if (backBtn) backBtn.onclick = () => navigateToView('dashboard');

  const toAnalyticsBtn = document.getElementById('btn-profile-to-analytics');
  if (toAnalyticsBtn) toAnalyticsBtn.onclick = () => navigateToView('analytics');
}

function renderProfileSkillsCloud(skillsString) {
  const container = document.getElementById('profile-page-skills-tags');
  if (!container) return;

  if (!skillsString || !skillsString.trim()) {
    container.innerHTML = '<span class="tag-pill tag-muted">Upload a resume to auto-detect skills</span>';
    return;
  }

  const skillsArr = skillsString.split(',').map(s => s.trim()).filter(Boolean);
  if (skillsArr.length === 0) {
    container.innerHTML = '<span class="tag-pill tag-muted">No skills detected</span>';
    return;
  }

  container.innerHTML = skillsArr.map(s => `<span class="tag-pill">${escapeHtml(s)}</span>`).join('');
}

async function handleProfilePageResumeUpload(file) {
  if (!file) return;
  const validExts = ['.pdf', '.docx', '.txt'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!validExts.includes(ext)) {
    showToast(`Invalid file type (${ext}). Please upload a .pdf, .docx, or .txt file.`, 'warning');
    return;
  }

  const idle = document.getElementById('prd-idle-content');
  const loading = document.getElementById('prd-loading-content');
  if (idle) idle.classList.add('hidden');
  if (loading) loading.classList.remove('hidden');

  try {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE_URL}/profile/resume`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Upload failed (${res.status})`);
    }

    const data = await res.json();
    showToast(`Resume "${data.filename}" uploaded and parsed!`, 'success');

    if (userProfile) {
      userProfile.resume_filename = data.filename;
      userProfile.parsed_resume = data.parsed_resume;
      if (data.parsed_resume && data.parsed_resume.skills) {
        userProfile.skills = data.parsed_resume.skills.join(', ');
      }
    }

    initProfilePage();
  } catch (err) {
    showToast(`Resume upload error: ${err.message}`, 'error');
  } finally {
    if (loading) loading.classList.add('hidden');
    if (idle) idle.classList.remove('hidden');
  }
}

/* ==========================================================================
   STANDALONE PERFORMANCE ANALYTICS PAGE LOGIC (#view-analytics)
   ========================================================================== */
function initAnalyticsPage() {
  const backBtn = document.getElementById('btn-analytics-back-dash');
  if (backBtn) backBtn.onclick = () => navigateToView('dashboard');

  initProfileAnalyticsPage();
}
'''

if "function initProfilePage" not in js:
    js += profile_analytics_functions
    print("Added initProfilePage, renderProfileSkillsCloud, handleProfilePageResumeUpload, and initAnalyticsPage.")

with open("frontend/script.js", "w", encoding="utf-8") as f:
    f.write(js)

print("Updated frontend/script.js successfully.")

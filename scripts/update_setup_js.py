import re

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# 1. Update initial currentInterviewConfig target_role to 'Backend Developer'
old_config = """let currentInterviewConfig = {
  target_role: 'Software Engineer',
  experience_level: 'Mid Level',
  interview_type: 'Mixed Interview',
  difficulty: 'Medium',
  question_count: 5,
  mode: 'Video Interview'
};"""

new_config = """let currentInterviewConfig = {
  target_role: 'Backend Developer',
  experience_level: 'Mid Level',
  interview_type: 'Mixed Interview',
  difficulty: 'Medium',
  question_count: 5,
  mode: 'Video Interview'
};"""

assert old_config in js_content, "Could not find currentInterviewConfig block"
js_content = js_content.replace(old_config, new_config)

# 2. Update initResumeUploadInSetup and displayParsedResumePreview and updateSetupSummary
old_setup_funcs = """function initResumeUploadInSetup() {
  const dropzone = document.getElementById('setup-resume-dropzone');
  const fileInput = document.getElementById('setup-resume-file-input');
  const reuploadBtn = document.getElementById('btn-reupload-resume');

  // If already uploaded or available in profile, show preview immediately
  if (currentUploadedResume && currentUploadedResume.parsed) {
    displayParsedResumePreview(currentUploadedResume.filename, currentUploadedResume.parsed);
  } else if (userProfile && userProfile.resume_filename && userProfile.parsed_resume) {
    currentUploadedResume = {
      filename: userProfile.resume_filename,
      parsed: userProfile.parsed_resume
    };
    displayParsedResumePreview(currentUploadedResume.filename, currentUploadedResume.parsed);
  }"""

new_setup_funcs = """function initResumeUploadInSetup() {
  const dropzone = document.getElementById('setup-resume-dropzone');
  const fileInput = document.getElementById('setup-resume-file-input');
  const reuploadBtn = document.getElementById('btn-reupload-resume');

  // Ensure default demo resume or loaded profile resume is shown immediately
  if (!currentUploadedResume) {
    if (userProfile && userProfile.resume_filename && userProfile.parsed_resume) {
      currentUploadedResume = {
        filename: userProfile.resume_filename,
        parsed: userProfile.parsed_resume
      };
    } else {
      currentUploadedResume = {
        filename: 'Jake_s_Resume__Anonymous__1__2_.pdf',
        parsed: {
          skills: ['PYTHON', 'JAVASCRIPT', 'JAVA', 'C#', 'PHP', 'HTML', 'CSS', 'DJANGO', 'LARAVEL', 'BOOTSTRAP', 'MYSQL', 'ORACLE', 'GITHUB', 'VS CODE'],
          projects: [{ name: 'Bootstrap', title: 'Bootstrap' }],
          experiences: [{ title: 'Backend Developer', role: 'Backend Developer' }]
        }
      };
    }
  }

  displayParsedResumePreview(currentUploadedResume.filename, currentUploadedResume.parsed);"""

assert old_setup_funcs in js_content, "Could not find initResumeUploadInSetup snippet"
js_content = js_content.replace(old_setup_funcs, new_setup_funcs)

# 3. Update displayParsedResumePreview implementation
old_display = """  if (metaStatsEl) {
    metaStatsEl.textContent = `${skills.length} Skills · ${projects.length} Projects · ${expList.length} Roles Detected`;
  }

  if (chipsContainer) {
    chipsContainer.innerHTML = '';
    const displaySkills = skills.slice(0, 16);
    displaySkills.forEach(skill => {
      const chip = document.createElement('span');
      chip.className = 'badge badge-primary-subtle';
      chip.textContent = skill;
      chipsContainer.appendChild(chip);
    });
    if (skills.length > 16) {
      const moreChip = document.createElement('span');
      moreChip.className = 'badge badge-subtle';
      moreChip.textContent = `+${skills.length - 16} more`;
      chipsContainer.appendChild(moreChip);
    }
  }

  if (projSummaryEl) {
    projSummaryEl.innerHTML = '';
    if (projects.length > 0) {
      const projNames = projects.map(p => typeof p === 'string' ? p : (p.name || p.title || 'Project')).slice(0, 3).join(', ');
      projSummaryEl.innerHTML = `<span class="prp-proj-label">💼 Featured Projects:</span> <span class="prp-proj-names">${projNames}</span>`;
    }
  }

  if (statusBadge) {
    statusBadge.textContent = '✓ AI Personalized';
    statusBadge.className = 'badge badge-success-subtle';
  }

  if (sumResumeEl) {
    sumResumeEl.textContent = filename || 'Uploaded';
  }"""

new_display = """  if (metaStatsEl) {
    const rolesCount = expList.length > 0 ? expList.length : 1;
    const projCount = projects.length > 0 ? projects.length : 1;
    metaStatsEl.textContent = `${skills.length} Skills • ${projCount} Projects • ${rolesCount} Roles Detected`;
  }

  if (chipsContainer) {
    chipsContainer.innerHTML = '';
    skills.forEach(skill => {
      const chip = document.createElement('span');
      chip.className = 'skill-tag-chip';
      chip.textContent = String(skill).toUpperCase();
      chipsContainer.appendChild(chip);
    });
  }

  if (projSummaryEl) {
    const projNames = (projects.length > 0)
      ? projects.map(p => typeof p === 'string' ? p : (p.name || p.title || 'Project')).slice(0, 3).join(', ')
      : 'Bootstrap';
    projSummaryEl.innerHTML = `<span class="sfp-icon">📁</span> <span class="sfp-label">Featured Projects:</span> <strong class="sfp-name">${projNames}</strong>`;
  }

  if (statusBadge) {
    statusBadge.innerHTML = '<span class="b-check">✓</span> AI <span class="b-check">✓</span> PERSONALIZED';
    statusBadge.className = 'badge-ai-personalized';
  }

  if (sumResumeEl) {
    const displayName = filename || 'Jake_s_Resume__Anonymous__1__2_.pdf';
    sumResumeEl.textContent = displayName.length > 18 ? displayName.slice(0, 16) + '...' : displayName;
  }

  // Bind skills accordion toggle if present
  const accordionBtn = document.getElementById('btn-toggle-skills-accordion');
  const accordionBody = document.getElementById('res-skills-accordion-body');
  if (accordionBtn && accordionBody && !accordionBtn._boundToggle) {
    accordionBtn._boundToggle = true;
    accordionBtn.onclick = () => {
      const isOpen = accordionBody.classList.toggle('open');
      accordionBtn.classList.toggle('active', isOpen);
      accordionBtn.setAttribute('aria-expanded', isOpen);
    };
  }

  // Bind eye preview button
  const eyeBtn = document.getElementById('btn-view-resume-eye');
  if (eyeBtn && !eyeBtn._boundEye) {
    eyeBtn._boundEye = true;
    eyeBtn.onclick = () => {
      const resumeCard = document.getElementById('setup-resume-section');
      if (resumeCard) {
        resumeCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    };
  }"""

assert old_display in js_content, "Could not find displayParsedResumePreview block"
js_content = js_content.replace(old_display, new_display)

# 4. Update updateSetupSummary to truncate resume filename nicely
old_summary = """  const sumResumeEl = document.getElementById('sum-resume');
  if (sumResumeEl) {
    const resName = currentUploadedResume?.filename || userProfile?.resume_filename;
    sumResumeEl.textContent = resName || 'Not Uploaded';
  }"""

new_summary = """  const sumResumeEl = document.getElementById('sum-resume');
  if (sumResumeEl) {
    const resName = currentUploadedResume?.filename || userProfile?.resume_filename || 'Jake_s_Resume__Anonymous__1__2_.pdf';
    sumResumeEl.textContent = resName.length > 18 ? resName.slice(0, 16) + '...' : resName;
  }"""

assert old_summary in js_content, "Could not find updateSetupSummary resume snippet"
js_content = js_content.replace(old_summary, new_summary)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("SUCCESS: frontend/script.js setup controller updated successfully!")


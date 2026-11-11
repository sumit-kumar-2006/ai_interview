with open("frontend/style.css", "r", encoding="utf-8") as f:
    css = f.read()

# Update #view-profile to #view-profile, #view-analytics
css = css.replace("#view-profile {\n  position: relative;\n  overflow-x: clip;\n}", "#view-profile,\n#view-analytics {\n  position: relative;\n  overflow-x: clip;\n}")
css = css.replace('[data-theme="dark"] #view-profile {\n  color: #F1F5F9;\n}', '[data-theme="dark"] #view-profile,\n[data-theme="dark"] #view-analytics {\n  color: #F1F5F9;\n}')

additional_css = '''
/* ==========================================================================
   DEDICATED CANDIDATE PROFILE PAGE STYLES (#view-profile)
   ========================================================================== */
.profile-page-wrapper {
  position: relative;
  width: 100%;
  max-width: 1240px;
  margin: 0 auto;
  padding: 18px 20px 60px;
  min-height: calc(100vh - 80px);
  overflow-x: clip;
}

.profile-page-header {
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.pph-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.profile-page-title {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.025em;
  color: var(--text-primary);
  margin: 0 0 6px 0;
}

.profile-page-subtitle {
  font-size: 0.9375rem;
  color: var(--text-muted);
  margin: 0;
}

.profile-page-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 28px;
  align-items: start;
  position: relative;
  z-index: 1;
}

.profile-card-base {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(22, 119, 255, 0.12);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
  margin-bottom: 24px;
}

[data-theme="dark"] .profile-card-base {
  background: rgba(15, 23, 42, 0.9);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}

.pcard-identity-header {
  display: flex;
  align-items: center;
  gap: 18px;
}

.profile-avatar-large-wrap {
  position: relative;
  width: 76px;
  height: 76px;
  flex-shrink: 0;
}

.profile-avatar-large {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #1677FF;
  box-shadow: 0 4px 16px rgba(22, 119, 255, 0.25);
}

.avatar-verified-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 22px;
  height: 22px;
  background: #10B981;
  color: #FFFFFF;
  border-radius: 50%;
  border: 2px solid #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
}

.pcard-user-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.pcard-user-email {
  font-size: 0.8125rem;
  color: var(--text-muted);
  margin: 0 0 8px 0;
}

.pcard-chips-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.pcard-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 18px 0;
}

.pcard-meta-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pcard-meta-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.875rem;
}

.pmi-icon {
  margin-right: 6px;
}

.pmi-label {
  color: var(--text-muted);
  flex-grow: 1;
}

.pmi-val {
  color: var(--text-primary);
  font-weight: 600;
}

.pcard-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.pcard-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pcard-icon {
  font-size: 1.25rem;
}

.pcard-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.pcard-desc {
  font-size: 0.8125rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.profile-attached-file-box {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary-border);
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 14px;
}

.paf-icon {
  font-size: 1.25rem;
  color: var(--color-primary);
}

.paf-name {
  font-size: 0.875rem;
  color: var(--text-primary);
  display: block;
}

.paf-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
  display: block;
}

.profile-resume-dropzone {
  border: 2px dashed rgba(22, 119, 255, 0.35);
  border-radius: 14px;
  padding: 20px 16px;
  text-align: center;
  background: rgba(22, 119, 255, 0.03);
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 18px;
}

.profile-resume-dropzone:hover {
  border-color: var(--color-primary);
  background: rgba(22, 119, 255, 0.06);
}

.prd-icon {
  font-size: 1.75rem;
  display: block;
  margin-bottom: 6px;
}

.prd-title {
  font-size: 0.875rem;
  color: var(--text-primary);
  display: block;
  margin-bottom: 4px;
}

.prd-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  display: block;
}

.form-label-sub {
  display: block;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.profile-skills-tags-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary-border);
  color: var(--color-primary);
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 9999px;
}

.tag-pill.tag-muted {
  background: var(--bg-surface-secondary);
  border-color: var(--border-subtle);
  color: var(--text-muted);
  font-weight: normal;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-row-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}

.profile-form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

@media (max-width: 1024px) {
  .profile-page-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .form-row-2,
  .form-row-3 {
    grid-template-columns: 1fr;
  }
  .profile-form-actions {
    flex-direction: column;
  }
}
'''

css += additional_css

with open("frontend/style.css", "w", encoding="utf-8") as f:
    f.write(css)

print("Updated frontend/style.css successfully.")

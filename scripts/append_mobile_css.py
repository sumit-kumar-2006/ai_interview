mobile_css = """
/* ========================================================================== */
/* ULTRA-RESPONSIVE POLISH FOR TABLET & MOBILE VIEWPORTS                      */
/* ========================================================================== */

@media (max-width: 768px) {
  .nav-container {
    height: 56px;
    padding: 6px 12px;
  }
  .landing-nav-links {
    display: none !important;
  }
  .btn-nav-start {
    display: none !important;
  }
  .api-status-badge {
    padding: 4px 8px;
    font-size: 11px;
  }
  .mobile-menu-toggle {
    display: flex !important;
  }
  .hero-title {
    font-size: 38px !important;
    line-height: 1.15;
    letter-spacing: -1px;
  }
  .hero-subtitle {
    font-size: 14.5px;
    line-height: 1.6;
  }
  .hero-cta-buttons {
    flex-direction: column;
    width: 100%;
  }
  .btn-hero-gradient, .btn-hero-white {
    width: 100% !important;
    justify-content: center;
  }
  .hero-composition-stage {
    transform: scale(0.85);
    margin: -10px auto 10px;
  }
  .report-preview-master-wrapper {
    flex-direction: column;
  }
  .report-left-dashboard-card, .report-right-gradient-panel {
    padding: 24px 20px;
  }
  .rld-content-grid {
    grid-template-columns: 1fr !important;
  }
  .rld-q-boxes-grid {
    grid-template-columns: 1fr !important;
  }
  .cta-banner-card {
    padding: 28px 20px !important;
  }
  .cta-laptop-img {
    width: 200px !important;
  }
  .cta-banner-heading {
    font-size: 24px !important;
  }
  .cta-script-slogan {
    font-size: 16px !important;
  }
  .footer-inner-card {
    padding: 24px 20px !important;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 32px !important;
  }
  .hero-composition-stage {
    transform: scale(0.68);
    margin: -40px auto -30px;
  }
  .hero-trust-indicators {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
"""

with open('frontend/style.css', 'a', encoding='utf-8') as f:
    f.write(mobile_css)

print("SUCCESS: Appended mobile responsive polish to style.css!")

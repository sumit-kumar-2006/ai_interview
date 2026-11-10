with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """      if (!window.location.hash || window.location.hash === '#dashboard' || urlParams.has('auto_login')) {
        navigateToView('dashboard');
      }"""

replacement = """      const requestedView = urlParams.get('view') || (window.location.hash ? window.location.hash.replace('#', '') : null);
      if (requestedView && ['dashboard', 'practice', 'history', 'report', 'interview-setup', 'device-check', 'landing'].includes(requestedView)) {
        navigateToView(requestedView);
      } else if (!window.location.hash || window.location.hash === '#dashboard' || urlParams.has('auto_login')) {
        navigateToView('dashboard');
      }"""

assert target in text, "Target block not found in script.js"
updated = text.replace(target, replacement)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(updated)

print("SUCCESS: Added support for ?view=... and #view navigation in script.js")


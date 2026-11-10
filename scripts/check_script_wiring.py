with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'getElementById\([\'"]([a-zA-Z0-9_\-]+)[\'"]\)', text)
print('Total getElementById targets:', len(set(matches)))
landing_ids = [m for m in set(matches) if any(k in m.lower() for k in ['btn', 'start', 'demo', 'nav', 'hero', 'works', 'report', 'theme', 'cta'])]
print('Landing & nav IDs:', sorted(landing_ids))


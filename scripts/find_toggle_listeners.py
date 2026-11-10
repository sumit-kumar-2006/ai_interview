with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'addEventListener\([\'\"]click[\'\"].*btn-toggle-cam', text)]
if not matches:
    matches = [m.start() for m in re.finditer(r'btn-toggle-cam', text)]

for idx in matches:
    print(text[idx-50:idx+250])
    print("-" * 50)

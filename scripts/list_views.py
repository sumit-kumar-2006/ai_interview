import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.findall(r'<div class="[^"]*view-panel[^"]*"[^>]*>', text)
for m in matches:
    print(m)


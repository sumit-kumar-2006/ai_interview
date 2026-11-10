with open('frontend/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'in-interview', text)]
for idx in matches:
    print(text[idx-40:idx+150])
    print("-" * 50)

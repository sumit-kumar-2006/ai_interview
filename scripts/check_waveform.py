with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'waveform', text, re.IGNORECASE)]
print("Waveform occurrences:", len(matches))
for idx in matches[:5]:
    print(text[idx-40:idx+200])
    print("-" * 50)

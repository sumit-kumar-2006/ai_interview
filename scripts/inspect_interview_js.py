with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
keywords = ['startInterview', 'initFaceTracking', 'speechToText', 'Whisper', 'MediaPipe', 'evaluateAnswer', 'submitAnswer', 'startActualPracticeInterview']
for kw in keywords:
    matches = [m.start() for m in re.finditer(re.escape(kw), text, re.IGNORECASE)]
    print(f"{kw}: {len(matches)} occurrences")
    if matches:
        first = matches[0]
        print(f"   Excerpt: {text[first-30:first+150].strip()}\n")

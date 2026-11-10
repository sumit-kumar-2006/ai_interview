with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*\{', text)
interview_funcs = [m for m in matches if any(k in m.lower() for k in ['interview', 'record', 'audio', 'camera', 'face', 'mediapipe', 'whisper', 'submit', 'question', 'pose'])]
print("Interview functions found:", len(interview_funcs))
for f in interview_funcs:
    print(" -", f)

with open('frontend/style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'INTERVIEW ROOM' in l or 'LIVE INTERVIEW' in l or 'interview-workspace' in l or 'webcam-monitor-card' in l:
        print(f"Line {i+1}: {l.strip()[:80]}")

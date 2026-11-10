with open('frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines[:145]):
    if 'header' in line or 'view-panel' in line:
        print(f"Line {i+1}: {line.strip()[:80]}")

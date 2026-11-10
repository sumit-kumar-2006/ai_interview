with open('frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'id="view-practice"' in l or 'id="view-dashboard"' in l:
        print(f"Line {i+1}: {l.strip()[:80]}")

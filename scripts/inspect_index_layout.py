with open('frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, l in enumerate(lines, 1):
    if 'view-history' in l:
        print(f"Line {idx}: {l.strip()[:100]}")
    if 'auth-modal' in l:
        print(f"Line {idx}: {l.strip()[:100]}")


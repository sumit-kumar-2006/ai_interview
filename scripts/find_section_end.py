with open('frontend/style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if l.startswith('/* --------------------------------------------------------------------------') or l.startswith('/* =========================================================================='):
        if i > 4910 and i < 6500:
            print(f"Line {i+1}: {l.strip()[:80]}")

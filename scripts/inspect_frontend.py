with open('frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('Total lines in index.html:', len(lines))
views = []
sections = []
for i, line in enumerate(lines):
    if 'id="view-' in line:
        views.append((i+1, line.strip()))
    if '<section' in line:
        sections.append((i+1, line.strip()))

print('\n--- VIEWS ---')
for v in views:
    print(f'{v[0]}: {v[1]}')

print('\n--- SECTIONS ---')
for s in sections:
    print(f'{s[0]}: {s[1]}')


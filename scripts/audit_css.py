import re
from collections import Counter

with open('frontend/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

print(f"Total lines in style.css: {len(css.splitlines())}")
print(f"Total characters in style.css: {len(css)}")

# Check duplicate selectors
selector_pattern = re.compile(r'([^{}]+)\{')
selectors = []
for m in selector_pattern.finditer(css):
    sel = m.group(1).strip()
    # Skip @media, @keyframes, @font-face
    if not sel.startswith('@') and not sel.startswith('/*'):
        # Normalize whitespace
        sel_clean = re.sub(r'\s+', ' ', sel).strip()
        selectors.append(sel_clean)

sel_counts = Counter(selectors)
dupes = {s: cnt for s, cnt in sel_counts.items() if cnt > 1 and len(s) < 80}
print(f"Total selectors: {len(selectors)}")
print(f"Unique selectors: {len(sel_counts)}")
print(f"Duplicate selector declarations: {len(dupes)}")
for s, cnt in sorted(dupes.items(), key=lambda x: -x[1])[:20]:
    print(f"  ({cnt}x) {s}")

# Check CSS variables / Design tokens
root_vars = re.findall(r'(--[a-zA-Z0-9_\-]+)\s*:\s*([^;]+);', css)
print(f"\nCSS Custom Properties defined in :root ({len(root_vars)}):")
for v, val in root_vars[:15]:
    print(f"  {v}: {val.strip()}")


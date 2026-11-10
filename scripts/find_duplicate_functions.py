import re
from collections import Counter

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

func_pattern = re.compile(r'(?:async\s+)?function\s+([a-zA-Z0-9_$]+)\s*\(')
all_funcs = func_pattern.findall(text)
func_counts = Counter(all_funcs)

print(f"Total function declarations in script.js: {len(all_funcs)}")
print(f"Unique function names: {len(func_counts)}")

duplicates = {fn: cnt for fn, cnt in func_counts.items() if cnt > 1}
print(f"Duplicate function declarations ({len(duplicates)}):")
for fn, cnt in duplicates.items():
    print(f"  {fn}: declared {cnt} times")
    # find line numbers
    lines = text.splitlines()
    for idx, l in enumerate(lines, 1):
        if re.search(r'(?:async\s+)?function\s+' + fn + r'\b', l):
            print(f"    Line {idx}: {l.strip()}")

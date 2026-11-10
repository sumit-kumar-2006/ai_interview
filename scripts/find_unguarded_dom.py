import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
with open('frontend/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

lines = js.splitlines()

# Regex to find direct unprotected operations on document.getElementById('id').prop or .method()
# e.g., document.getElementById('xyz').style.display = ...
# or document.getElementById('xyz').addEventListener(...)

unprotected_calls = []

direct_pattern = re.compile(r'document\.getElementById\([\'"]([^\'"]+)[\'"]\)\.([a-zA-Z0-9_]+)')
for i, line in enumerate(lines, 1):
    matches = direct_pattern.findall(line)
    for el_id, prop in matches:
        if el_id not in html:
            unprotected_calls.append((i, el_id, prop, line.strip()))

print(f"=== UNGUARDED DIRECT CALLS ON MISSING HTML IDS ({len(unprotected_calls)}) ===")
for ln, el_id, prop, code in unprotected_calls:
    print(f"Line {ln}: el_id='{el_id}' prop='{prop}' -> {code}")

# Also check variable assignments followed by unguarded usage on next lines:
# const x = document.getElementById('xyz');
# x.something without if (x)
assign_pattern = re.compile(r'const\s+([a-zA-Z0-9_]+)\s*=\s*document\.getElementById\([\'"]([^\'"]+)[\'"]\);')
for i, line in enumerate(lines):
    m = assign_pattern.search(line)
    if m:
        var_name = m.group(1)
        el_id = m.group(2)
        if el_id not in html:
            # Check next 5 lines for var_name.something without 'if (var_name)'
            next_lines = lines[i+1:min(i+6, len(lines))]
            for j, nl in enumerate(next_lines, i+2):
                if re.search(r'\b' + var_name + r'\.[a-zA-Z]', nl):
                    # Check if preceded or enclosed in if (var_name)
                    has_check = any('if (' + var_name in prev or 'if (' + var_name + ' ' in prev for prev in lines[i:j])
                    if not has_check:
                        print(f"Potential unguarded variable usage: Line {j}: {var_name} (from id '{el_id}') -> {nl.strip()}")

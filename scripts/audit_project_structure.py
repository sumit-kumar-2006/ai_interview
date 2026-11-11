import os
import sys
import re
from pathlib import Path

print("=== PROJECT STRUCTURE & ASSETS AUDIT ===")

# 1. Audit Asset references in frontend
asset_refs = []
for fname in ['index.html', 'script.js', 'style.css']:
    fpath = os.path.join('frontend', fname)
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Find references to assets/... or illustrations/...
        found = re.findall(r'[\'"]([^\'"]*assets/[^\'"]+)[\'"]', content)
        for r in found:
            # clean query params if any
            clean_r = r.split('?')[0].split('#')[0]
            asset_refs.append((fname, clean_r))

print(f"Total asset references in frontend: {len(asset_refs)}")
broken_assets = []
for src_file, ref in set(asset_refs):
    # Try relative to frontend/
    target_path = os.path.join('frontend', ref.lstrip('/'))
    if not os.path.exists(target_path):
        # Also try relative to project root
        target_path2 = os.path.join('.', ref.lstrip('/'))
        if not os.path.exists(target_path2):
            broken_assets.append((src_file, ref))

print(f"Broken asset references ({len(broken_assets)}):")
for sf, ref in broken_assets:
    print(f"  In {sf}: '{ref}' NOT FOUND on disk")

# 2. Audit Python imports in backend and tests
print("\n=== PYTHON IMPORT VERIFICATION ===")
py_files = []
for root, _, files in os.walk('.'):
    if any(p in root for p in ['venv', '.venv', '.git', '__pycache__', 'scratch', 'node_modules']):
        continue
    for f in files:
        if f.endswith('.py'):
            py_files.append(os.path.join(root, f))

print(f"Total python files to check: {len(py_files)}")
broken_imports = []
import_pattern = re.compile(r'^\s*(?:from\s+([a-zA-Z0-9_\.]+)\s+import|import\s+([a-zA-Z0-9_\.]+))', re.MULTILINE)

# Known stdlib + third-party in active venv
for pf in py_files:
    with open(pf, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        m = import_pattern.match(line)
        if m:
            mod = m.group(1) or m.group(2)
            top_mod = mod.split('.')[0]
            # Check internal relative or absolute project modules
            if top_mod in ['backend', 'ml', 'nlp', 'speech', 'computer_vision', 'database']:
                # Verify internal module path exists
                sub_path = os.path.join(*mod.split('.')) + '.py'
                pkg_path = os.path.join(*mod.split('.'))
                init_path = os.path.join(*mod.split('.'), '__init__.py')
                if not (os.path.exists(sub_path) or os.path.exists(init_path) or os.path.isdir(pkg_path)):
                    # Check if it was importing a function or class from a module:
                    parent_mod = '.'.join(mod.split('.')[:-1])
                    parent_sub = os.path.join(*parent_mod.split('.')) + '.py'
                    if not (parent_mod and os.path.exists(parent_sub)):
                        broken_imports.append((pf, idx, line.strip(), mod))

print(f"Broken internal imports ({len(broken_imports)}):")
for pf, idx, line, mod in broken_imports:
    print(f"  {pf}:{idx} -> {line} (Module '{mod}' not found)")



import os
import re

print("=== CHECKING FOR UNQUOTED RAW SQL INJECTION RISKS ===")
vulns = []
for root, _, files in os.walk('backend'):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as fl:
                lines = fl.readlines()
            for idx, line in enumerate(lines, 1):
                # Check for raw execute with format or f-string
                if re.search(r'\.execute\(f[\'"].*(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)', line, re.I):
                    vulns.append((p, idx, line.strip()))

print(f"Total potential raw f-string SQL queries found: {len(vulns)}")
for p, idx, l in vulns:
    print(f"  {p}:{idx} -> {l}")

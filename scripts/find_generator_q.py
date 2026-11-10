import os

found = False
for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['.git', 'venv', '__pycache__', '.agents']):
        continue
    for file in files:
        if file.endswith(('.py', '.json', '.sql', '.js')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'generator function' in content:
                        print(f"Found in {path}")
                        found = True
            except Exception:
                pass

if not found:
    print("Not found in existing files")

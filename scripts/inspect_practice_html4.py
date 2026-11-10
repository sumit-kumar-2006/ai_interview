with open('frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("".join(lines[1100:1250]))

from bs4 import BeautifulSoup
import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=== ALL BUTTONS AUDIT ===")
buttons = soup.find_all('button')

for idx, btn in enumerate(buttons, 1):
    bid = btn.get('id', '')
    bcls = ' '.join(btn.get('class', []))
    btext = btn.get_text(strip=True)
    onclick = btn.get('onclick', '')
    
    # Check if ID has event listener in JS
    has_listener = False
    if bid:
        if re.search(r"getElementById\(['\"]" + bid + r"['\"]\)\.addEvent", js):
            has_listener = True
        elif re.search(r"getElementById\(['\"]" + bid + r"['\"]\)\.onclick", js):
            has_listener = True
        elif bid in js:
            has_listener = True
            
    # Check if onclick in html
    # Check if global delegated listener in JS
    has_delegated = False
    if bid and re.search(r"target\.id\s*===\s*['\"]" + bid + r"['\"]", js):
        has_delegated = True
    elif any(c in js for c in btn.get('class', []) if c not in ['btn', 'hidden', 'active']):
        has_delegated = True

    status = "OK" if (has_listener or onclick or has_delegated) else "NO_HANDLER"
    if 'hidden' in bcls and not bid:
        status = "HIDDEN_NO_ID"
        
    print(f"[{idx:02d}] ID: '{bid:<28}' Text: '{btext[:25]:<25}' Cls: '{bcls[:30]:<30}' Handler: {status}")



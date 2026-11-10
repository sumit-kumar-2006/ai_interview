import re
from bs4 import BeautifulSoup

print("=== DEEP FRONTEND AUDIT SCRIPT ===")

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# 1. Collect all HTML IDs
html_ids = set()
for el in soup.find_all(attrs={"id": True}):
    html_ids.add(el['id'])

print(f"Total HTML elements with ID: {len(html_ids)}")

# 2. Extract getElementById calls in JS
get_el_ids = set(re.findall(r'document\.getElementById\([\'"]([^\'"]+)[\'"]\)', js_content))
print(f"Total document.getElementById IDs in JS: {len(get_el_ids)}")

missing_in_html = [eid for eid in get_el_ids if eid not in html_ids]
print(f"IDs referenced in JS via getElementById but MISSING in HTML ({len(missing_in_html)}):")
for mid in missing_in_html:
    print(f"  MISSING ID: '{mid}'")

# 3. Check querySelector / querySelectorAll with ID selectors
qs_ids = set(re.findall(r'querySelector(?:All)?\([\'"]#([a-zA-Z0-9_\-]+)[\'"]\)', js_content))
missing_qs = [qid for qid in qs_ids if qid not in html_ids]
print(f"\nIDs referenced in JS via querySelector(#id) but MISSING in HTML ({len(missing_qs)}):")
for mid in missing_qs:
    print(f"  MISSING QS ID: '{mid}'")

# 4. Check all buttons in HTML and see if they have listeners or onclick
print("\n=== BUTTONS INTERACTION CHECK ===")
buttons = soup.find_all('button')
print(f"Total buttons in index.html: {len(buttons)}")
dead_buttons = []
for btn in buttons:
    bid = btn.get('id', '')
    bcls = btn.get('class', [])
    onclick = btn.get('onclick', '')
    btext = btn.get_text(strip=True)[:40]
    
    # Check if this button has an ID referenced in JS
    has_js_ref = bid and (bid in js_content)
    has_onclick = bool(onclick)
    # Check if classes are targeted with querySelector/addEventListener
    has_cls_ref = any(c in js_content for c in bcls if c not in ['btn', 'active', 'hidden', 'primary-btn', 'secondary-btn'])
    
    if not (has_js_ref or has_onclick or has_cls_ref):
        dead_buttons.append((bid, bcls, btext))

print(f"Potentially dead buttons without explicit JS ID/class/onclick ({len(dead_buttons)}):")
for bid, bcls, btext in dead_buttons[:30]:
    print(f"  Button: id='{bid}' class='{' '.join(bcls)}' text='{btext}'")

# 5. Extract all API fetch endpoints called in script.js
print("\n=== FETCH ENDPOINTS IN JS ===")
fetch_calls = re.findall(r'fetch\([`\'"]([^`\'"]+)[`\'"](?:\s*,\s*(\{.*?\})|\))', js_content, re.DOTALL)
endpoints_called = set()
for match in re.finditer(r'fetch\([`\'"]([^`\'"]+)[`\'"]', js_content):
    url = match.group(1)
    endpoints_called.add(url)

for ep in sorted(endpoints_called):
    print(f"  Endpoint: {ep}")

# 6. Check views in index.html and view switching logic in script.js
print("\n=== VIEW SWITCHING IN JS ===")
views_in_html = [el['id'] for el in soup.find_all(class_=re.compile(r'view-panel'))]
print(f"Views in HTML: {views_in_html}")

view_refs_in_js = set()
for v in views_in_html:
    count = js_content.count(v)
    print(f"  View '{v}': referenced {count} times in JS")


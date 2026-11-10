import re
from bs4 import BeautifulSoup

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    js = f.read()
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=== 1. REPORT REFERENCES ===")
print("'view-report' in html:", 'view-report' in html)
print("'view-report' in js:", 'view-report' in js)
report_navs = list(re.finditer(r'navigateToView\([\'"]([^\'"]+)[\'"]\)', js))
for rn in report_navs:
    print(f"navigateToView('{rn.group(1)}') called at char {rn.start()}")

print("\n=== 2. COMPLETE INTERVIEW FLOW / RESULTS ===")
# Look for completeInterview or showReport or results
matches = re.findall(r'function\s+([a-zA-Z0-9_]*(?:result|report|complete|finish|score)[a-zA-Z0-9_]*)\s*\(', js, re.I)
print("Functions related to result/report/complete/score:")
print(set(matches))

# Look for report elements in HTML
print("\n=== 3. REPORT ELEMENTS IN HTML ===")
report_els = soup.find_all(lambda tag: tag.has_attr('id') and ('report' in tag['id'].lower() or 'result' in tag['id'].lower() or 'summary' in tag['id'].lower()))
for el in report_els[:20]:
    print(f"<{el.name}> id='{el.get('id')}' class='{el.get('class')}'")


# Inspect view-report
import re
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'<[^>]+id=[\'"]view-report[\'"][^>]*>', text)
if m:
    print('Found tag:', m.group(0))
    idx = m.start()
    print('Context:')
    print(text[max(0, idx-100):min(len(text), idx+400)])
else:
    print('view-report exact tag not found. Searching for occurrences of view-report:')
    for m2 in re.finditer(r'view-report', text):
        print(f"Occurrence at {m2.start()}: {text[m2.start()-40:m2.start()+60]}")

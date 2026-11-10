import os
import re
from bs4 import BeautifulSoup

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print('=== 1. VIEWS / PANELS ===')
view_panels = soup.find_all(class_=re.compile(r'view-panel'))
for vp in view_panels:
    print(f"Panel: id={vp.get('id')} class={vp.get('class')}")

print('\n=== 2. MODALS & OVERLAYS ===')
for tag in soup.find_all(True):
    tid = tag.get('id', '')
    tcls = ' '.join(tag.get('class', []))
    if any(k in tid.lower() or k in tcls.lower() for k in ['modal', 'overlay', 'dialog', 'popup']):
        print(f"<{tag.name}> id='{tid}' class='{tcls}'")

print('\n=== 3. ALL FORMS ===')
forms = soup.find_all('form')
for form in forms:
    print(f"Form: id='{form.get('id')}' action='{form.get('action')}' method='{form.get('method')}'")

print('\n=== 4. NAVIGATION LINKS ===')
nav_links = soup.find_all(['a', 'button'], class_=re.compile(r'nav|tab|btn-nav'))
for nl in nav_links[:30]:
    print(f"<{nl.name}> id='{nl.get('id')}' href='{nl.get('href')}' onclick='{nl.get('onclick')}' text='{nl.get_text(strip=True)[:30]}'")

print(f'\nTotal tags: {len(soup.find_all(True))}')
print(f'Total buttons: {len(soup.find_all("button"))}')
print(f'Total inputs: {len(soup.find_all("input"))}')
print(f'Total selects: {len(soup.find_all("select"))}')
print(f'Total links: {len(soup.find_all("a"))}')

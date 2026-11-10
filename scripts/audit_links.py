from bs4 import BeautifulSoup

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

links = soup.find_all('a')
print(f"Total links: {len(links)}")

all_ids = set(el['id'] for el in soup.find_all(attrs={"id": True}))

for idx, a in enumerate(links, 1):
    href = a.get('href', '')
    aid = a.get('id', '')
    cls = ' '.join(a.get('class', []))
    text = a.get_text(strip=True)[:35]
    
    # Check if target anchor exists in document if href starts with #
    status = "OK"
    if href.startswith('#'):
        target_id = href[1:]
        if target_id and target_id not in all_ids:
            status = f"BROKEN_ANCHOR (#{target_id} NOT FOUND)"
    elif href == '' or href == '#':
        status = "EMPTY_OR_HASH_ONLY"
        
    print(f"[{idx:02d}] href='{href:<25}' id='{aid:<20}' text='{text:<30}' status={status}")

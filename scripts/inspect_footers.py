from bs4 import BeautifulSoup

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

footers = soup.find_all('footer')
print(f"Total footers in HTML: {len(footers)}")
for idx, foot in enumerate(footers, 1):
    parent = foot.find_parent(class_='view-panel')
    parent_id = parent.get('id') if parent else 'root/unknown'
    print(f"\nFooter {idx} inside view: '{parent_id}'")
    links = foot.find_all(['a', 'button'])
    for l in links:
        print(f"   <{l.name}> id='{l.get('id')}' href='{l.get('href')}' text='{l.get_text(strip=True)}'")


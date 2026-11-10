with open('frontend/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('body.in-interview .navbar')
print(text[pos-100:pos+300])

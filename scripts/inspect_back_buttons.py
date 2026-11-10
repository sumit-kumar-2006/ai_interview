with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('btn-back-home')
print(text[pos-100:pos+300])

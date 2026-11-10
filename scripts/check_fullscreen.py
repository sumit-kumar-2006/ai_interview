with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('fullscreen')
if pos != -1:
    print("Found fullscreen at:", pos, text[pos-30:pos+150])
else:
    print("Not found fullscreen in script.js")

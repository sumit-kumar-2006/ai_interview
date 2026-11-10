with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('window.location.hash')
print('hash:', pos)
pos2 = text.find('navigateToView')
print('navigateToView first call:', text[pos2-100:pos2+200])


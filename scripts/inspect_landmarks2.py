with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function processMediaPipeLandmarks(')
print(text[pos+2000:pos+4500])

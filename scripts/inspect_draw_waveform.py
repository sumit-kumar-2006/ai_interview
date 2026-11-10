with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function drawWaveform(')
print(text[pos:pos+1500])

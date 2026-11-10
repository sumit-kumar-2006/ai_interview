with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('async function startInterview(')
if pos == -1:
    pos = text.find('function startInterview(')

print(text[pos:pos+2500])

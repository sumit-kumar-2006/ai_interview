with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function initQuestionWorkspace(')
print(text[pos:pos+2500])

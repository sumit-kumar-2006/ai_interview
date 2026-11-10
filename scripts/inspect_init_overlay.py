with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('async function runInterviewRoomInitialization(')
print(text[pos+1000:pos+3500])

with open('backend/app/questions.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '"javascript": ['
pos = text.find(target)
print(text[pos:pos+500])

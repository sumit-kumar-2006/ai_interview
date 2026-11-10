with open('backend/app/questions.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('"javascript":')
if pos != -1:
    print(text[pos:pos+1500])
else:
    print("No javascript key in TECH_QUESTION_BANK")

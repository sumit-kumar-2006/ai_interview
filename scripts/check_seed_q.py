with open('database/seed_questions.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('generator')
print("generator in seed_questions:", pos)

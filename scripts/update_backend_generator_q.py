with open('backend/app/questions.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '"javascript": [\n        {'
replacement = '''"javascript": [
        {
            "id": 700,
            "question": "Explain what a generator function is in JavaScript.",
            "topic": "JavaScript Iterators & Generators",
            "category": "Frontend & Web Development",
            "difficulty": "Medium",
            "expected_answer": "A generator function in JavaScript is defined with function* and uses the yield keyword to pause execution and produce values lazily. Calling a generator returns an iterator object with a next() method that yields an object with value and done properties. They are ideal for custom iterables, infinite streams, state machines, and handling asynchronous control flows.",
            "reference_answer": "A generator function in JavaScript is defined with function* and uses the yield keyword to pause execution and produce values lazily. Calling a generator returns an iterator object with a next() method that yields an object with value and done properties. They are ideal for custom iterables, infinite streams, state machines, and handling asynchronous control flows.",
            "required_concepts": ["function*", "yield", "iterator", "next()", "pause and resume execution"],
            "optional_concepts": ["lazy evaluation", "generator object", "value and done properties", "iterables"],
            "acceptable_alternatives": ["Explain generators in JS", "How do JavaScript generator functions work"],
            "misconceptions": [
                {"concept": "regular function execution", "correction": "Generator functions do not run immediately to completion; calling them returns an iterator that pauses at yield statements."}
            ]
        },
        {'''

assert target in text, "Target block not found in backend/app/questions.py"
updated = text.replace(target, replacement, 1)

with open('backend/app/questions.py', 'w', encoding='utf-8') as f:
    f.write(updated)

print("SUCCESS: Added generator function question specification to backend/app/questions.py")

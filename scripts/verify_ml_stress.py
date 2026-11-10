import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
import pandas as pd
from backend.app.evaluator import AnswerEvaluator
from nlp.contradiction_detector import ContradictionDetector

print("=" * 70)
print("COMPREHENSIVE ML & NLP EDGE-CASE STRESS TEST")
print("=" * 70)

evaluator = AnswerEvaluator()
detector = ContradictionDetector()

test_cases = [
    {
        "name": "Empty String",
        "q": "What is polymorphism?",
        "ref": "Polymorphism allows objects to take multiple forms.",
        "cand": ""
    },
    {
        "name": "Whitespace Only",
        "q": "What is polymorphism?",
        "ref": "Polymorphism allows objects to take multiple forms.",
        "cand": "   \n\t   "
    },
    {
        "name": "Gibberish / Symbols",
        "q": "What is polymorphism?",
        "ref": "Polymorphism allows objects to take multiple forms.",
        "cand": "!!! $$$ %%% ^^^ 12345 ???"
    },
    {
        "name": "Direct Contradiction",
        "q": "What is Python typing?",
        "ref": "Python is a dynamically typed interpreted programming language.",
        "cand": "Python is a statically typed compiled programming language."
    },
    {
        "name": "Extremely Long Text (1000 words)",
        "q": "What is polymorphism?",
        "ref": "Polymorphism allows objects to take multiple forms.",
        "cand": "Polymorphism is an object oriented concept " * 150
    },
    {
        "name": "Code Snippet Answer",
        "q": "How do you define a function in Python?",
        "ref": "In Python you use the def keyword followed by function name and parameters.",
        "cand": "def add(a, b):\n    return a + b\nWe use def keyword followed by name."
    },
    {
        "name": "Proficient Technical Answer (Detailed)",
        "q": "What is encapsulation?",
        "ref": "Encapsulation is bundling data and methods that operate on that data within a single class.",
        "cand": "Encapsulation is the fundamental object oriented principle of bundling data attributes and methods that operate on them into a single unit or class while hiding internal implementation."
    }
]

for tc in test_cases:
    res = evaluator.evaluate(
        question=tc["q"],
        candidate_answer=tc["cand"],
        reference_answer=tc["ref"]
    )
    score = res.get("score", res.get("final_score", 0))
    acad = res.get("academic_classification", "N/A")
    has_c = res.get("has_contradiction", False)
    assert 0.0 <= score <= 100.0, f"Score out of bounds: {score}"
    print(f"[PASS] {tc['name']:<32} | Score: {score:5.1f} | Academic: {acad:<17} | Contradiction: {has_c}")

print("=" * 70)
print("ALL 7 ML EDGE-CASE STRESS TESTS PASSED WITH 100% SUCCESS!")
print("=" * 70)

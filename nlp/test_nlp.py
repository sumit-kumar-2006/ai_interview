import sys
import math
sys.path.insert(0, r"d:\AI-Interview-Analyzer")

from nlp.answer_analyzer import analyze_answer


def run_nlp_tests():
    question = "What is polymorphism in object oriented programming?"
    reference_answer = (
        "Polymorphism is an object-oriented programming concept where the same interface "
        "can be used for different underlying forms or classes. It allows a single method call "
        "to behave differently depending on the object invoking it."
    )

    print("==================================================")
    print("RUNNING NLP ANSWER INTELLIGENCE SUITE")
    print("==================================================")

    # ----------------------------------------------------
    # TEST 1: Strong answer matching reference
    # ----------------------------------------------------
    cand1 = "Polymorphism allows objects of different classes to respond to the same interface or method call in their own specific way."
    res1 = analyze_answer(question, cand1, reference_answer)
    print("\n--- TEST 1: Strong Answer ---")
    print("Relevance:", res1["relevance_score"])
    print("Concept Coverage:", res1["concept_coverage"])
    print("Completeness:", res1["completeness"])
    print("Strengths:", res1["strengths"])
    print("AI Feedback:", res1["ai_feedback"])

    assert res1["status"] == "success"
    assert res1["relevance_score"] >= 65.0
    assert res1["concept_coverage"] >= 40.0
    assert not math.isnan(res1["relevance_score"])
    assert len(res1["strengths"]) > 0

    # ----------------------------------------------------
    # TEST 2: Partially correct answer
    # ----------------------------------------------------
    cand2 = "Polymorphism means same method name used differently."
    res2 = analyze_answer(question, cand2, reference_answer)
    print("\n--- TEST 2: Partially Correct Answer ---")
    print("Relevance:", res2["relevance_score"])
    print("Concept Coverage:", res2["concept_coverage"])
    print("Completeness:", res2["completeness"])
    print("Areas for Improvement:", res2["areas_for_improvement"])

    assert res2["status"] == "success"
    assert 0.0 <= res2["relevance_score"] <= 100.0
    assert len(res2["areas_for_improvement"]) >= 0

    # ----------------------------------------------------
    # TEST 3: "I don't know"
    # ----------------------------------------------------
    cand3 = "I don't know the answer to this question."
    res3 = analyze_answer(question, cand3, reference_answer)
    print("\n--- TEST 3: 'I don't know' ---")
    print("Status:", res3["status"])
    print("Relevance:", res3["relevance_score"])
    print("AI Feedback:", res3["ai_feedback"])

    assert res3["status"] in ["honest_no_answer", "success"]
    assert res3["relevance_score"] == 0.0
    assert res3["concept_coverage"] == 0.0

    # ----------------------------------------------------
    # TEST 4: Empty answer
    # ----------------------------------------------------
    cand4 = ""
    res4 = analyze_answer(question, cand4, reference_answer)
    print("\n--- TEST 4: Empty Answer ---")
    print("Status:", res4["status"])
    print("Relevance:", res4["relevance_score"])

    assert res4["status"] == "no_answer"
    assert res4["relevance_score"] == 0.0
    assert res4["completeness"] == 0.0

    # ----------------------------------------------------
    # TEST 5: Unrelated answer
    # ----------------------------------------------------
    cand5 = "Photosynthesis is the process by which green plants turn sunlight into energy."
    res5 = analyze_answer(question, cand5, reference_answer)
    print("\n--- TEST 5: Unrelated Answer ---")
    print("Relevance:", res5["relevance_score"])
    print("Concept Coverage:", res5["concept_coverage"])
    print("Areas for Improvement:", res5["areas_for_improvement"])

    assert res5["relevance_score"] < 45.0
    assert res5["concept_coverage"] == 0.0
    assert len(res5["areas_for_improvement"]) > 0

    # ----------------------------------------------------
    # TEST 6: Long but irrelevant answer
    # ----------------------------------------------------
    cand6 = (
        "In modern web development, JavaScript frameworks like React, Vue, and Angular "
        "have revolutionized state management and virtual DOM rendering across frontend applications. "
        "Furthermore, Node.js allows asynchronous non-blocking event-driven servers."
    )
    res6 = analyze_answer(question, cand6, reference_answer)
    print("\n--- TEST 6: Long Irrelevant Answer ---")
    print("Relevance:", res6["relevance_score"])
    print("Completeness:", res6["completeness"])
    print("Areas for Improvement:", res6["areas_for_improvement"])

    assert res6["relevance_score"] < 45.0
    assert res6["completeness"] < 45.0  # Must NOT reward verbosity for off-topic content
    assert not math.isnan(res6["completeness"])

    print("\n==================================================")
    print("ALL 6 NLP TESTS PASSED PERFECTLY!")
    print("==================================================")

if __name__ == "__main__":
    run_nlp_tests()
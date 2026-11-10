import pytest
from sentence_transformers import SentenceTransformer
from backend.app.evaluator import AnswerEvaluator

@pytest.fixture(scope="module")
def evaluator():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return AnswerEvaluator(model)

def test_rule_a_equivalent_correct_wording(evaluator):
    """Rule A: Award high score even if candidate uses different wording from reference."""
    question = "What is the Global Interpreter Lock (GIL) in Python and why does it exist?"
    ref = "The GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once to ensure thread safety with CPython's reference counting memory management."
    
    # Candidate uses completely different phrasing, synonyms, but technically accurate
    candidate = "In CPython, a mutual exclusion mechanism ensures memory management via reference counters stays thread-safe by stopping concurrent native bytecode interpretation across CPU cores."
    spec = {
        "expected_answer": ref,
        "required_concepts": ["mutex", "thread safety", "reference counting", "bytecodes"],
        "optional_concepts": ["multiprocessing", "io bound"],
        "acceptable_alternatives": ["subinterpreters", "multiprocessing module"],
        "common_misconceptions": ["gil prevents multiprocessing", "gil speeds up multi core cpu"],
        "rubric": {"mutex_definition": 35, "memory_management_ref_counting": 35, "single_thread_bytecode_concurrency": 30}
    }
    
    result = evaluator.evaluate(question, candidate, ref, evaluation_spec=spec)
    assert result["final_score"] >= 80.0, f"Expected >= 80 for equivalent wording, got {result['final_score']}"
    assert len(result["correct_concepts"]) >= 2
    assert len(result["incorrect_claims"]) == 0

def test_rule_b_correct_but_incomplete_answer(evaluator):
    """Rule B: Partial credit based on correctly explained concepts."""
    question = "What is database normalization and why is Third Normal Form (3NF) important?"
    ref = "Normalization reduces redundancy. 3NF requires 2NF and ensures every non-key column depends solely on the primary key, eliminating transitive dependencies."
    
    # Explains normalization and 2NF, but completely omits transitive dependencies / non-key attributes
    candidate = "Database normalization helps reduce data duplication across tables and organizes relational schemas."
    spec = {
        "expected_answer": ref,
        "required_concepts": ["redundancy", "3NF", "transitive dependencies", "primary key"],
        "rubric": {"redundancy_reduction": 30, "non_key_dependence": 35, "transitive_dependency_removal": 35}
    }
    
    result = evaluator.evaluate(question, candidate, ref, evaluation_spec=spec)
    assert 25.0 <= result["final_score"] <= 65.0, f"Expected partial credit 25-65, got {result['final_score']}"
    assert "redundancy" in result["correct_concepts"]
    assert any("transitive" in m.lower() for m in result["missing_concepts"])

def test_rule_c_misconceptions_penalized(evaluator):
    """Rule C: Do not award high score for keyword matches with incorrect technical claims."""
    question = "What is the Global Interpreter Lock (GIL) in Python?"
    ref = "The GIL is a mutex preventing simultaneous thread execution to protect reference counting."
    
    # Contains relevant keywords (threads, Python, execution, lock) but makes completely false claims
    candidate = "The Python GIL is an accelerator lock that makes multithreaded Python code execute simultaneously across all 16 CPU cores at 10x faster speed and eliminates the need for locks."
    spec = {
        "expected_answer": ref,
        "required_concepts": ["mutex", "thread safety", "reference counting"],
        "common_misconceptions": [
            "makes multithreaded code faster",
            "allows simultaneous multi core cpu execution",
            "executes simultaneously across all cores",
            "accelerator lock"
        ],
        "rubric": {"mutex_thread_safety": 50, "reference_counting": 50}
    }
    
    result = evaluator.evaluate(question, candidate, ref, evaluation_spec=spec)
    assert result["final_score"] < 30.0, f"Expected < 30 due to misconceptions penalty, got {result['final_score']}"
    assert len(result["incorrect_claims"]) > 0

def test_rule_d_completely_unrelated_answer(evaluator):
    """Rule D: Completely unrelated answers receive zero or near-zero marks."""
    question = "How does indexing improve query performance in PostgreSQL?"
    ref = "Indexes provide B-tree data structures allowing O(log N) searches instead of sequential table scans."
    
    candidate = "I really enjoy baking sourdough bread on weekends because fermentation takes about twenty-four hours."
    
    result = evaluator.evaluate(question, candidate, ref)
    assert result["final_score"] <= 10.0, f"Expected <= 10 for completely unrelated answer, got {result['final_score']}"

def test_rule_e_empty_or_whitespace_answer(evaluator):
    """Rule E: Empty or no response receives zero score with explicit no_answer flag."""
    question = "Explain RESTful API idempotent methods."
    ref = "GET, PUT, and DELETE are idempotent because multiple identical requests produce the same server state."
    
    result = evaluator.evaluate(question, "   ", ref)
    assert result["final_score"] == 0.0
    assert result["relevance_score"] == 0.0
    assert result["strengths"] == []
    assert "No answer provided" in result["weaknesses"][0]

def test_rule_f_alternative_valid_implementation(evaluator):
    """Rule F: Accept technically valid alternatives without forcing one specific approach."""
    question = "How would you handle heavy CPU-bound computation in Python without being throttled by the GIL?"
    ref = "Use Python's multiprocessing module to spawn separate OS processes with independent memory spaces."
    
    # Alternative: Using Cython with nogil block or C-extensions, or ProcessPoolExecutor
    candidate = "Instead of multiprocessing, I release the GIL using Cython with a nogil block, or delegate the calculation to a NumPy C-extension or Rust PyO3 module."
    spec = {
        "expected_answer": ref,
        "required_concepts": ["multiprocessing", "separate processes", "concurrency"],
        "acceptable_alternatives": ["cython nogil", "c extension", "rust pyo3", "processpoolexecutor", "c-extensions"],
        "rubric": {"concurrency_solution": 60, "explanation": 40}
    }
    
    result = evaluator.evaluate(question, candidate, ref, evaluation_spec=spec)
    assert result["final_score"] >= 80.0, f"Expected >= 80 for valid alternative approach, got {result['final_score']}"

def test_rule_g_technical_definition_correctness(evaluator):
    """Rule G: Deterministic verification of technical definitions and concepts."""
    question = "What is the difference between an abstract class and an interface in Java?"
    ref = "An abstract class can have concrete method implementations and state fields, whereas an interface defines a contract of method signatures and default methods."
    
    candidate = "Abstract classes in Java can have instance member fields and partial implementations with constructors, whereas interfaces cannot maintain mutable instance state."
    spec = {
        "expected_answer": ref,
        "required_concepts": ["state", "fields", "implementations", "contract"],
        "rubric": {"state_and_fields": 50, "implementation_contract": 50}
    }
    
    result = evaluator.evaluate(question, candidate, ref, evaluation_spec=spec)
    assert result["final_score"] >= 75.0
    assert len(result["correct_concepts"]) >= 2


def test_nli_polarity_inversion_contradiction_penalized(evaluator):
    """Test that NLI contradiction filter catches antipodal property inversions and penalizes heavily."""
    question = "What is the difference between list comprehensions and generators in Python?"
    ref = "List comprehensions compute values eagerly in memory, whereas generators compute values lazily on demand."
    
    # Candidate asserts the exact opposite polarities for both concepts
    candidate = "List comprehensions are lazy while generators are eager and compute everything upfront."
    spec = {
        "expected_answer": ref,
        "required_concepts": ["eager", "lazy", "memory"],
        "rubric": {"accuracy": 100}
    }
    
    result = evaluator.evaluate(question, candidate, ref, evaluation_spec=spec)
    assert result["has_contradiction"] is True
    assert len(result["contradictions_detected"]) > 0
    assert result["final_score"] < 40.0
    assert any("lazy" in c["explanation"] or "eager" in c["explanation"] for c in result["contradictions_detected"])


def test_nli_negation_inversion_contradiction_penalized(evaluator):
    """Test that NLI contradiction filter catches factual capability negation flips."""
    question = "Are Python strings mutable or immutable?"
    ref = "Strings in Python are immutable and cannot be modified in place."
    
    # Candidate asserts mutability and modification capability
    candidate = "Strings in Python are mutable and you are able to modify strings directly in memory."
    
    result = evaluator.evaluate(question, candidate, ref)
    assert result["has_contradiction"] is True
    assert len(result["contradictions_detected"]) > 0
    assert result["final_score"] < 40.0


def test_nli_accurate_response_has_zero_contradictions(evaluator):
    """Test that accurate and thorough technical explanations produce zero false positive contradictions."""
    question = "What is the difference between list comprehensions and generators in Python?"
    ref = "List comprehensions compute values eagerly in memory, whereas generators compute values lazily on demand."
    
    candidate = "List comprehensions evaluate elements eagerly and allocate memory all at once with O(N) space, whereas generators evaluate lazily yielding one element at a time with O(1) space."
    
    result = evaluator.evaluate(question, candidate, ref)
    assert result["has_contradiction"] is False
    assert len(result["contradictions_detected"]) == 0
    assert result["final_score"] >= 80.0


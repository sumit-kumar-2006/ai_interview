import os
import re
import math
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
import numpy as np
import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from backend.app.services.llm_provider import llm_provider
from nlp.answer_analyzer import extract_key_concepts, normalize_word, STOP_WORDS, get_embedding_model
from nlp.contradiction_detector import contradiction_detector

logger = logging.getLogger(__name__)

# Global ML Scoring Model Singleton (Audited RF Model)
_SCORING_MODEL = None

def get_scoring_model():
    """
    Loads ml/models/interview_scoring_model.pkl for informational comparison.
    NOTE: As audited, this RandomForest model was trained on synthetic targets
    (semantic_similarity * 0.85 + length_score * 0.15). Per architectural guidelines,
    it is NOT used as the authoritative technical correctness score.
    """
    global _SCORING_MODEL
    if _SCORING_MODEL is None:
        model_path = os.path.join("ml", "models", "interview_scoring_model.pkl")
        if os.path.exists(model_path):
            try:
                _SCORING_MODEL = joblib.load(model_path)
            except Exception as e:
                logger.warning(f"Could not load scoring model from {model_path}: {e}")
                _SCORING_MODEL = None
    return _SCORING_MODEL


# Global Academic Classifier Singleton (Decision Tree / SVM / KNN from Part A)
_ACADEMIC_CLASSIFIER = None

def get_academic_classifier():
    """
    Loads ml/models/decision_tree_model.pkl trained on Part A academic features:
    ['semantic_similarity', 'lexical_overlap', 'word_count', 'unique_word_ratio', 'avg_word_length'].
    Outputs binary classification: 1 ('Proficient') vs 0 ('Needs Improvement').
    """
    global _ACADEMIC_CLASSIFIER
    if _ACADEMIC_CLASSIFIER is None:
        path = os.path.join("ml", "models", "decision_tree_model.pkl")
        if os.path.exists(path):
            try:
                _ACADEMIC_CLASSIFIER = joblib.load(path)
            except Exception as e:
                logger.warning(f"Could not load academic classifier from {path}: {e}")
                _ACADEMIC_CLASSIFIER = None
    return _ACADEMIC_CLASSIFIER


# Common Technical Concept Synonyms & Paraphrases (Rule A)
TECH_SYNONYMS: Dict[str, List[str]] = {
    "interface": ["contract", "public contract", "unified contract", "specification", "protocol", "api"],
    "classes": ["types", "subclass", "subclasses", "derived classes", "objects", "entities"],
    "method call": ["calling a method", "method invocation", "invoking", "invoking a method", "function call", "method"],
    "polymorphism": ["polymorphic", "dynamic dispatch", "multiple forms", "subclass behavior", "runtime dispatch"],
    "gil": ["global interpreter lock", "interpreter lock"],
    "mutex": ["lock", "mutual exclusion", "synchronization lock"],
    "cpu-bound": ["computationally heavy", "cpu intensive", "math heavy", "cpu tasks"],
    "i/o-bound": ["network", "disk", "database calls", "input output", "blocking i/o"],
    "multiprocessing": ["multiple processes", "process pool", "separate processes"],
    "eager": ["immediately", "in memory all at once", "evaluates all", "allocates upfront"],
    "lazy": ["on demand", "deferred", "generator", "yield", "streaming"],
    "memory": ["ram", "space", "allocation", "o(1)"],
    "yield": ["generator", "generates values", "generator expression"],
    "n+1": ["multiple queries", "loop queries", "separate queries for each"],
    "select_related": ["sql join", "join query"],
    "prefetch_related": ["separate query with in", "batch in query", "prefetches in python"],
    "state machine": ["iasyncstatemachine", "generated struct", "compiler transformation"],
    "continuation": ["callback", "resumes execution"],
    "event loop": ["single-threaded loop", "call stack coordination"],
    "micro-task queue": ["microtask", "promise queue", "job queue"],
    "macro-task queue": ["macrotask", "task queue", "timer queue"],
    "b-tree": ["b+tree", "balanced tree", "sorted tree index", "b-tree / b+tree"],
    "mvcc": ["multi-version", "undo logs", "snapshots", "read consistency"],
    "http methods": ["http verbs", "verbs", "methods", "standard http verbs", "rest verbs", "get post", "get, post, put, delete"],
    "methods": ["verbs", "http verbs"],
    "stateless": ["statelessness", "no server session", "without session state"],
    "statelessness": ["stateless", "no session stored"],
    "redundancy": ["duplication", "data duplication", "duplicate data", "repeated data", "redundant data", "duplicates", "duplicate"],
    "transitive dependencies": ["transitive dependency", "indirect dependency"],
    "3nf": ["third normal form", "3rd normal form"],
    "third normal form": ["3nf", "3rd normal form"]
}


class AnswerEvaluator:
    """
    Enterprise Technical Answer Evaluation Engine.
    Implements multi-factor rubric assessment adhering strictly to Rules A through H:
      - Rule A: High scores for correct/complete answers despite different phrasing
      - Rule B: Fair partial credit based on correctly explained concepts
      - Rule C: Penalizes related but incorrect claims and common misconceptions
      - Rule D: Zero/near-zero for completely unrelated responses
      - Rule E: Zero for silence or empty answers, distinguished from mic failure
      - Rule F: Rewards alternative valid architectures and implementations
      - Rule G: Deterministic verification for technical definitions and complexities
      - Rule H: Flags ambiguous or insufficient reference answers
    Supports configured LLM evaluators with automatic schema validation and transparent fallback.
    """

    def __init__(self, embedding_model: Optional[SentenceTransformer] = None):
        self.embedding_model = embedding_model if embedding_model is not None else get_embedding_model()
        self.scoring_model = get_scoring_model()
        self._emb_cache: Dict[str, np.ndarray] = {}

    def _encode_cached(self, text: str) -> np.ndarray:
        """Cached SentenceTransformer encoding to eliminate redundant vector operations."""
        cleaned = text.strip()
        if not cleaned:
            return np.zeros((1, 384))
        if cleaned not in self._emb_cache:
            if self.embedding_model is not None:
                self._emb_cache[cleaned] = self.embedding_model.encode([cleaned])
            else:
                return np.zeros((1, 384))
        return self._emb_cache[cleaned]

    def evaluate(
        self,
        question: str,
        candidate_answer: str,
        reference_answer: str,
        evaluation_spec: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main evaluation entrypoint.
        Evaluates candidate_answer against question, reference_answer, and evaluation_spec.
        """
        cand_text = candidate_answer.strip() if candidate_answer else ""
        ref_text = reference_answer.strip() if reference_answer else ""
        q_text = question.strip() if question else ""
        spec = evaluation_spec or {}

        # ---------------------------------------------------------------------
        # 1. RULE E: EMPTY ANSWER OR SILENCE DETECTION
        # ---------------------------------------------------------------------
        if not cand_text:
            return {
                "score": 0.0,
                "final_score": 0.0,
                "relevance_score": 0.0,
                "semantic_similarity": 0.0,
                "concept_coverage": 0.0,
                "completeness": 0.0,
                "correct_concepts": [],
                "missing_concepts": spec.get("required_concepts") or extract_key_concepts(ref_text),
                "incorrect_claims": [],
                "contradictions_detected": [],
                "has_contradiction": False,
                "explanation": "No spoken or written response was submitted for evaluation.",
                "improvement_suggestions": ["Ensure your microphone is recording and articulate your technical explanation clearly."],
                "strengths": [],
                "weaknesses": ["No answer provided."],
                "feedback": "No answer detected. Please record or type your response.",
                "status": "no_answer",
                "evaluation_mode": "empty_input",
                "rf_predicted_score": 0.0
            }

        # ---------------------------------------------------------------------
        # 2. RULE E: NON-COMMITTAL "I DON'T KNOW"
        # ---------------------------------------------------------------------
        idk_patterns = [r"\bi\s+don'?t\s+know\b", r"\bno\s+idea\b", r"\bnot\s+sure\b", r"\bi\s+have\s+no\s+clue\b"]
        words = cand_text.split()
        if len(words) <= 8 and any(re.search(pat, cand_text, re.IGNORECASE) for pat in idk_patterns):
            ref_concepts = spec.get("required_concepts") or extract_key_concepts(ref_text)
            return {
                "score": 0.0,
                "final_score": 0.0,
                "relevance_score": 0.0,
                "semantic_similarity": 0.0,
                "concept_coverage": 0.0,
                "completeness": 0.0,
                "correct_concepts": [],
                "missing_concepts": ref_concepts,
                "incorrect_claims": [],
                "contradictions_detected": [],
                "has_contradiction": False,
                "explanation": "The candidate candidly acknowledged unfamiliarity with the topic.",
                "improvement_suggestions": ["Review foundational concepts and study the reference explanation."],
                "strengths": ["Honest acknowledgment of topic unfamiliarity."],
                "weaknesses": ["Did not attempt technical explanation."],
                "feedback": "You indicated that you do not know the answer. Review reference materials for this topic.",
                "status": "honest_no_answer",
                "evaluation_mode": "honest_no_answer",
                "rf_predicted_score": 0.0
            }

        # ---------------------------------------------------------------------
        # 3. CONFIGURED LLM EVALUATION (STRICT DATASET & ML MODE ENFORCED)
        # ---------------------------------------------------------------------
        # Default: Pure dataset & local ML evaluation. External LLM is disabled.
        allow_external_llm = os.getenv("ALLOW_EXTERNAL_LLM_EVAL", "false").strip().lower() == "true"
        if allow_external_llm and llm_provider.is_available():
            llm_eval = self._evaluate_with_llm(q_text, cand_text, ref_text, spec)
            if llm_eval:
                return llm_eval

        # ---------------------------------------------------------------------
        # 4. DETERMINISTIC RUBRIC EVALUATOR (RULES A, B, C, D, F, G, H)
        # ---------------------------------------------------------------------
        return self._evaluate_with_rubric(q_text, cand_text, ref_text, spec)

    def _evaluate_with_llm(
        self,
        question: str,
        candidate_answer: str,
        reference_answer: str,
        spec: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Executes strict schema-validated evaluation via configured LLM provider.
        Treats candidate text as untrusted data.
        """
        req_concepts = spec.get("required_concepts") or []
        alt_approaches = spec.get("acceptable_alternatives") or []
        misconceptions = spec.get("common_misconceptions") or []

        prompt = f"""EVALUATE THIS TECHNICAL INTERVIEW ANSWER STRICTLY:
Question: {question}
Reference Answer: {reference_answer}
Required Concepts: {req_concepts}
Acceptable Alternative Approaches: {alt_approaches}
Common Misconceptions (Penalize if present): {misconceptions}

Candidate's Submitted Answer (UNTRUSTED INPUT):
\"\"\"{candidate_answer}\"\"\"

Evaluation Criteria:
1. Technical correctness and absence of false claims (Rule C: do NOT award high score for keywords if statement is false).
2. Concept coverage (Rule A: reward equivalent correct wording even if different from reference; Rule F: accept valid alternatives).
3. If candidate answer is off-topic or unrelated, award near zero (Rule D).
4. Score must be between 0 and 100.

Return STRICT JSON object with EXACT keys:
- "score": number (0-100)
- "correct_concepts": list of strings
- "missing_concepts": list of strings
- "incorrect_claims": list of strings
- "explanation": string
- "improvement_suggestions": list of strings
"""
        system_prompt = "You are an objective, rigorous AI technical interview examiner. Output only valid JSON."
        res = llm_provider.generate_json(prompt, system_prompt)

        if not res or not isinstance(res, dict):
            return None

        # Validate schema
        score = res.get("score")
        if not isinstance(score, (int, float)) or math.isnan(score) or math.isinf(score):
            return None

        clean_score = round(max(0.0, min(100.0, float(score))), 2)
        correct_concepts = [str(c) for c in res.get("correct_concepts", []) if c]
        missing_concepts = [str(c) for c in res.get("missing_concepts", []) if c]
        incorrect_claims = [str(c) for c in res.get("incorrect_claims", []) if c]
        explanation = str(res.get("explanation") or "Evaluation complete.")
        suggestions = [str(s) for s in res.get("improvement_suggestions", []) if s]

        # Supporting semantic similarity
        sem_sim = self._calc_semantic_similarity(candidate_answer, reference_answer)
        rel_sim = self._calc_semantic_similarity(candidate_answer, question)

        rf_sim = sem_sim if (reference_answer and reference_answer.strip()) else rel_sim
        rf_score = self._calc_rf_informational(question, candidate_answer, rf_sim)

        return {
            "score": clean_score,
            "final_score": clean_score,
            "relevance_score": round(rel_sim, 2),
            "semantic_similarity": round(sem_sim, 2),
            "concept_coverage": round((len(correct_concepts) / max(1, len(correct_concepts) + len(missing_concepts))) * 100.0, 2),
            "completeness": clean_score,
            "correct_concepts": correct_concepts,
            "missing_concepts": missing_concepts,
            "incorrect_claims": incorrect_claims,
            "contradictions_detected": [],
            "has_contradiction": len(incorrect_claims) > 0,
            "explanation": explanation,
            "improvement_suggestions": suggestions,
            "strengths": [f"Demonstrated solid grasp of {c}" for c in correct_concepts[:3]] if correct_concepts else ["Attempted response to technical prompt."],
            "weaknesses": [f"Missing key concept: {c}" for c in missing_concepts[:3]] + [f"Incorrect statement: {c}" for c in incorrect_claims[:2]],
            "feedback": explanation,
            "status": "success",
            "evaluation_mode": f"llm_{llm_provider.provider_name}",
            "rf_predicted_score": rf_score
        }

    def _evaluate_with_rubric(
        self,
        question: str,
        candidate_answer: str,
        reference_answer: str,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deterministic, transparent NLP and Rubric Evaluator enforcing Rules A through H.
        """
        cand_lower = candidate_answer.lower()
        ref_text = reference_answer.strip() if reference_answer else ""
        cand_tokens = set(re.findall(r'\b[a-zA-Z0-9_\#\+\.]{2,}\b', cand_lower))
        cand_words = cand_text_words = [w for w in cand_lower.split() if w.strip()]

        # 1. Compute Semantic Similarity and Relevance
        sem_sim = self._calc_semantic_similarity(candidate_answer, reference_answer)
        rel_sim = self._calc_semantic_similarity(candidate_answer, question)

        # 2. Extract Concept Targets
        req_concepts = spec.get("required_concepts") or extract_key_concepts(reference_answer)
        opt_concepts = spec.get("optional_concepts") or []
        alt_approaches = spec.get("acceptable_alternatives") or []
        misconceptions = spec.get("common_misconceptions") or []

        # ---------------------------------------------------------------------
        # RULE H: AMBIGUOUS OR INSUFFICIENT REFERENCE ANSWER CHECK
        # ---------------------------------------------------------------------
        needs_review = False
        if not ref_text or len(ref_text.split()) < 4 or not req_concepts:
            needs_review = True

        # 3. CONCEPT MATCHING (Exact, Stemmed, and Semantic Embedding Match)
        correct_concepts: List[str] = []
        missing_concepts: List[str] = []

        # Pre-compute candidate sentence/clause phrases for semantic concept matching
        cand_phrases = [p.strip() for p in re.split(r'[,;.]', candidate_answer) if len(p.strip()) > 5]
        cand_phrase_embs = None
        if self.embedding_model is not None and cand_phrases:
            try:
                cand_phrase_embs = self.embedding_model.encode(cand_phrases)
            except Exception:
                cand_phrase_embs = None

        for concept in req_concepts:
            c_clean = concept.lower().strip()
            c_words = [w for w in c_clean.split() if w not in STOP_WORDS]
            matched = False

            if c_clean in cand_lower:
                matched = True
            elif all(w in cand_tokens or any(w in t for t in cand_tokens) for w in c_words if len(w) >= 3):
                matched = True
            else:
                norm_c = [normalize_word(w) for w in c_words if len(w) >= 3]
                norm_cand = {normalize_word(w) for w in cand_tokens}
                if norm_c and all(nc in norm_cand for nc in norm_c):
                    matched = True

            # Synonym check (Rule A)
            if not matched:
                for syn in TECH_SYNONYMS.get(c_clean, []):
                    if syn in cand_lower:
                        matched = True
                        break

            # Semantic concept embedding matching if literal words differ (Rule A)
            if not matched and self.embedding_model is not None and len(c_clean) >= 3:
                try:
                    c_emb = self._encode_cached(c_clean)
                    if cand_phrase_embs is not None:
                        sims = cosine_similarity(c_emb, cand_phrase_embs)[0]
                        if any(s >= 0.45 for s in sims):
                            matched = True
                    if not matched:
                        cand_full_emb = self._encode_cached(candidate_answer)
                        sim_full = float(cosine_similarity(c_emb, cand_full_emb)[0][0])
                        if sim_full >= 0.42:
                            matched = True
                except Exception:
                    pass

            if matched:
                correct_concepts.append(concept)
            else:
                missing_concepts.append(concept)

        # ---------------------------------------------------------------------
        # RULE F: ACCEPTABLE ALTERNATIVE IMPLEMENTATIONS
        # ---------------------------------------------------------------------
        alt_bonus = 0.0
        used_alternatives: List[str] = []
        for alt in alt_approaches:
            alt_clean = alt.lower()
            alt_keywords = [w for w in re.findall(r'\b[a-zA-Z0-9_\#\+\.]{3,}\b', alt_clean) if w not in STOP_WORDS]
            if len(alt_keywords) >= 2 and sum(1 for kw in alt_keywords if kw in cand_lower) >= max(2, len(alt_keywords) // 2):
                used_alternatives.append(alt)
                alt_bonus += 20.0

        # ---------------------------------------------------------------------
        # RULE D: COMPLETELY UNRELATED ANSWER CHECK
        # ---------------------------------------------------------------------
        # Only classify as unrelated if relevance and similarity are both low
        # AND no required concepts or alternatives were identified.
        is_unrelated = (rel_sim < 30.0 and sem_sim < 30.0 and len(correct_concepts) == 0 and len(used_alternatives) == 0)

        # ---------------------------------------------------------------------
        # RULE C: MISCONCEPTIONS & NLI CONTRADICTION DETECTION
        # ---------------------------------------------------------------------
        detected_incorrect_claims: List[str] = []
        contradictions_detected: List[Dict[str, Any]] = []

        try:
            detected_confs = contradiction_detector.detect_contradictions(
                question=question,
                candidate_answer=candidate_answer,
                reference_answer=reference_answer,
                spec=spec
            )
            for conf in detected_confs:
                contradictions_detected.append(conf)
                if conf["explanation"] not in detected_incorrect_claims:
                    detected_incorrect_claims.append(conf["explanation"])
        except Exception as e:
            logger.warning(f"Contradiction detection error: {e}")

        # Deterministic rubric misconceptions fallback check
        for misc in misconceptions:
            misc_clean = misc.lower()
            if misc_clean in cand_lower:
                if misc not in detected_incorrect_claims:
                    detected_incorrect_claims.append(misc)
                continue
            misc_keywords = [w for w in re.findall(r'\b[a-zA-Z0-9_\#\+\.]{3,}\b', misc_clean) if w not in STOP_WORDS]
            if len(misc_keywords) >= 2:
                matched_kw = [w for w in misc_keywords if w in cand_tokens]
                if len(matched_kw) == len(misc_keywords):
                    if misc not in detected_incorrect_claims:
                        detected_incorrect_claims.append(misc)
                elif len(misc_keywords) >= 3 and len(matched_kw) >= len(misc_keywords) - 1:
                    # Require critical assertion/action verbs to be present
                    critical_verbs = {"modifies", "modify", "requires", "require", "bypasses", "bypass", "eliminates", "accelerator", "faster"}
                    if any(v in misc_keywords for v in critical_verbs):
                        if any(v in cand_tokens for v in critical_verbs):
                            if misc not in detected_incorrect_claims:
                                detected_incorrect_claims.append(misc)
                    else:
                        if misc not in detected_incorrect_claims:
                            detected_incorrect_claims.append(misc)

        # Specific known technical contradictions (Rule C deterministic checks)
        if "polymorphism" in question.lower():
            if any(term in cand_lower for term in ["css", "html shape", "photosynthesis", "plant"]):
                expl = "Confused object-oriented polymorphism with visual styling or biology."
                if expl not in detected_incorrect_claims:
                    detected_incorrect_claims.append(expl)

        if "gil" in question.lower():
            if "threads provide multi-core parallel speedup" in cand_lower or "threads bypass gil for cpu" in cand_lower:
                expl = "Claimed Python native threads bypass the GIL on multi-core CPUs for CPU-bound tasks."
                if expl not in detected_incorrect_claims:
                    detected_incorrect_claims.append(expl)

        if "select_related" in question.lower() and "manytomany" in cand_lower:
            if "select_related for manytomany" in cand_lower or "select_related performs join on many to many" in cand_lower:
                expl = "Incorrectly stated select_related handles ManyToMany relationships (prefetch_related is required)."
                if expl not in detected_incorrect_claims:
                    detected_incorrect_claims.append(expl)

        # ---------------------------------------------------------------------
        # RULE G: DETERMINISTIC CHECKS
        # ---------------------------------------------------------------------
        deterministic_boost = 0.0
        # Time / Space complexity checks
        if "o(1)" in ref_text.lower() and "o(1)" in cand_lower:
            deterministic_boost += 5.0
        if "o(n)" in ref_text.lower() and "o(n)" in cand_lower:
            deterministic_boost += 5.0
        # SQL methods checks
        if "join" in ref_text.lower() and "union" in ref_text.lower():
            if "join" in cand_lower and "union" in cand_lower:
                deterministic_boost += 8.0

        # ---------------------------------------------------------------------
        # SCORING FORMULA INTEGRATION (0 - 100)
        # ---------------------------------------------------------------------
        total_req = max(1, len(req_concepts))
        concept_ratio = len(correct_concepts) / total_req
        concept_score = concept_ratio * 100.0

        if is_unrelated:
            # Rule D: completely unrelated
            final_score = min(10.0, rel_sim * 0.25)
            explanation = "The response is unrelated to the question asked."
        else:
            # Base scoring: 50% Concept Coverage, 25% Semantic Alignment, 25% Relevance
            base_score = (
                (0.50 * concept_score) +
                (0.25 * sem_sim) +
                (0.25 * rel_sim) +
                alt_bonus +
                deterministic_boost
            )

            # Rule A: High score for correct complete answers even with different wording
            if (concept_ratio >= 0.75 or (concept_ratio >= 0.50 and (sem_sim >= 55.0 or rel_sim >= 48.0))) and not detected_incorrect_claims:
                base_score = max(85.0, base_score)

            # Rule C: Heavy penalty for incorrect claims / misconceptions
            if detected_incorrect_claims:
                misconception_penalty = len(detected_incorrect_claims) * 35.0
                base_score = max(5.0, base_score - misconception_penalty)

            # Completeness cap if answer is exceedingly brief
            if len(cand_words) < 12 and concept_ratio < 0.6:
                base_score = min(base_score, 45.0)

            final_score = round(max(0.0, min(100.0, base_score)), 2)

            # Explanation synthesis
            if final_score >= 85.0:
                explanation = f"Excellent technical response. Thoroughly covered key concepts: {', '.join(correct_concepts[:4])}."
            elif final_score >= 65.0:
                explanation = f"Solid answer with accurate core ideas ({', '.join(correct_concepts[:3])})."
                if missing_concepts:
                    explanation += f" Could be strengthened by detailing {', '.join(missing_concepts[:2])}."
            elif final_score >= 40.0:
                explanation = f"Partially correct answer. Addressed {', '.join(correct_concepts[:2]) if correct_concepts else 'general context'} but missed essential technical concepts ({', '.join(missing_concepts[:3])})."
            else:
                if detected_incorrect_claims:
                    explanation = f"Answer contained technical misconceptions: {', '.join(detected_incorrect_claims[:2])}."
                else:
                    explanation = f"Answer lacked necessary technical depth. Missing required concepts: {', '.join(missing_concepts[:3])}."

        # Actionable Suggestions
        suggestions: List[str] = []
        if missing_concepts:
            suggestions.append(f"Incorporate specific technical explanation of: {', '.join(missing_concepts[:3])}.")
        if detected_incorrect_claims:
            suggestions.append(f"Clarify distinction regarding: {detected_incorrect_claims[0]}.")
        if not is_unrelated and len(cand_words) < 25:
            suggestions.append("Provide concrete architectural or implementation examples to demonstrate hands-on experience.")
        if not suggestions:
            suggestions.append("Continue demonstrating clear technical reasoning with trade-off analysis.")

        rf_sim = sem_sim if (reference_answer and reference_answer.strip()) else rel_sim
        rf_score = self._calc_rf_informational(question, candidate_answer, rf_sim)
        acad_class, acad_conf = self._calc_academic_classification(question, candidate_answer, sem_sim)

        return {
            "score": final_score,
            "final_score": final_score,
            "relevance_score": round(rel_sim, 2),
            "semantic_similarity": round(sem_sim, 2),
            "concept_coverage": round(concept_score, 2),
            "completeness": round(min(100.0, (len(cand_words) / max(1, len(ref_text.split()))) * 100.0), 2),
            "correct_concepts": correct_concepts,
            "missing_concepts": missing_concepts,
            "incorrect_claims": detected_incorrect_claims,
            "contradictions_detected": contradictions_detected,
            "has_contradiction": len(contradictions_detected) > 0,
            "used_alternatives": used_alternatives,
            "explanation": explanation,
            "improvement_suggestions": suggestions,
            "strengths": [f"Accurately articulated {c}" for c in correct_concepts[:3]] if correct_concepts else ["Engaged with technical topic."],
            "weaknesses": [f"Missing concept: {c}" for c in missing_concepts[:3]] + [f"Technical error: {c}" for c in detected_incorrect_claims[:2]],
            "feedback": explanation,
            "status": "success",
            "needs_review": needs_review,
            "evaluation_mode": "rubric_deterministic",
            "rf_predicted_score": rf_score,
            "academic_classification": acad_class,
            "academic_confidence": acad_conf
        }

    def _calc_semantic_similarity(self, text_a: str, text_b: str) -> float:
        """Computes cosine similarity (0-100) using SentenceTransformer or fallback."""
        if not text_a or not text_b:
            return 0.0

        if self.embedding_model is not None:
            try:
                emb_a = self.embedding_model.encode([text_a])
                emb_b = self.embedding_model.encode([text_b])
                sim = float(cosine_similarity(emb_a, emb_b)[0][0])
                return max(0.0, min(100.0, sim * 100.0))
            except Exception:
                pass

        # Lexical fallback
        toks_a = set(re.findall(r'\b[a-zA-Z]{3,}\b', text_a.lower())) - STOP_WORDS
        toks_b = set(re.findall(r'\b[a-zA-Z]{3,}\b', text_b.lower())) - STOP_WORDS
        if not toks_b:
            return 50.0
        overlap = len(toks_a & toks_b) / len(toks_b)
        return max(0.0, min(100.0, overlap * 100.0))

    def _calc_rf_informational(self, question: str, candidate_answer: str, question_similarity: float) -> Optional[float]:
        """
        Runs the audited RandomForest model as an informational feature.
        Feature order in model: ['semantic_similarity', 'question_length', 'answer_length'].
        Note: The model was fitted with 'semantic_similarity' representing question-to-answer similarity in [0, 1].
        """
        if self.scoring_model is None or not candidate_answer.strip():
            return None

        try:
            features_df = pd.DataFrame([{
                "semantic_similarity": max(0.0, min(1.0, float(question_similarity) / 100.0)),
                "question_length": len(question),
                "answer_length": len(candidate_answer.strip())
            }])
            raw_pred = self.scoring_model.predict(features_df)[0]
            return round(max(0.0, min(100.0, float(raw_pred))), 2)
        except Exception:
            return None

    def _calc_academic_classification(
        self,
        question: str,
        candidate_answer: str,
        sem_sim: float
    ) -> Tuple[Optional[str], Optional[float]]:
        """
        Executes the Part A DecisionTree classifier trained on academic QA features:
        ['semantic_similarity', 'lexical_overlap', 'word_count', 'unique_word_ratio', 'avg_word_length'].
        Predicts: 'Proficient' (1) or 'Needs Improvement' (0) with confidence probability.
        """
        dt = get_academic_classifier()
        if dt is None or not candidate_answer.strip():
            return None, None

        try:
            tokens_q = set(re.findall(r'\b[a-zA-Z]{3,}\b', question.lower()))
            tokens_c = set(re.findall(r'\b[a-zA-Z]{3,}\b', candidate_answer.lower()))
            jaccard = len(tokens_q & tokens_c) / max(1, len(tokens_q | tokens_c))
            cand_words = [w for w in candidate_answer.split() if w.strip()]
            w_cnt = len(cand_words)
            u_ratio = len(set(cand_words)) / max(1, w_cnt)
            avg_len = sum(len(w) for w in cand_words) / max(1, w_cnt)

            features_df = pd.DataFrame([{
                "semantic_similarity": max(0.0, min(1.0, float(sem_sim) / 100.0)),
                "lexical_overlap": max(0.0, min(1.0, float(jaccard))),
                "word_count": w_cnt,
                "unique_word_ratio": max(0.0, min(1.0, float(u_ratio))),
                "avg_word_length": float(avg_len)
            }])
            pred = int(dt.predict(features_df)[0])
            label = "Proficient" if pred == 1 else "Needs Improvement"
            confidence = 1.0
            if hasattr(dt, "predict_proba"):
                probs = dt.predict_proba(features_df)[0]
                confidence = round(float(probs[pred]), 2)
            return label, confidence
        except Exception:
            return None, None

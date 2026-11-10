"""
================================================================================
NATURAL LANGUAGE INFERENCE (NLI) & CONTRADICTION DETECTOR
Part B - Advanced Answer Evaluation & Factual Truth Enforcement
Project: AI Interview Analyzer
Workspace: D:\\AI-Interview-Analyzer
================================================================================

This module implements a hybrid two-tier contradiction filter to detect when
a candidate makes factually contradictory, false, or antipodal statements relative
to the verified reference technical truth:

Tier 1: High-Precision Domain Antonym & Polarity Binding Engine
- Analyzes subject-predicate pairs across canonical CS polarity dimensions (eager/lazy,
  mutable/immutable, sync/async, stateless/stateful, single/multithreaded, etc.).
- Detects direct negation flips (e.g. asserting capability for an action that
  reference standard states is impossible, prevented, or unhandled).
- Evaluates against structured common misconceptions defined in evaluation rubrics.

Tier 2: Neural Natural Language Inference (CrossEncoder)
- Lazy-loaded CrossEncoder model (cross-encoder/nli-distilroberta-base) for deep
  semantic entailment vs. contradiction verification on candidate claim assertions.
- Non-blocking, fails gracefully if CPU is busy or network is offline.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from nlp.answer_analyzer import STOP_WORDS

logger = logging.getLogger(__name__)

# Canonical CS Polarity Antonym Pairs
TECHNICAL_POLARITY_PAIRS: List[Tuple[str, str]] = [
    ("eager", "lazy"),
    ("eagerly", "lazily"),
    ("mutable", "immutable"),
    ("mutability", "immutability"),
    ("synchronous", "asynchronous"),
    ("synchronously", "asynchronously"),
    ("sync", "async"),
    ("blocking", "non-blocking"),
    ("blocking", "nonblocking"),
    ("stateless", "stateful"),
    ("statelessly", "statefully"),
    ("connectionless", "connection-oriented"),
    ("lossless", "lossy"),
    ("single-threaded", "multi-threaded"),
    ("single-threaded", "multithreaded"),
    ("cpu-bound", "i/o-bound"),
    ("compile-time", "runtime"),
    ("static", "dynamic"),
    ("statically", "dynamically"),
    ("strongly typed", "weakly typed"),
    ("horizontal", "vertical"),
    ("horizontally", "vertically"),
    ("pessimistic", "optimistic"),
    ("symmetric", "asymmetric"),
    ("relational", "non-relational"),
    ("monolithic", "distributed"),
    ("monolith", "microservices"),
    ("centralized", "decentralized"),
    ("deterministic", "non-deterministic"),
    ("ordered", "unordered"),
    ("unique", "duplicate"),
    ("thread-safe", "thread-unsafe"),
    ("atomic", "non-atomic"),
    ("lossless", "lossy")
]

# Negation Tokens and Verbs
NEGATION_WORDS: Set[str] = {
    "not", "never", "no", "neither", "nor", "cannot", "can't",
    "doesn't", "doesnt", "don't", "dont", "won't", "wont",
    "isn't", "isnt", "aren't", "arent", "without", "lacks", "fails"
}

CAPABILITY_VERBS: Set[str] = {
    "allows", "enables", "supports", "permits", "provides", "requires",
    "prevents", "restricts", "prohibits", "blocks", "bypasses", "modifies"
}


class ContradictionDetector:
    """
    Hybrid Natural Language Inference and Technical Contradiction Filter.
    """

    def __init__(self, enable_neural_nli: bool = True):
        self.enable_neural_nli = enable_neural_nli
        self._nli_model = None
        self._nli_load_attempted = False

        # Build bidirectional antonym lookup
        self.antonym_map: Dict[str, str] = {}
        for term1, term2 in TECHNICAL_POLARITY_PAIRS:
            self.antonym_map[term1] = term2
            self.antonym_map[term2] = term1

    def _get_nli_model(self):
        """Lazy load CrossEncoder NLI model singleton."""
        if not self.enable_neural_nli:
            return None
        if not self._nli_load_attempted and self._nli_model is None:
            self._nli_load_attempted = True
            try:
                from sentence_transformers import CrossEncoder
                self._nli_model = CrossEncoder("cross-encoder/nli-distilroberta-base")
                logger.info("Neural NLI CrossEncoder model successfully loaded.")
            except Exception as e:
                logger.warning(f"Could not initialize Neural NLI model ({e}). Continuing with deterministic filter.")
                self._nli_model = None
        return self._nli_model

    def detect_contradictions(
        self,
        question: str,
        candidate_answer: str,
        reference_answer: str,
        spec: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes multi-tier contradiction analysis on candidate_answer relative to reference_answer.
        Returns a list of contradiction records with claim, conflict_type, explanation, and confidence.
        """
        if not candidate_answer or not reference_answer:
            return []

        cand_clean = candidate_answer.strip()
        ref_clean = reference_answer.strip()
        q_clean = question.strip() if question else ""

        contradictions: List[Dict[str, Any]] = []
        seen_explanations: Set[str] = set()

        # ----------------------------------------------------------------------
        # Tier 1A: Technical Polarity & Property Inversion
        # ----------------------------------------------------------------------
        polarity_conflicts = self._detect_polarity_inversions(cand_clean, ref_clean)
        for conf in polarity_conflicts:
            expl = conf["explanation"]
            if expl not in seen_explanations:
                contradictions.append(conf)
                seen_explanations.add(expl)

        # ----------------------------------------------------------------------
        # Tier 1B: Technical Capability & Negation Inversion
        # ----------------------------------------------------------------------
        negation_conflicts = self._detect_negation_inversions(cand_clean, ref_clean)
        for conf in negation_conflicts:
            expl = conf["explanation"]
            if expl not in seen_explanations:
                contradictions.append(conf)
                seen_explanations.add(expl)

        # ----------------------------------------------------------------------
        # Tier 1C: Specific Rubric Misconceptions
        # ----------------------------------------------------------------------
        if spec:
            misconceptions = spec.get("common_misconceptions") or []
            cand_lower = cand_clean.lower()
            for misc in misconceptions:
                misc_clean = misc.lower().strip()
                misc_words = [w for w in re.findall(r'\b[a-zA-Z0-9_\-\+]{3,}\b', misc_clean) if w not in NEGATION_WORDS]
                if len(misc_words) >= 3:
                    cand_words_set = set(re.findall(r'\b[a-zA-Z0-9_\-\+]{3,}\b', cand_lower))
                    matched = [w for w in misc_words if w in cand_words_set]
                    if len(matched) >= len(misc_words) - 1:
                        expl = f"Affirmed known technical misconception: {misc}"
                        if expl not in seen_explanations:
                            contradictions.append({
                                "claim": misc,
                                "conflict_type": "rubric_misconception",
                                "explanation": expl,
                                "confidence": 0.95
                            })
                            seen_explanations.add(expl)

        # ----------------------------------------------------------------------
        # Tier 2: Neural NLI CrossEncoder (Deep Semantic Contradiction)
        # ----------------------------------------------------------------------
        nli_model = self._get_nli_model()
        if nli_model is not None:
            neural_conflicts = self._detect_neural_contradictions(nli_model, cand_clean, ref_clean)
            for conf in neural_conflicts:
                expl = conf["explanation"]
                if expl not in seen_explanations:
                    contradictions.append(conf)
                    seen_explanations.add(expl)

        return contradictions

    def _extract_subject_properties(self, text: str) -> Dict[str, List[str]]:
        """
        Parses sentences into subjects and assigned polarity adjectives/adverbs.
        """
        clauses = re.split(r'[,;.\n]|(?:\b(?:whereas|while|but|however|although|instead of)\b)', text, flags=re.IGNORECASE)
        results: Dict[str, List[str]] = {}

        for clause in clauses:
            c_clean = clause.strip().lower()
            if not c_clean:
                continue

            words = re.findall(r'\b[a-zA-Z0-9_\-\+]{2,}\b', c_clean)
            found_polarities = []

            for term1, term2 in TECHNICAL_POLARITY_PAIRS:
                if term1 in words or term1 in c_clean:
                    found_polarities.append(term1)
                if term2 in words or term2 in c_clean:
                    found_polarities.append(term2)

            if found_polarities:
                # Subjects are key technical nouns in the same clause
                ignore_tokens = {
                    "they", "that", "this", "these", "those", "have", "with", "from",
                    "into", "over", "each", "both", "such", "than", "when", "where",
                    "which", "also", "some", "more", "most", "only", "used", "using",
                    "values", "data", "compute", "computes", "process", "processes"
                }
                subjects = [
                    w for w in words
                    if w not in found_polarities
                    and len(w) >= 3
                    and w not in ignore_tokens
                    and w not in STOP_WORDS
                ]

                for subj in subjects:
                    for pol in found_polarities:
                        results.setdefault(subj, []).append(pol)

        return results

    def _detect_polarity_inversions(self, candidate_answer: str, reference_answer: str) -> List[Dict[str, Any]]:
        """
        Detects when a candidate attributes an antipodal property to a subject
        contrary to reference technical truth (e.g. claiming list comprehensions are lazy).
        """
        cand_props = self._extract_subject_properties(candidate_answer)
        ref_props = self._extract_subject_properties(reference_answer)

        conflicts = []
        for subj, c_polarities in cand_props.items():
            if subj in ref_props:
                r_polarities = ref_props[subj]
                for cp in c_polarities:
                    expected_opposite = self.antonym_map.get(cp)
                    if expected_opposite and expected_opposite in r_polarities:
                        conflicts.append({
                            "claim": f"{subj} is {cp}",
                            "conflict_type": "polarity_inversion",
                            "explanation": f"Factual inversion: asserted '{subj}' is {cp}, but technical reference establishes it as {expected_opposite}.",
                            "confidence": 0.95
                        })
        return conflicts

    def _detect_negation_inversions(self, candidate_answer: str, reference_answer: str) -> List[Dict[str, Any]]:
        """
        Detects polarity inversion between positive capability claims and reference prohibitions.
        """
        conflicts = []
        cand_lower = candidate_answer.lower()
        ref_lower = reference_answer.lower()

        # Common critical technical capability conflicts
        critical_inversions = [
            (
                r"\b(bypass(es)?|circumvent(s)?)\b.*?\bgil\b",
                r"\b(prevents?|cannot bypass|does not bypass|restricts?)\b.*?\bgil\b",
                "Asserted native threads bypass the GIL for CPU-bound tasks, which violates Python core runtime architecture."
            ),
            (
                r"\bselect_related\b.*?\b(many[\s\-_]?to[\s\-_]?many|m2m)\b",
                r"\bprefetch_related\b.*?\b(many[\s\-_]?to[\s\-_]?many|m2m)\b",
                "Asserted select_related supports ManyToMany relationships (prefetch_related is required for multi-valued joins)."
            ),
            (
                r"\b(can|allowed to|able to)\b.*?\bmodify\b.*?\bstrings?\b",
                r"\b(immutable|cannot be modified|read[\s\-_]?only)\b.*?\bstrings?\b",
                "Asserted Python strings are mutable and can be modified in place."
            ),
            (
                r"\babstract\s+class(es)?\b.*?\b(can\s+be\s+instantiated|instantiate\s+directly)\b",
                r"\bcannot\s+be\s+instantiated\b",
                "Asserted abstract classes can be instantiated directly."
            ),
            (
                r"\bprimary\s+key(s)?\b.*?\b(can\s+be\s+null|allows?\s+duplicates?)\b",
                r"\b(not\s+null|unique|cannot\s+be\s+null)\b",
                "Asserted primary keys allow NULL or duplicate values."
            )
        ]

        for cand_pat, ref_pat, expl in critical_inversions:
            if re.search(cand_pat, cand_lower) and re.search(ref_pat, ref_lower):
                conflicts.append({
                    "claim": cand_lower[:120],
                    "conflict_type": "negation_inversion",
                    "explanation": expl,
                    "confidence": 0.98
                })

        return conflicts

    def _detect_neural_contradictions(
        self,
        nli_model: Any,
        candidate_answer: str,
        reference_answer: str
    ) -> List[Dict[str, Any]]:
        """
        Uses CrossEncoder to evaluate candidate claims against reference truth.
        """
        conflicts = []
        # Split candidate answer into discrete sentence claims
        sentences = [s.strip() for s in re.split(r'[.!?\n]', candidate_answer) if len(s.strip().split()) >= 4]

        # Only evaluate sentences with technical content to conserve CPU
        if not sentences:
            return []

        pairs = [(reference_answer, s) for s in sentences[:4]]
        try:
            from scipy.special import softmax
            scores = nli_model.predict(pairs)
            for idx, raw_score in enumerate(scores):
                probs = softmax(raw_score)
                # Model labels: 0: contradiction, 1: entailment, 2: neutral
                p_contradiction = float(probs[0])
                p_entailment = float(probs[1])

                # High-confidence neural contradiction: contradiction > 0.70 and contradiction > entailment * 2
                if p_contradiction >= 0.70 and p_contradiction > (p_entailment * 2.0):
                    conflicts.append({
                        "claim": sentences[idx],
                        "conflict_type": "neural_contradiction",
                        "explanation": f"Neural NLI identified claim '{sentences[idx]}' as a direct factual contradiction of technical ground truth (confidence: {round(p_contradiction * 100, 1)}%).",
                        "confidence": round(p_contradiction, 2)
                    })
        except Exception as e:
            logger.debug(f"Neural NLI inference skipped: {e}")

        return conflicts


# Global Singleton Instance
contradiction_detector = ContradictionDetector()


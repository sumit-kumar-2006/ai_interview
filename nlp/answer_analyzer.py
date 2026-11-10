import re
from typing import List, Dict, Any, Set, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Global lazy-loaded embedding model instance
_EMBEDDING_MODEL = None

def get_embedding_model():
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _EMBEDDING_MODEL = None
    return _EMBEDDING_MODEL


STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "eg", "ie", "etc", "also", "using", "used", "use"
}


def normalize_word(word: str) -> str:
    """
    Lightweight deterministic stemming/normalization for concept matching.
    """
    w = word.lower().strip()
    w = re.sub(r'^[^\w]+|[^\w]+$', '', w)
    if len(w) > 4 and w.endswith("es"):
        w = w[:-2]
    elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]
    elif len(w) > 4 and w.endswith("ing"):
        w = w[:-3]
    elif len(w) > 4 and w.endswith("ed"):
        w = w[:-2]
    return w


def extract_key_concepts(text: str) -> List[str]:
    """
    Extracts key technical terms and concepts from reference text ignoring stop words.
    """
    if not text or not text.strip():
        return []
    
    clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = [w.strip() for w in clean_text.split() if w.strip()]

    concepts: List[str] = []
    seen = set()

    # Extract meaningful key single terms (length >= 3 and not stop word)
    for w in words:
        norm_w = normalize_word(w)
        if len(norm_w) >= 3 and norm_w not in STOP_WORDS and norm_w not in seen:
            concepts.append(norm_w)
            seen.add(norm_w)

    return concepts


def analyze_answer(
    question: str,
    candidate_answer: str,
    reference_answer: str,
    model: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Analyzes candidate_answer against question and reference_answer using deterministic NLP logic.
    Returns structured JSON/dict without fake/random numbers or NaN.
    """
    cand_text = candidate_answer.strip() if candidate_answer else ""
    ref_text = reference_answer.strip() if reference_answer else ""
    q_text = question.strip() if question else ""

    # 1. Edge Case: Empty Answer
    if not cand_text:
        return {
            "status": "no_answer",
            "relevance_score": 0.0,
            "semantic_similarity": 0.0,
            "concept_coverage": 0.0,
            "completeness": 0.0,
            "answer_length": {"char_count": 0, "word_count": 0},
            "key_concepts_matched": [],
            "key_concepts_missing": extract_key_concepts(ref_text),
            "strengths": [],
            "areas_for_improvement": ["No answer provided."],
            "ai_feedback": "No answer detected. Please record or type a substantive response."
        }

    cand_words = [w for w in cand_text.split() if w.strip()]
    word_count = len(cand_words)
    char_count = len(cand_text)

    # 2. Edge Case: "I don't know" or brief non-committal answers
    idk_patterns = [r"\bi\s+don'?t\s+know\b", r"\bno\s+idea\b", r"\bnot\s+sure\b", r"\bi\s+have\s+no\s+clue\b"]
    is_idk = any(re.search(pat, cand_text, re.IGNORECASE) for pat in idk_patterns) and word_count <= 8

    if is_idk:
        ref_concepts = extract_key_concepts(ref_text)
        return {
            "status": "honest_no_answer",
            "relevance_score": 0.0,
            "semantic_similarity": 0.0,
            "concept_coverage": 0.0,
            "completeness": 0.0,
            "answer_length": {"char_count": char_count, "word_count": word_count},
            "key_concepts_matched": [],
            "key_concepts_missing": ref_concepts,
            "strengths": ["Honest acknowledgment of topic unfamiliarity."],
            "areas_for_improvement": ["Missing required technical concepts and explanation."],
            "ai_feedback": "You indicated that you don't know the answer. Review the reference material to build conceptual knowledge."
        }

    # 3. Compute Embeddings & Semantic Similarity / Relevance
    embedder = model if model is not None else get_embedding_model()

    if embedder is not None:
        try:
            cand_emb = embedder.encode([cand_text])
            ref_emb = embedder.encode([ref_text]) if ref_text else cand_emb
            q_emb = embedder.encode([q_text]) if q_text else cand_emb

            ref_sim = float(cosine_similarity(ref_emb, cand_emb)[0][0])
            q_sim = float(cosine_similarity(q_emb, cand_emb)[0][0])

            relevance_raw = max(0.0, q_sim) * 100.0
            semantic_sim_raw = max(0.0, ref_sim) * 100.0
        except Exception:
            relevance_raw = 0.0
            semantic_sim_raw = 0.0
    else:
        # Fallback lexical overlap if model is absent
        ref_w_set = set(normalize_word(w) for w in ref_text.lower().split() if w not in STOP_WORDS)
        q_w_set = set(normalize_word(w) for w in q_text.lower().split() if w not in STOP_WORDS)
        cand_w_set = set(normalize_word(w) for w in cand_words)

        relevance_raw = (len(cand_w_set & q_w_set) / max(1, len(q_w_set))) * 100.0
        semantic_sim_raw = (len(cand_w_set & ref_w_set) / max(1, len(ref_w_set))) * 100.0

    relevance_score = round(max(0.0, min(100.0, relevance_raw)), 2)
    semantic_similarity = round(max(0.0, min(100.0, semantic_sim_raw)), 2)

    # 4. Concept Coverage Analysis
    ref_concepts = extract_key_concepts(ref_text)
    cand_norm_words = set(normalize_word(w) for w in cand_words)

    matched_concepts: List[str] = []
    missing_concepts: List[str] = []

    if ref_concepts:
        for concept in ref_concepts:
            if concept in cand_norm_words:
                matched_concepts.append(concept)
            else:
                missing_concepts.append(concept)

        concept_coverage = round((len(matched_concepts) / len(ref_concepts)) * 100.0, 2)
    else:
        concept_coverage = 100.0

    # 5. Completeness Analysis
    ref_word_count = max(1, len(ref_text.split()))
    length_ratio = min(1.0, word_count / ref_word_count)
    raw_completeness = (0.6 * concept_coverage) + (0.4 * (length_ratio * 100.0))

    # Cap completeness if relevance is low (< 35%) to avoid rewarding long off-topic rambles
    if relevance_score < 35.0:
        raw_completeness = min(raw_completeness, relevance_score)

    completeness = round(max(0.0, min(100.0, raw_completeness)), 2)

    # 6. Generate Evidence-Based Strengths
    strengths: List[str] = []
    if relevance_score >= 70.0:
        strengths.append("Directly addresses the core topic of the question.")
    if semantic_similarity >= 75.0:
        strengths.append("High semantic alignment with the reference answer.")
    if concept_coverage >= 60.0:
        strengths.append(f"Successfully covered major key concepts ({len(matched_concepts)}/{len(ref_concepts)} terms).")
    elif matched_concepts:
        strengths.append(f"Mentioned key terms: {', '.join(matched_concepts[:3])}.")
    if completeness >= 70.0:
        strengths.append("Provides a thorough and complete explanation.")
    elif word_count <= 25 and relevance_score >= 65.0:
        strengths.append("Concise response focused on the core question.")

    # 7. Generate Evidence-Based Areas for Improvement
    areas_for_improvement: List[str] = []
    if concept_coverage < 60.0 and missing_concepts:
        areas_for_improvement.append(f"Missing key concepts: {', '.join(missing_concepts[:4])}.")
    if relevance_score < 50.0:
        areas_for_improvement.append("Low relevance score; answer may be partially off-topic.")
    if completeness < 50.0:
        areas_for_improvement.append("Answer lacks detail compared to expected technical depth.")
    if word_count > 150 and concept_coverage < 40.0:
        areas_for_improvement.append("Response is verbose but lacks essential technical concepts.")

    # 8. Generate Explainable AI Feedback
    if relevance_score >= 75.0 and concept_coverage >= 60.0:
        ai_feedback = f"Great answer! You directly addressed the question and covered core concepts ({', '.join(matched_concepts[:3])})."
    elif relevance_score >= 50.0:
        if missing_concepts:
            ai_feedback = f"Good response. To improve, try incorporating specific details about: {', '.join(missing_concepts[:3])}."
        else:
            ai_feedback = "Good response. Try elaborating further with concrete examples to increase completeness."
    else:
        if missing_concepts:
            ai_feedback = f"Your answer missed key concepts such as {', '.join(missing_concepts[:3])}. Focus directly on answering the core question."
        else:
            ai_feedback = "Your response had low relevance to the question. Review the question requirements and core concepts."

    return {
        "status": "success",
        "relevance_score": relevance_score,
        "semantic_similarity": semantic_similarity,
        "concept_coverage": concept_coverage,
        "completeness": completeness,
        "answer_length": {"char_count": char_count, "word_count": word_count},
        "key_concepts_matched": matched_concepts,
        "key_concepts_missing": missing_concepts,
        "strengths": strengths,
        "areas_for_improvement": areas_for_improvement,
        "ai_feedback": ai_feedback
    }


class AnswerAnalyzer:
    """
    Class wrapper around analyze_answer function for OOP integration.
    """
    def __init__(self, embedding_model=None):
        self.embedding_model = embedding_model if embedding_model is not None else get_embedding_model()

    def analyze(self, question: str, candidate_answer: str, reference_answer: str) -> Dict[str, Any]:
        return analyze_answer(question, candidate_answer, reference_answer, model=self.embedding_model)

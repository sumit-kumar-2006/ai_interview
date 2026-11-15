"""
================================================================================
MULTI-CRITERIA RUBRIC UTILITIES FOR INTERVIEW SCORING
================================================================================
Defines standardized multi-criteria rubric dimensions:
1. Semantic Similarity / Technical Correctness: Dense embedding cosine similarity
2. Concept Coverage: Recall of essential technical question concepts in answer
3. Technical Depth: Substantive depth, lexical richness, explanation structure
4. Keyword Alignment: Precision of technical keywords between question & answer
================================================================================
"""

import re
from typing import Set, Dict, Any

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
    "yourself", "yourselves", "tell", "explain", "describe", "discuss", "give"
}

TECHNICAL_INDICATORS: Set[str] = {
    "because", "specifically", "implements", "inherits", "architecture",
    "concurrency", "performance", "complexity", "protocol", "mechanism",
    "structure", "algorithm", "database", "distributed", "interface",
    "synchronous", "asynchronous", "thread", "memory", "latency", "throughput",
    "scalability", "overhead", "tradeoff", "optimization", "example"
}


def normalize_token(token: str) -> str:
    """Normalize word token by stripping punctuation and common inflection suffixes."""
    w = token.lower().strip()
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


def extract_concepts(text: str) -> Set[str]:
    """Extract substantive normalized concept tokens from text, filtering stopwords."""
    if not isinstance(text, str) or not text.strip():
        return set()
    clean = re.sub(r'[^\w\s]', ' ', text.lower())
    words = [normalize_token(w) for w in clean.split() if w.strip()]
    return {w for w in words if len(w) >= 3 and w not in STOP_WORDS}


def compute_concept_coverage(question: str, answer: str) -> float:
    """
    Computes percentage (0 to 100) of question concepts recalled in the candidate answer.
    """
    q_concepts = extract_concepts(question)
    a_concepts = extract_concepts(answer)
    if not q_concepts:
        return 75.0
    matched = len(q_concepts & a_concepts)
    coverage = matched / len(q_concepts)
    return round(float(min(1.0, max(0.0, coverage))) * 100.0, 2)


def compute_keyword_alignment(question: str, answer: str) -> float:
    """
    Computes keyword precision percentage (0 to 100) between question & answer.
    """
    q_concepts = extract_concepts(question)
    a_concepts = extract_concepts(answer)
    if not q_concepts:
        return 50.0
    matched = len(q_concepts & a_concepts)
    precision = matched / len(q_concepts)
    return round(float(min(1.0, max(0.0, precision))) * 100.0, 2)


def compute_technical_depth(answer: str) -> float:
    """
    Evaluates technical depth percentage (0 to 100) based on:
    - Substantive length / word count (optimal technical elaboration range)
    - Lexical diversity (unique content word ratio)
    - Presence of technical indicator/justification markers
    """
    if not isinstance(answer, str) or not answer.strip():
        return 0.0
    
    words = [w.lower().strip() for w in re.sub(r'[^\w\s]', ' ', answer).split() if w.strip()]
    word_count = len(words)
    if word_count == 0:
        return 0.0
    
    # 1. Length factor (smooth saturation up to 25 words)
    length_factor = min(1.0, word_count / 20.0)
    if word_count < 5:
        length_factor *= 0.3
    
    # 2. Lexical diversity
    content_words = [w for w in words if w not in STOP_WORDS]
    diversity = (len(set(content_words)) / max(1, len(content_words))) if content_words else 0.5
    
    # 3. Technical indicator density
    tech_hits = sum(1 for w in words if w in TECHNICAL_INDICATORS)
    tech_factor = min(1.0, tech_hits / 2.0)
    
    depth = (length_factor * 0.50) + (diversity * 0.35) + (tech_factor * 0.15)
    return round(float(min(1.0, max(0.0, depth))) * 100.0, 2)


def compute_rubric_target_score(
    semantic_similarity: float,
    concept_coverage: float,
    keyword_alignment: float,
    technical_depth: float,
    answer_length: int
) -> float:
    """
    Multi-criteria rubric scoring function:
    - Semantic Similarity (60% weight for accurate technical alignment)
    - Concept Coverage (20% weight)
    - Technical Depth (10% weight)
    - Keyword Alignment (10% weight)
    Includes boosts for high-accuracy answers and guards for empty/irrelevant answers.
    """
    if answer_length < 10 or semantic_similarity <= 0.15:
        return 0.0
    
    sem_score = max(0.0, min(1.0, float(semantic_similarity))) * 100.0
    cov_score = max(0.0, min(100.0, float(concept_coverage)))
    depth_score = max(0.0, min(100.0, float(technical_depth)))
    align_score = max(0.0, min(100.0, float(keyword_alignment)))
    
    composite = (
        (sem_score * 0.60) +
        (cov_score * 0.20) +
        (depth_score * 0.10) +
        (align_score * 0.10)
    )
    
    # High-accuracy boost for expert answers (matching reference)
    if semantic_similarity >= 0.80:
        base_boost = sem_score * 0.85
        composite = max(composite, base_boost + (depth_score * 0.15))
        
    return round(float(min(100.0, max(0.0, composite))), 2)


def extract_all_rubric_features(question: str, answer: str, semantic_similarity: float) -> Dict[str, Any]:
    """
    Extracts complete dictionary of features for training and inference.
    """
    q_len = len(question) if isinstance(question, str) else 0
    a_len = len(answer.strip()) if isinstance(answer, str) else 0
    
    cov = compute_concept_coverage(question, answer)
    align = compute_keyword_alignment(question, answer)
    depth = compute_technical_depth(answer)
    target = compute_rubric_target_score(semantic_similarity, cov, align, depth, a_len)
    
    return {
        "semantic_similarity": float(semantic_similarity),
        "question_length": int(q_len),
        "answer_length": int(a_len),
        "concept_coverage": float(cov),
        "keyword_alignment": float(align),
        "technical_depth": float(depth),
        "target_score": float(target)
    }

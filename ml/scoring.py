def calculate_score(
    semantic_similarity,
    word_count,
    sentence_count,
    unique_word_ratio,
    filler_ratio
):
    # Semantic score: 50%
    semantic_score = semantic_similarity * 100

    # Basic answer-length score
    if word_count >= 50:
        length_score = 100
    elif word_count >= 30:
        length_score = 80
    elif word_count >= 15:
        length_score = 60
    else:
        length_score = 40

    # Sentence structure score
    if sentence_count >= 4:
        structure_score = 100
    elif sentence_count >= 2:
        structure_score = 80
    else:
        structure_score = 60

    # Vocabulary diversity
    vocabulary_score = min(unique_word_ratio * 150, 100)

    # Filler score
    filler_score = max(100 - (filler_ratio * 500), 0)

    final_score = (
        semantic_score * 0.50
        + vocabulary_score * 0.20
        + structure_score * 0.15
        + filler_score * 0.15
    )

    return round(final_score, 2)


if __name__ == "__main__":

    score = calculate_score(
        semantic_similarity=0.7745,
        word_count=45,
        sentence_count=3,
        unique_word_ratio=0.65,
        filler_ratio=0.02
    )

    print("==============================")
    print("Interview Answer Score:", score)
    print("==============================")
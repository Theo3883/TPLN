"""Shrinkage aggregation for robust scoring with confidence measure."""

PRIOR_SCORE = 3.0
SHRINKAGE_K = 5.0


def compute_score(review_ratings: list[float], prior: float = PRIOR_SCORE, k: float = SHRINKAGE_K) -> tuple[float, float]:
    """
    Bayesian shrinkage: score = (n * avg + k * prior) / (n + k).
    Confidence is inverse of variance proxy: higher when more reviews.
    """
    n = len(review_ratings)
    if n == 0:
        return prior, 0.0

    avg = sum(review_ratings) / n
    shrunk_score = (n * avg + k * prior) / (n + k)
    confidence = min(1.0, n / (n + k))
    return round(shrunk_score, 2), round(confidence, 4)

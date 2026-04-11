import re
from typing import List


def _normalise(text: str) -> str:
    """Lowercase and strip punctuation/whitespace for loose comparison."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def compute_disagreement(outputs: List[str]) -> dict:
    """
    Given a list of model outputs for the same row, determine whether they
    disagree.  Returns a dict compatible with the DisagreementScore schema.

    Score = fraction of unique-pairs that disagree (0.0 = full agreement,
    1.0 = all pairs disagree).
    """
    if len(outputs) < 2:
        return {"has_disagreement": False, "score": 0.0}

    normalised = [_normalise(o) for o in outputs]

    total_pairs = 0
    disagreeing_pairs = 0
    for i in range(len(normalised)):
        for j in range(i + 1, len(normalised)):
            total_pairs += 1
            if normalised[i] != normalised[j]:
                disagreeing_pairs += 1

    score = disagreeing_pairs / total_pairs if total_pairs else 0.0
    return {"has_disagreement": disagreeing_pairs > 0, "score": round(score, 3)}

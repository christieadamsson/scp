"""Dispatch rule extracted from solution.py without changing its selection logic.

IMPORTANT: The current algorithm sorts (cost/newly-covered, subset index).
It does not use the team's previously proposed uncovered-count tie-break.
"""

def select_next_set(selected, costs, subsets, uncovered, rng=None):
    candidates = []
    for j, elements in enumerate(subsets):
        if j in selected:
            continue
        newly_covered = len(elements & uncovered)
        if newly_covered > 0:
            score = costs[j] / newly_covered
            candidates.append((score, j))
    if not candidates:
        raise ValueError("It is impossible to cover all elements.")
    candidates.sort()
    if rng is None:
        return candidates[0][1]
    return rng.choice(candidates[:3])[1]

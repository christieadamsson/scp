"""Cost evaluation and coverage counts (copied from solution.py)."""

def calculate_cost(selected, costs):
    """
    Add the costs of all selected sets.

    Example:
        selected = {0, 2}
        costs = [4, 3, 6]

        Total cost = costs[0] + costs[2] = 10.

    'selected' contains set indices, not covered elements.
    """

    return sum(costs[j] for j in selected)

def count_coverage(selected, subsets, m):
    """
    Count how many selected sets cover each element.

    Example:
        coverage = [1, 2, 0]

    Interpretation:
        Element 1 is covered once.
        Element 2 is covered twice.
        Element 3 is uncovered.

    A feasible solution requires every count to be at least 1.
    """

    coverage = [0] * m

    for j in selected:
        for element in subsets[j]:
            coverage[element] += 1

    return coverage

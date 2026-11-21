"""Greedy construction/repair and redundant-set removal."""
from dispatch_rule import select_next_set
from solution_utils import count_coverage

def repair(selected, costs, subsets, m, rng=None):
    """
    Add sets until every element is covered.

    This function has two purposes:

    1. Initial construction:
       Starting with no selected sets, build a full cover.

    2. Repair:
       After some sets have been removed, restore full coverage.

    Candidate score:
        set cost / number of newly covered elements

    A lower score is better.

    If rng is None:
        Choose the candidate with the lowest score.

    If rng is provided:
        Choose randomly among the three best candidates.
        This introduces variety during VNS.
    """

    # Work on a copy so the original solution is not changed.
    selected = set(selected)

    coverage = count_coverage(selected, subsets, m)

    uncovered = {
        i for i in range(m)
        if coverage[i] == 0
    }

    while uncovered:

        chosen_set = select_next_set(
            selected, costs, subsets, uncovered, rng
        )

        selected.add(chosen_set)

        # Remove newly covered elements from the uncovered group.
        uncovered.difference_update(subsets[chosen_set])

    return selected

def remove_redundant(selected, costs, subsets, m):
    """
    Remove selected sets that are unnecessary.

    A set can be removed if every element it covers is
    also covered by at least one other selected set.

    Before removing that set, all its elements must therefore
    have coverage counts of at least 2.

    Expensive sets are checked first.
    """

    selected = set(selected)
    coverage = count_coverage(selected, subsets, m)

    order = sorted(
        selected,
        key=lambda j: (-costs[j], j)
    )

    for j in order:

        can_remove = all(
            coverage[element] >= 2
            for element in subsets[j]
        )

        if can_remove:

            selected.remove(j)

            # Update the counts immediately.
            # Later removal decisions must use current counts.
            for element in subsets[j]:
                coverage[element] -= 1

    return selected

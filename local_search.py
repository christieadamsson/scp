"""Deterministic remove-one / greedy-repair local search."""
import time
from constructive import repair, remove_redundant
from solution_utils import calculate_cost

def local_search(selected, costs, subsets, m, deadline):
    """
    Try to improve a solution by removing one selected set
    and rebuilding the missing coverage.

    For each selected set:
        1. Remove it temporarily.
        2. Repair coverage using the greedy rule.
        3. Remove redundant sets.
        4. Accept the candidate only if it is cheaper.

    After an improvement, restart the search.

    Stop when:
        - a complete pass finds no improvement, or
        - the time limit is reached.

    This checks a specific remove-one-and-repair procedure.
    It does not examine every possible solution.
    """

    current = set(selected)

    while time.perf_counter() < deadline:

        improvement_found = False
        current_cost = calculate_cost(current, costs)

        order = sorted(
            current,
            key=lambda j: (-costs[j], j)
        )

        for j in order:

            if time.perf_counter() >= deadline:
                return current

            # Create a trial solution without set j.
            candidate = current - {j}

            # Restore full coverage.
            candidate = repair(
                candidate, costs, subsets, m
            )

            # Remove any unnecessary sets.
            candidate = remove_redundant(
                candidate, costs, subsets, m
            )

            candidate_cost = calculate_cost(candidate, costs)

            if candidate_cost < current_cost:

                current = candidate
                improvement_found = True

                # Restart with the improved solution.
                break

        if not improvement_found:
            break

    return current

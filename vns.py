"""Variable Neighborhood Search orchestration."""
import random
import time
from config import TIME_LIMIT, K_MAX, SEED
from constructive import repair, remove_redundant
from local_search import local_search
from solution_utils import calculate_cost

def solve_vns(m, costs, subsets):
    """
    Run the main optimization procedure.

    Initial stage:
        Greedy construction -> remove redundancy -> local search.

    VNS stage:
        1. Remove k randomly selected sets: shaking.
        2. Repair coverage using randomized choices.
        3. Remove redundancy.
        4. Apply local search.
        5. Accept only a strictly cheaper solution.

    Neighborhood change:
        Improvement -> reset k to 1.
        No improvement -> increase k.
        Beyond K_MAX -> start another cycle with k = 1.

    'best' always stores the lowest-cost accepted solution.
    """

    if TIME_LIMIT <= 0:
        raise ValueError(
            "TIME_LIMIT must be positive."
        )

    if not isinstance(K_MAX, int) or K_MAX < 1:
        raise ValueError(
            "K_MAX must be a positive integer."
        )

    rng = random.Random(SEED)

    start = time.perf_counter()
    deadline = start + TIME_LIMIT

    # Start from an empty selection and construct a cover.
    initial = repair(
        set(), costs, subsets, m
    )

    initial = remove_redundant(
        initial, costs, subsets, m
    )

    initial_cost = calculate_cost(initial, costs)

    print(f"Initial greedy cost: {initial_cost}")

    # Store improvements for the final report.
    history = [
        (time.perf_counter() - start, initial_cost)
    ]

    best = local_search(
        initial, costs, subsets, m, deadline
    )

    best_cost = calculate_cost(best, costs)

    if best_cost < initial_cost:

        history.append(
            (time.perf_counter() - start, best_cost)
        )

        print(f"After initial local search: {best_cost}")

    k = 1
    iterations = 0

    while time.perf_counter() < deadline:

        # SHAKING:
        # Randomly remove k selected sets.
        # Never remove more than the solution contains.
        number_to_remove = min(k, len(best))

        removed = rng.sample(
            sorted(best),
            number_to_remove
        )

        candidate = best - set(removed)

        # REPAIR:
        # Rebuild coverage using randomized candidate selection.
        candidate = repair(
            candidate, costs, subsets, m, rng
        )

        # CLEAN UP:
        # Remove unnecessary selected sets.
        candidate = remove_redundant(
            candidate, costs, subsets, m
        )

        # LOCAL IMPROVEMENT:
        candidate = local_search(
            candidate, costs, subsets, m, deadline
        )

        iterations += 1

        candidate_cost = calculate_cost(candidate, costs)

        # ACCEPTANCE:
        # Keep the candidate only if it improves the cost.
        if candidate_cost < best_cost:

            best = candidate
            best_cost = candidate_cost

            elapsed = time.perf_counter() - start
            history.append((elapsed, best_cost))

            print(
                f"Improvement: cost = {best_cost}, "
                f"time = {elapsed:.2f} s"
            )

            # Return to the smallest shaking size.
            k = 1

        else:

            # Try a stronger shaking operation next.
            k += 1

            if k > K_MAX:
                k = 1

    elapsed_time = time.perf_counter() - start

    return (
        best,
        initial_cost,
        elapsed_time,
        iterations,
        history
    )

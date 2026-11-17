"""
SET COVERING PROBLEM — VARIABLE NEIGHBORHOOD SEARCH (VNS)
========================================================

HOW TO USE THIS SCRIPT IN SPYDER
-------------------------------
1. Change INPUT_FILE and OUTPUT_FILE below.
2. Save this script as, for example, scp_project.py.
3. Press F5 or click Run.
4. Wait approximately TIME_LIMIT seconds.
5. Open the output TXT file to see the answer.

WHAT THE PROGRAM DOES
---------------------
1. Reads the SCP instance from a TXT file.
2. Builds an initial solution using a greedy rule.
3. Removes unnecessary selected sets.
4. Improves the solution using local search.
5. Runs Variable Neighborhood Search.
6. Checks that every element is covered.
7. Saves the answer to a new TXT file.

IMPORTANT
----------
The algorithm searches for a low-cost feasible solution.
It does not prove that the solution is globally optimal.
"""


from pathlib import Path
import random
import time


# %% 1. SETTINGS — CHANGE YOUR FILE PATHS HERE
# ============================================================

# INPUT_FILE must point to your existing SCP data file.
# Replace this example with your own path.

INPUT_FILE = r"intances\scp42.txt"


# OUTPUT_FILE specifies where the answer will be saved.

OUTPUT_FILE = r"C:\Users\guill\Documents\FEUP\Projeto em gestao de operation\Part2\SCP_py\solution42.txt"


# Approximate solving time in seconds.
# This includes initial construction and the VNS search.
# Reading the input and writing the output are not included.

TIME_LIMIT = 30


# Maximum shaking size.
# For example, K_MAX = 5 means the algorithm can remove
# up to five selected sets before repairing the solution.

K_MAX = 5


# Random seed.
# The seed controls random choices.
# With a time-based stopping condition, final results can
# still differ because different runs may finish different
# numbers of iterations.

SEED = 42


# %% 2. READ THE INPUT FILE
# ============================================================

def read_instance(file_path):
    """
    Read an SCP instance in the expected OR-Library-style format.

    File structure:
        m n
        n set costs
        for each of the m elements:
            number of sets covering that element
            IDs of those sets

    Returns:
        m:
            Number of elements to cover.

        n:
            Number of available sets.

        costs[j]:
            Cost of selecting set j.

        subsets[j]:
            Python set containing the elements covered by set j.

    Internal numbering starts at 0.
    Input and output set IDs start at 1.
    """

    # Read the file as text, split it at whitespace,
    # and convert all entries to integers.
    #
    # This works even when a list continues on another line.

    numbers = list(
        map(int, Path(file_path).read_text().split())
    )

    if len(numbers) < 2:
        raise ValueError(
            "The input file does not contain a valid header."
        )

    # The first two numbers specify the problem size.
    m, n = numbers[0], numbers[1]

    if m <= 0 or n <= 0:
        raise ValueError(
            "The numbers of elements and sets must be positive."
        )

    if len(numbers) < 2 + n:
        raise ValueError(
            "The input file does not contain all set costs."
        )

    # The next n numbers are the costs of the available sets.
    costs = numbers[2:2 + n]

    if any(cost <= 0 for cost in costs):
        raise ValueError(
            "All set costs must be positive."
        )

    # Create an empty coverage collection for every set.
    #
    # Example:
    # subsets[0] = {0, 2}
    #
    # This means Set 1 covers Elements 1 and 3.
    subsets = [set() for _ in range(n)]

    # Position of the next unread number.
    position = 2 + n

    # Read coverage information for each element.
    for element in range(m):

        if position >= len(numbers):
            raise ValueError(
                f"Missing coverage information for element {element + 1}."
            )

        number_of_sets = numbers[position]
        position += 1

        if number_of_sets <= 0:
            raise ValueError(
                f"Element {element + 1} has no covering sets."
            )

        if position + number_of_sets > len(numbers):
            raise ValueError(
                f"Incomplete coverage list for element {element + 1}."
            )

        covering_set_ids = numbers[
            position:position + number_of_sets
        ]

        for set_id in covering_set_ids:

            if not 1 <= set_id <= n:
                raise ValueError(
                    f"Set ID {set_id} is outside the valid range 1 to {n}."
                )

            # Convert from file numbering to Python numbering.
            #
            # File Set 1 -> Python index 0.
            # File Element 1 -> Python index 0.
            subsets[set_id - 1].add(element)

        position += number_of_sets

    if position != len(numbers):
        raise ValueError(
            "Unexpected extra data at the end of the input file."
        )

    return m, n, costs, subsets


# %% 3. CALCULATE THE COST OF A SOLUTION
# ============================================================

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


# %% 4. COUNT COVERAGE
# ============================================================

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


# %% 5. BUILD OR REPAIR A SOLUTION
# ============================================================

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

        candidates = []

        for j, elements in enumerate(subsets):

            if j in selected:
                continue

            # '&' means intersection.
            #
            # We count only currently uncovered elements
            # that this set would cover.
            newly_covered = len(elements & uncovered)

            # Ignore sets that do not add any new coverage.
            if newly_covered > 0:

                score = costs[j] / newly_covered
                candidates.append((score, j))

        if not candidates:
            raise ValueError(
                "It is impossible to cover all elements."
            )

        # Sort by score, then by set index to resolve ties.
        candidates.sort()

        if rng is None:
            chosen_set = candidates[0][1]
        else:
            chosen_set = rng.choice(candidates[:3])[1]

        selected.add(chosen_set)

        # Remove newly covered elements from the uncovered group.
        uncovered.difference_update(subsets[chosen_set])

    return selected


# %% 6. REMOVE REDUNDANT SETS
# ============================================================

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


# %% 7. LOCAL SEARCH
# ============================================================

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


# %% 8. VARIABLE NEIGHBORHOOD SEARCH
# ============================================================

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


# %% 9. RUN THE SOLVER AND SAVE THE OUTPUT
# ============================================================

def main():
    """
    Connect all parts of the program.

    Read data -> solve -> verify -> save the answer.
    """

    input_path = Path(INPUT_FILE).expanduser()
    output_path = Path(OUTPUT_FILE).expanduser()

    # Prevent accidental overwriting of the input data.
    if input_path.resolve() == output_path.resolve():
        raise ValueError(
            "INPUT_FILE and OUTPUT_FILE must be different."
        )

    if not input_path.is_file():
        raise FileNotFoundError(
            "Input file not found.\n"
            "Check INPUT_FILE at the top of this script.\n"
            f"Current path: {input_path}"
        )

    print("=" * 60)
    print("SET COVERING PROBLEM — VNS")
    print("=" * 60)

    print("\nReading:", input_path)

    m, n, costs, subsets = read_instance(input_path)

    print(f"Elements to cover: {m}")
    print(f"Available sets: {n}")
    print(f"Approximate time limit: {TIME_LIMIT} seconds")
    print(f"Maximum shaking size: {K_MAX}")
    print(f"Random seed: {SEED}")
    print("\nStarting optimization...\n")

    (
        selected,
        initial_cost,
        elapsed_time,
        iterations,
        history
    ) = solve_vns(m, costs, subsets)

    # Independently verify the final coverage.
    coverage = count_coverage(selected, subsets, m)

    covered_count = sum(
        count > 0 for count in coverage
    )

    uncovered_ids = [
        i + 1 for i, count in enumerate(coverage)
        if count == 0
    ]

    feasible = covered_count == m

    if not feasible:
        raise RuntimeError(
            "The final solution is not feasible.\n"
            f"Uncovered elements: {uncovered_ids}"
        )

    final_cost = calculate_cost(selected, costs)

    # Convert internal indices to IDs used in the input file.
    selected_ids = [
        j + 1 for j in sorted(selected)
    ]

    # Alternative representation of the same solution.
    binary_solution = [
        1 if j in selected else 0
        for j in range(n)
    ]

    cost_reduction = initial_cost - final_cost

    # This compares VNS with the initial greedy solution.
    # It is NOT a gap to the optimum or best-known solution.
    reduction_percent = (
        100 * cost_reduction / initial_cost
    )

    report = [
        "SET COVERING PROBLEM — RESULTS",
        "=" * 60,
        "Method: Variable Neighborhood Search (VNS)",
        "",
        "INSTANCE",
        f"Input file: {input_path}",
        f"Number of elements: {m}",
        f"Number of available sets: {n}",
        "",
        "PARAMETERS",
        f"Approximate time limit: {TIME_LIMIT} seconds",
        f"Maximum shaking size: {K_MAX}",
        f"Random seed: {SEED}",
        "",
        "RESULTS",
        f"Initial cost (greedy with redundancy removal): {initial_cost}",
        f"Final cost (VNS): {final_cost}",
        f"Cost reduction: {cost_reduction}",
        f"Reduction relative to greedy: {reduction_percent:.2f}%",
        f"Number of selected sets: {len(selected)}",
        f"Covered elements: {covered_count}/{m}",
        f"Full coverage: {'YES' if feasible else 'NO'}",
        f"Elapsed solving time: {elapsed_time:.3f} seconds",
        f"VNS iterations: {iterations}",
        "",
        "SELECTED SET IDs",
        "Numbering starts at 1, as in the input file.",
        " ".join(map(str, selected_ids)),
        "",
        "SELECTED SETS AND THEIR COSTS",
    ]

    for j in sorted(selected):
        report.append(
            f"Set {j + 1}: cost {costs[j]}"
        )

    report.extend([
        "",
        "BINARY SOLUTION",
        "Entry 1 corresponds to Set 1, entry 2 to Set 2, etc.",
        "1 = selected; 0 = not selected.",
        " ".join(map(str, binary_solution)),
        "",
        "COVERAGE COUNTS",
        "How many selected sets cover each element:",
    ])

    for element, count in enumerate(coverage, start=1):
        report.append(
            f"Element {element}: {count}"
        )

    report.extend([
        "",
        "IMPROVEMENT HISTORY",
        "Time in seconds | Best accepted cost",
    ])

    for elapsed, cost in history:
        report.append(
            f"{elapsed:.3f} | {cost}"
        )

    report.extend([
        "",
        "INTERPRETATION",
        "Every element must have a coverage count of at least 1.",
        "Covering an element more than once is allowed.",
        "The objective is to minimize total selected-set cost.",
        "The result is heuristic; global optimality is not proven.",
        "The percentage reduction compares VNS with greedy,",
        "not with an optimal or best-known reference value.",
    ])

    # Create the output directory if necessary.
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save the complete report.
    output_path.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("FINISHED")
    print("=" * 60)

    print(f"Initial greedy cost: {initial_cost}")
    print(f"Final VNS cost: {final_cost}")
    print(f"Cost reduction: {cost_reduction}")
    print(f"Reduction relative to greedy: {reduction_percent:.2f}%")
    print(f"Selected sets: {len(selected)}")
    print(f"Covered elements: {covered_count}/{m}")
    print(f"Full coverage: {'YES' if feasible else 'NO'}")
    print(f"Elapsed time: {elapsed_time:.3f} seconds")
    print(f"VNS iterations: {iterations}")

    print("\nSelected set IDs:")
    print(selected_ids)

    print("\nAnswer saved to:")
    print(output_path.resolve())

    # Returning these values also makes them available
    # through the 'results' variable in Spyder.
    return {
        "initial_cost": initial_cost,
        "final_cost": final_cost,
        "selected_set_ids": selected_ids,
        "binary_solution": binary_solution,
        "coverage_counts": coverage,
        "feasible": feasible,
        "elapsed_time": elapsed_time,
        "iterations": iterations,
        "history": history,
    }


# %% 10. START THE PROGRAM
# ============================================================

if __name__ == "__main__":
    results = main()
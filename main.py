"""Main application: load -> optimize -> verify -> export.

Run: python main.py [input_instance] [output_report]
"""
from pathlib import Path
import sys
from config import INPUT_FILE, OUTPUT_FILE, TIME_LIMIT, K_MAX, SEED
from scp_reader import read_instance
from feasibility import is_feasible
from solution_utils import calculate_cost, count_coverage
from vns import solve_vns

def main(input_file=None, output_file=None):
    """
    Connect all parts of the program.

    Read data -> solve -> verify -> save the answer.
    """

    input_path = Path(INPUT_FILE if input_file is None else input_file).expanduser()
    output_path = Path(OUTPUT_FILE if output_file is None else output_file).expanduser()

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

    instance = read_instance(str(input_path))
    m, n, costs = instance.m, instance.n, instance.cost
    subsets = [set(elements) for elements in instance.covers]

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

    feasible = is_feasible(instance, sorted(selected)) and covered_count == m

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


if __name__ == "__main__":
    if len(sys.argv) > 3:
        sys.exit("Usage: python main.py [input_instance] [output_report]")
    results = main(
        sys.argv[1] if len(sys.argv) >= 2 else None,
        sys.argv[2] if len(sys.argv) >= 3 else None,
    )

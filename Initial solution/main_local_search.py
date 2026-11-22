import math
import time
from pathlib import Path
from main_1st_sol import *
from local_search import *

# For this we have now removed the swap2-1 move because of its high computation time. 

def mean_and_cv(values: list[float]) -> tuple[float, float]:
    # returns average and coefficient of variance
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    mean = sum(values) / n
    if n == 1 or mean == 0:
        return mean, 0.0

    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    cv = math.sqrt(variance) / mean
    return mean, cv


def main():
    base_dir = Path(__file__).resolve().parent.parent
    instances_dir = base_dir / "instances"
    # Reads all scp*.txt-files in the map instances in order.
    # If we want to run a specific list instead we can use this code: 
    # selected_files = ["scp42.txt", "scp43.txt", "scp51.txt"]
    # instances = [read_instance(str(instances_dir / f)) for f in selected_files]
    
    instances = read_all(str(instances_dir))

    methods = [
        ("Initial (Drop)", None),
        ("Add then drop", local_search_add_then_drop),
        ("Swap 1-1", local_search_swap_1_1),
        ("Remove & repair", local_search_remove_and_repair),
    ]

    costs_by_method = {name: [] for name, _ in methods}
    times_by_method = {name: [] for name, _ in methods}

    for inst in instances:
        greedy_sol = greedy_heuristics(inst)
        init_sol = remove_redundant(greedy_sol, inst)

        print(f"Instance {inst.name} (m={inst.m}, n={inst.n})")
        for name, ls_func in methods:
            t0 = time.perf_counter()
            sol = init_sol if ls_func is None else ls_func(inst, init_sol)
            dt = time.perf_counter() - t0

            assert is_feasible(sol, inst), f"Unfeasible solution for {name} on {inst.name}"
            cost = total_cost(sol, inst)
            costs_by_method[name].append(cost)
            times_by_method[name].append(dt)
            print(f"  {name:16s}: Cost = {cost}, Time = {dt:.4f} s")

    print("Summary of all instances ---")
    print("| Move | Mean Cost (x̄) | c.v. (Cost) | Mean Time (s) | c.v. (Time) |")
    print("| :--- | ---: | ---: | ---: | ---: |")
    for name, _ in methods:
        mean_c, cv_c = mean_and_cv(costs_by_method[name])
        mean_t, cv_t = mean_and_cv(times_by_method[name])
        print(f"| {name} | {mean_c:.2f} | {cv_c:.4f} | {mean_t:.4f} | {cv_t:.4f} |")


if __name__ == "__main__":
    main()
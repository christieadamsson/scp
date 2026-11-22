from main_1st_sol import *
from local_search import *

def main():
    base_dir = Path(__file__).resolve().parent.parent
    instance = read_instance(str(base_dir / "instances" / "scp42.txt"))

    t0 = time.perf_counter()
    greedy_sol = greedy_heuristics(instance)
    init_sol = remove_redundant(greedy_sol, instance)
    t_init = time.perf_counter() - t0

    print(f"Instance: {instance.name} (m={instance.m}, n={instance.n})")
    print(
        f"Initial solution: {len(init_sol)} subsets, "
        f"Cost = {total_cost(init_sol, instance)}, "
        f"Feasible = {is_feasible(init_sol, instance)}, "
        f"Time = {t_init:.4f} s"
    )

    methods = [
        ("Add then drop", local_search_add_then_drop),
        ("Swap 1-1", local_search_swap_1_1),
        ("Swap 2-1", local_search_swap_2_1),
        ("Remove & repair", local_search_remove_and_repair),
    ]

    for name, ls_func in methods:
        t0 = time.perf_counter()
        sol = ls_func(instance, init_sol)
        elapsed = time.perf_counter() - t0
        print(
            f"LS ({name:15s}): {len(sol)} subsets, "
            f"Cost = {total_cost(sol, instance)}, "
            f"Feasible = {is_feasible(sol, instance)}, "
            f"Time = {elapsed:.4f} s"
        )


if __name__ == "__main__":
    main()
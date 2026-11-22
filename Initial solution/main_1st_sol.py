from initial_sol import *
from scp_reader import *
from feasibility import *

# DO NOT REMOVE
"Main function for the first initial solution"

if __name__ == "__main__":
    start_time = time.perf_counter()

    inst = read_instance("instances/scp42.txt")
    greedy_sol = greedy_heuristics(inst)
    after_greedy_time = time.perf_counter() - start_time

    final_sol = remove_redundant(greedy_sol, inst)
    total_time = time.perf_counter() - start_time

    print(f"Instance: {inst.name} (m={inst.m}, n={inst.n})")
    print(
        f"After greedy: {len(greedy_sol)} subsets, "
        f"Cost = {total_cost(greedy_sol, inst)}, "
        f"Feasible = {is_feasible(greedy_sol, inst)}, "
        f"Computation time = {after_greedy_time:.4f} s"
    )
    print(
        f"After redundancy removal: {len(final_sol)} subsets, "
        f"Cost = {total_cost(final_sol, inst)}, "
        f"Feasible = {is_feasible(final_sol, inst)}, "
        f"Time = {total_time:.4f} s"
    )
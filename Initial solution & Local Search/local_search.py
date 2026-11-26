from itertools import combinations
from pathlib import Path
from main_1st_sol import *
from moves import *
import random 


def local_search_add_then_drop(instance, initial_solution):
    # Tests to add a not already selected subset and then remvoes redundant (First improvement) 
    current = set(initial_solution)
    current_cost = total_cost(current, instance)

    keep_searching = True
    while keep_searching:
        keep_searching = False

        # Generate a new random exploration order
        indices = list(range(instance.n))
        random.shuffle(indices)

        for subset_index in indices:
            if subset_index in current:
                continue
            test_sol = add_then_drop_move(current, subset_index, instance)
            test_cost = total_cost(test_sol, instance)

            if test_cost < current_cost:
                current = test_sol
                current_cost = test_cost
                keep_searching = True
                break

    return current



def local_search_swap_1_1(instance, initial_solution):
    # Swaps one selected subset with an unselected subset
    # Random neighborhood exploration - First Improvement

    current = set(initial_solution)
    current_cost = total_cost(current, instance)

    keep_searching = True
    while keep_searching:
        keep_searching = False

        # Randomize selected subsets (OUT)
        picked_subsets = list(current)
        random.shuffle(picked_subsets)

        # Randomize unselected candidates (IN)
        available_subsets = list(range(instance.n))
        random.shuffle(available_subsets)

        for out_sub in picked_subsets:
            for in_sub in available_subsets:
                if in_sub in current:
                    continue
                if instance.cost[in_sub] >= instance.cost[out_sub]:
                    continue

                test_sol = swap_1_1_move(
                    current, out_sub, in_sub, instance
                )

                if test_sol is None:
                    continue

                test_cost = total_cost(test_sol, instance)

                if test_cost < current_cost:
                    current = test_sol
                    current_cost = test_cost
                    keep_searching = True
                    break

            if keep_searching:
                break

    return current




def local_search_swap_2_1(instance, initial_solution):
    # Replaces two selected subsets with one unselected subset
    # Random neighborhood exploration - First Improvement

    current = set(initial_solution)
    current_cost = total_cost(current, instance)

    keep_searching = True
    while keep_searching:
        keep_searching = False

        # Randomize selected subsets
        picked_subsets = list(current)
        random.shuffle(picked_subsets)

        # Randomize candidate subsets
        available_subsets = list(range(instance.n))
        random.shuffle(available_subsets)

        for out1, out2 in combinations(picked_subsets, 2):
            removed_cost = (
                instance.cost[out1] + instance.cost[out2]
            )

            for in_sub in available_subsets:
                if in_sub in current:
                    continue
                if instance.cost[in_sub] >= removed_cost:
                    continue

                test_sol = swap_2_1_move(
                    current, out1, out2, in_sub, instance
                )

                if test_sol is None:
                    continue

                test_cost = total_cost(test_sol, instance)

                if test_cost < current_cost:
                    current = test_sol
                    current_cost = test_cost
                    keep_searching = True
                    break

            if keep_searching:
                break

    return current



def local_search_remove_and_repair(instance, initial_solution):
    # Removes a selected subset, repairs coverage,
    # and removes redundancy - First Improvement

    current = set(initial_solution)
    current_cost = total_cost(current, instance)

    keep_searching = True
    while keep_searching:
        keep_searching = False

        # Randomize the order of selected subsets
        picked_subsets = list(current)
        random.shuffle(picked_subsets)

        for drop_sub in picked_subsets:
            test_sol = remove_and_repair_move(
                current, drop_sub, instance
            )

            test_cost = total_cost(test_sol, instance)

            if test_cost < current_cost:
                current = test_sol
                current_cost = test_cost
                keep_searching = True
                break

    return current



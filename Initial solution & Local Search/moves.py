from itertools import combinations
from main_1st_sol import remove_redundant
from initial_sol import * 


def drop_move(solution, instance):
    # Takes away unnecessary selected subsets where all elements already is being covered by other subsets. 
    # Check with professor if the function should be here instead? 
    return remove_redundant(solution, instance)


def add_then_drop_move(solution, add_index, instance):
    # Adds an uncovered subset (add_index) and removes unnecessary earlier selected subsets
    candidate = set(solution)
    candidate.add(add_index)
    return remove_redundant(candidate, instance)


def swap_1_1_move(solution, out_index, in_index, instance):
    # Swaps a selected index (out_index) to a not already selected subset (in_index). 
    # Returns the new clean solution if it is still feasible, otherwise None
    remaining = set(solution) - {out_index}

    # this is to check the elements within the subsets
    covered = set()
    for j in remaining:
        covered.update(instance.covers[j])
    covered.update(instance.covers[in_index])

    if len(covered) < instance.m:
        return None

    # now we update the subsets with the new that we have swapped (if it was feasible)
    candidate = set(remaining)
    candidate.add(in_index)
    return remove_redundant(candidate, instance)


def swap_2_1_move(solution, out1_index, out2_index, in_index, instance):
    # Swaps two selected index (out1_index & out2_index) to a not already selected subset (in_index). 
    # Returns the new clean solution if it is still feasible, otherwise None
    # Same as the move before except we swap out 2 subsets for one another. 
    remaining = set(solution) - {out1_index, out2_index}

    covered = set()
    for j in remaining:
        covered.update(instance.covers[j])
    covered.update(instance.covers[in_index])

    if len(covered) < instance.m:
        return None

    candidate = set(remaining)
    candidate.add(in_index)
    return remove_redundant(candidate, instance)


def repair_uncovered(solution, instance):
    # Adds un uncovered subsets until all elements 0...m-1 is covered again
    
    repaired = set(solution)

    covered = set()
    for j in repaired:
        covered.update(instance.covers[j])
    uncovered = set(range(instance.m)) - covered

    while uncovered:
        chosen = dispatch_rule(repaired, uncovered, instance)
        repaired.add(chosen)
        uncovered.difference_update(instance.covers[chosen])

    return repaired


def remove_and_repair_move(solution, drop_index, instance):
    # Removes a selected subset (drop_index), repairs uncovered elements (by calling the method above), and cleans redundance
    candidate = set(solution) - {drop_index}
    candidate = repair_uncovered(candidate, instance)
    return remove_redundant(candidate, instance)
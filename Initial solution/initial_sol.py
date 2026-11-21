from __future__ import annotations
from scp_reader import Instance, read_instance

# DO NOT REMOVE
"This is the code for our first solution. It does not generate the best solution and is not yet optimised, however works as a first one. "


def total_cost(selected, instance: Instance) -> int:
    return sum(instance.cost[j] for j in selected)


def tie_breaking_rule(subset_index: int, uncovered: set[int], instance: Instance) -> float:   
    # How many subsets in the instance covers every new uncovered element in this subset. 
    # lower average = more unique (therefore harder to cover) element. 
    
    counts = [
        len(instance.covered_by[elem])
        for elem in instance.covers[subset_index]
        if elem in uncovered
    ]
    if not counts:
        return float("inf")
    
    return sum(counts) / len(counts)


def dispatch_rule(selected: set[int], uncovered: set[int], instance: Instance) -> int:
    # Chooses the subset that gives the lowest cost per new uncovered element.
    # If two has the same cost, we will choose the one that has is more uniqe e.g., element who is covered by the least subsets. 
    # lowest average wins 
    # if still the same lowest index wins 
    best_j = None
    best_ratio = float("inf")
    best_tie = float("inf")

    for j in range(instance.n):
        if j in selected:
            continue

        new_covered = 0
        for elem in instance.covers[j]:
            if elem in uncovered:
                new_covered += 1

        if new_covered > 0:
            ratio = instance.cost[j] / new_covered

            if ratio < best_ratio:
                best_ratio = ratio
                best_tie = tie_breaking_rule(j, uncovered, instance)
                best_j = j
            elif ratio == best_ratio:
                tie_val = tie_breaking_rule(j, uncovered, instance)
                if tie_val < best_tie:
                    best_tie = tie_val
                    best_j = j
                elif tie_val == best_tie:
                    if best_j is None or j < best_j:
                        best_j = j

    if best_j is None:
        raise ValueError("Couldn't find a subset that covers rest of all subsets.")

    return best_j

# GREEDY HEURISTICS
def greedy_heuristics(instance: Instance) -> set[int]:
    # Begins empty and adds a new subset at a time until every element is covered. 
    
    selected = set()
    uncovered = set(range(instance.m))

    while uncovered:
        j = dispatch_rule(selected, uncovered, instance)
        selected.add(j)
        for elem in instance.covers[j]:
            uncovered.discard(elem)

    return selected


def count_coverage(selected: set[int], instance: Instance) -> list[int]:
    # Counts how many of the chosen subsets that covers each element, 
    # this is for the redundancy removal and should not be confused with tie-breaking rule. 
    
    coverage = [0] * instance.m
    for j in selected:
        for elem in instance.covers[j]:
            coverage[elem] += 1
    return coverage

# REDUNDANCY REMOVAL
def remove_redundant(solution: set[int], instance: Instance) -> set[int]:
    # Goes through chosen subsets from most expensive to least, 
    # Takes away the subsets whos elements are covered by at least another subsets.
     
    selected = set(solution)
    coverage = count_coverage(selected, instance)

    expensive_first = sorted(selected, key=lambda j: instance.cost[j], reverse=True)

    for j in expensive_first:
        # Can be removed if every element i in subset j has a coverage of >= 2
        if all(coverage[elem] >= 2 for elem in instance.covers[j]):
            selected.remove(j)
            for elem in instance.covers[j]:
                coverage[elem] -= 1

    return selected


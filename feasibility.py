from __future__ import annotations
from scp_reader import Instance

def is_feasible(instance: Instance, solution: list[int]) -> bool:
    """
    Verifies if a candidate solution (list of subset indices, 0-based) is feasible 
    for the given Set Covering Problem instance using instance.covered_by.
    
    Parameters:
    - instance: The SCP Instance object (containing m, n, covered_by, etc.).
    - solution: List of selected subset indices (0-based).
    
    Returns:
    - True if every element is covered at least once and indices are valid, else False.
    """
    # 1. Check for duplicates by comparing length with a set
    sol_set = set(solution)
    if len(sol_set) != len(solution):
        return False  # Invalid: duplicates present in the solution
        
    # 2. Check that all indices are within the valid range [0, n-1]
    for j in solution:
        if not (0 <= j < instance.n):
            return False  # Invalid: index out of bounds

    # 3. Check coverage constraint via covered_by[i] (according to Section E)
    for i in range(instance.m):
        # Check if at least one subset covering element i is present in the solution (early exit)
        if not any(j in sol_set for j in instance.covered_by[i]):
            return False  # Infeasible: element i lacks coverage entirely

    # If all elements have at least one covering subset, the solution is valid
    return True
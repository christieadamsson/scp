"""
scp_reader.py - Reads Set Covering Problem instances in the OR-Library format
(J.E. Beasley: scp41 ... scp410, scp51 ... scp510, scp61 ... scp65,
scpa1 ... scpd5).

FILE FORMAT (all values are integers, separated by spaces/line breaks)
    m  n                      -> number of elements (rows) and of subsets (columns)
    c_1 c_2 ... c_n           -> cost of each subset
    for each element i = 1..m:
        k_i                   -> number of subsets that cover element i
        j_1 j_2 ... j_k       -> the subsets that cover element i (1-based)

The lists wrap over several lines (12 numbers per line), so line breaks
carry no meaning. The reader therefore reads the whole file as a single
stream of integers and consumes it in order.

INTERNAL CONVENTIONS (used by the whole group)
    * Everything is 0-based: subset j in the file  -> index j-1 here,
                             element i in the file -> index i-1 here.
      (index 0 = subset 1, index 1 = subset 2, ... as in the dispatch rule)
    * When reporting a solution, convert back to 1-based: index 0 -> S1.

STORED DATA (instead of the full m x n matrix a_ij, which is ~95-98% zeros)
    cost[j]        cost of subset j                               (c_j)
    covered_by[i]  list of subsets that cover element i           (a_ij = 1 for these j)
    covers[j]      list of elements that subset j covers          (a_ij = 1 for these i)
    a_ij = 1  <=>  j in covered_by[i]  <=>  i in covers[j]

    covered_by is what the file gives directly (useful for the feasibility
    test: every element needs at least one selected subset in covered_by[i]).
    covers is built by inverting it (needed by the dispatch rule: count the
    uncovered elements inside subset j).
"""

from __future__ import annotations

import os
import re
import sys
import time
from dataclasses import dataclass, field


@dataclass
class Instance:
    name: str                       # e.g. "4.1", "A.3" (same labels as the best-solutions file)
    m: int                          # number of elements (rows)
    n: int                          # number of subsets (columns)
    cost: list[int]                 # cost[j], j = 0..n-1
    covered_by: list[list[int]]     # covered_by[i] = subsets covering element i, i = 0..m-1
    covers: list[list[int]] = field(default_factory=list)  # covers[j] = elements in subset j

    @property
    def nonzeros(self) -> int:
        return sum(len(s) for s in self.covered_by)

    @property
    def density(self) -> float:
        """Share of a_ij entries equal to 1 (2% or 5% for these instances)."""
        return self.nonzeros / (self.m * self.n)


def instance_name(path: str) -> str:
    """'scp41.txt' -> '4.1', 'scp410.txt' -> '4.10', 'scpa1.txt' -> 'A.1', 'scpnre1.txt' -> 'NRE.1'."""
    base = os.path.splitext(os.path.basename(path))[0].lower()
    match = re.fullmatch(r"scp(nr[a-z]|[0-9a-z])(\d+)", base)
    if not match:
        return base                      # unknown naming: keep the file name
    group, number = match.groups()
    return f"{group.upper()}.{number}"


def read_instance(path: str) -> Instance:
    """Read one OR-Library SCP file and return an Instance (0-based indices)."""
    with open(path) as f:
        numbers = [int(tok) for tok in f.read().split()]

    pos = 0

    def take(count: int) -> list[int]:
        nonlocal pos
        if pos + count > len(numbers):
            raise ValueError(f"{path}: file ended early (expected more numbers)")
        chunk = numbers[pos:pos + count]
        pos += count
        return chunk

    m, n = take(2)
    cost = take(n)
    if any(c <= 0 for c in cost):
        raise ValueError(f"{path}: all costs must be > 0")

    covered_by = []
    for i in range(m):
        (k,) = take(1)
        if k < 1:
            raise ValueError(f"{path}: element {i + 1} is covered by no subset -> no feasible cover")
        subsets = take(k)
        if min(subsets) < 1 or max(subsets) > n:
            raise ValueError(f"{path}: element {i + 1} lists a subset outside 1..{n}")
        if len(set(subsets)) != k:
            raise ValueError(f"{path}: element {i + 1} lists the same subset twice")
        covered_by.append([j - 1 for j in subsets])          # 1-based -> 0-based

    if pos != len(numbers):
        raise ValueError(f"{path}: {len(numbers) - pos} unexpected numbers at the end of the file")

    # Invert covered_by (element -> subsets) into covers (subset -> elements).
    covers: list[list[int]] = [[] for _ in range(n)]
    for i, subsets in enumerate(covered_by):
        for j in subsets:
            covers[j].append(i)

    return Instance(instance_name(path), m, n, cost, covered_by, covers)


def read_best_known(path: str) -> dict[str, int]:
    """Read lines like '4.1 429' -> {'4.1': 429, ...}."""
    best = {}
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                best[parts[0].upper()] = int(parts[1])
    return best


def read_all(folder: str) -> list[Instance]:
    """Read every scp*.txt file in a folder, in the order 4.1, 4.2, ..., 4.10, 5.1, ..., D.5."""
    files = [f for f in os.listdir(folder) if f.lower().startswith("scp") and f.lower().endswith(".txt")]

    def order(f: str):
        group, _, number = instance_name(f).partition(".")
        return (group, int(number) if number.isdigit() else 0)

    return [read_instance(os.path.join(folder, f)) for f in sorted(files, key=order)]


def describe(inst: Instance) -> str:
    sizes = [len(s) for s in inst.covers]
    return (f"{inst.name}: m={inst.m} elements, n={inst.n} subsets, "
            f"density={inst.density:.2%}, cost {min(inst.cost)}-{max(inst.cost)}, "
            f"elements per subset {min(sizes)}-{max(sizes)}, "
            f"subsets per element {min(len(s) for s in inst.covered_by)}-{max(len(s) for s in inst.covered_by)}")


if __name__ == "__main__":
    # Usage: python scp_reader.py <instance file or folder> [SCP_Best_Solutions.txt]
    if len(sys.argv) < 2:
        sys.exit("usage: python scp_reader.py <instance file or folder> [best_solutions.txt]")
    target = sys.argv[1]
    best = read_best_known(sys.argv[2]) if len(sys.argv) > 2 else {}

    start = time.perf_counter()
    instances = read_all(target) if os.path.isdir(target) else [read_instance(target)]
    elapsed = time.perf_counter() - start

    for inst in instances:
        bks = best.get(inst.name)
        print(describe(inst) + (f", best known={bks}" if bks is not None else ""))
    print(f"\n{len(instances)} instance(s) read in {elapsed:.2f} s")

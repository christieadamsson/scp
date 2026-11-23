"""
scp_reader.py - Reads SCP instances in Beasley's OR-Library format.

Format: m n, then n subset costs, then for each element: the number of
subsets covering it followed by their IDs (1-based). Lists wrap over
lines, so the file is read as one stream of integers.

All indices are 0-based internally (subset j in the file -> j-1).
covered_by[i] = subsets that cover element i
covers[j]     = elements covered by subset j
"""

from __future__ import annotations

import os
import re
import sys
import time
from dataclasses import dataclass


@dataclass
class Instance:
    name: str                       # e.g. "4.1", "A.3" (same labels as the best-solutions file)
    m: int                          # number of elements (rows)
    n: int                          # number of subsets (columns)
    cost: list[int]                 # cost[j], j = 0..n-1
    covered_by: list[list[int]]     # covered_by[i] = subsets covering element i, i = 0..m-1
    covers: list[list[int]]         # covers[j] = elements in subset j

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

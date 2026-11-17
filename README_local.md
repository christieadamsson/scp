# SCP — modular version

This folder splits the supplied working `solution.py` into separate responsibilities, while retaining the original file as `solution_original.py`.

| File | Responsibility |
| --- | --- |
| `scp_reader.py` | Team's instance reader and `Instance` model |
| `feasibility.py` | Team's feasibility checker |
| `dispatch_rule.py` | Candidate ranking and selection (greedy or randomized top 3) |
| `constructive.py` | Construction/repair and redundant-set removal |
| `solution_utils.py` | Objective cost and coverage counts |
| `local_search.py` | Deterministic local improvement |
| `vns.py` | Shaking, randomized repair, acceptance, neighborhood changes |
| `config.py` | File paths and parameters |
| `main.py` | Integration, final feasibility check and TXT report |

## Run

Put the SCP instance in `instances/scp42.txt`, then run `python main.py` from anywhere. Alternatively supply instance and report paths:

```powershell
python main.py "C:\path\to\scp42.txt" "C:\path\to\result.txt"
```

## Compatibility notes

- Uses 0-based indices internally, 1-based IDs in the report.
- `scp_reader.py` returns an `Instance` with `covers` lists; `main.py` converts these to sets for the unchanged solver functions.
- The dispatch rule follows the *current working code*: ties use the lowest set index, not the maximum newly-covered elements from the team's draft.
- `feasibility.py` is called in `main.py` alongside the original coverage counts check.
- The VNS algorithm and parameters have not been redesigned.
- The original partner modules are preserved without modification; `solution_original.py` is kept as a reference.

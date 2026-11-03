"""Compare two JSON files: same structure, strings and integers; floats equal within 1e-3 (relative, floor 1).

Used by regen_check.sh for JSON outputs. Recomputing on another OS/BLAS (macOS dev vs Linux CI) can flip the
last rounded digit of a float that sits on a rounding boundary (e.g. spearman 0.12105 -> 0.121 vs 0.1211).
"""

import json
import sys

TOL = 1e-3


def close(a, b, path="$") -> list[str]:
    if isinstance(a, float) or isinstance(b, float):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
            return [] if abs(a - b) <= TOL * max(1.0, abs(a)) else [f"{path}: {a} != {b}"]
        return [f"{path}: {a!r} != {b!r}"]
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return [f"{path}: keys differ {sorted(set(a) ^ set(b))}"]
        return [m for k in a for m in close(a[k], b[k], f"{path}.{k}")]
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} != {len(b)}"]
        return [m for i, (x, y) in enumerate(zip(a, b, strict=True)) for m in close(x, y, f"{path}[{i}]")]
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


if __name__ == "__main__":
    with open(sys.argv[1]) as fa, open(sys.argv[2]) as fb:
        diffs = close(json.load(fa), json.load(fb))
    for d in diffs[:20]:
        print(d)
    sys.exit(1 if diffs else 0)

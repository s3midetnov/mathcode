"""
Key question: does D_n(k) = dim span{g·f_n : g in B_k} stabilize as n -> infinity?

Uses function-space BFS (avoids storing permutation arrays) and incremental
Gaussian elimination. Memory-safe: kept well under 200 MB.

Safe parameters: k <= 8, n <= 12.
"""

import numpy as np
import sys
from collections import deque


def apply_a_int(x, n):
    if n == 0:
        return x
    half = 1 << (n - 1)
    return x if x < half else half + apply_b_int(x - half, n - 1)


def apply_b_int(x, n):
    if n == 0:
        return x
    half = 1 << (n - 1)
    return (half + x) if x < half else apply_a_int(x - half, n - 1)


def build_gen_actions(n):
    """
    4 index arrays for generator actions on functions:
      a·f(x)    = f(a^{-1}(x)) -> new_f = f[inv_a]
      b·f(x)    = f(b^{-1}(x)) -> new_f = f[inv_b]
      a^{-1}·f  = f[perm_a]
      b^{-1}·f  = f[perm_b]
    """
    N = 2 ** n
    perm_a = np.array([apply_a_int(x, n) for x in range(N)], dtype=np.int32)
    perm_b = np.array([apply_b_int(x, n) for x in range(N)], dtype=np.int32)
    inv_a = np.argsort(perm_a).astype(np.int32)
    inv_b = np.argsort(perm_b).astype(np.int32)
    return [inv_a, inv_b, perm_a, perm_b]


class IncrementalZ2Basis:
    """Incrementally maintains a Z/2 row basis via Gaussian elimination."""

    def __init__(self, N):
        self.N = N
        self.basis = []       # reduced basis vectors (np.uint8 arrays)
        self.pivot_col = []   # pivot column for each basis vector
        self.pivot_to_idx = {}  # col -> index in self.basis

    def try_add(self, row):
        """Try to add row to basis. Returns True if it increased the rank."""
        v = row.copy()
        for col, idx in sorted(self.pivot_to_idx.items()):
            if v[col]:
                v ^= self.basis[idx]
        nz = np.nonzero(v)[0]
        if len(nz) == 0:
            return False
        col = nz[0]
        # Eliminate this column from all existing basis vectors
        for i, b in enumerate(self.basis):
            if b[col]:
                self.basis[i] = b ^ v
        self.basis.append(v)
        self.pivot_col.append(col)
        self.pivot_to_idx[col] = len(self.basis) - 1
        return True

    def rank(self):
        return len(self.basis)


def compute_Dn_k(n, max_k, verbose=False):
    """
    BFS in function-space to compute D_n(k) for k=1,...,max_k.
    Returns list of (k, orbit_size, dim).
    """
    N = 2 ** n
    gen_actions = build_gen_actions(n)
    f0 = np.array([x & 1 for x in range(N)], dtype=np.uint8)

    seen = {}
    def fkey(f): return f.tobytes()

    basis = IncrementalZ2Basis(N)
    basis.try_add(f0)

    seen[fkey(f0)] = True
    current_layer = [f0]
    orbit_size = 1
    results = []

    for k in range(1, max_k + 1):
        next_layer = []
        for f in current_layer:
            for act in gen_actions:
                new_f = f[act]
                fk = fkey(new_f)
                if fk not in seen:
                    seen[fk] = True
                    next_layer.append(new_f)
                    basis.try_add(new_f)
        current_layer = next_layer
        orbit_size += len(next_layer)
        results.append((k, orbit_size, basis.rank()))
        if verbose:
            print(f"    k={k}: orbit={orbit_size}, dim={basis.rank()}")
        if not current_layer:
            for kk in range(k + 1, max_k + 1):
                results.append((kk, orbit_size, basis.rank()))
            break

    return results


def main():
    max_k = 8
    max_n = 12

    # Memory estimate: orbit_size * N bytes for function storage
    # orbit_size <= |B_k|. At k=8: ~7543. At n=12: N=4096.
    # 7543 * 4096 = 30 MB for functions + 30 MB for basis. Safe.

    print("D_n(k) table: does it stabilize as n grows for fixed k?")
    print("Rows = level n, Cols = word length k")
    print()

    header = f"{'n':>4} {'N':>6}"
    for k in range(1, max_k + 1):
        header += f"  k={k}"
    print(header)

    all_dims = {}
    ball_sizes_ref = None

    for n in range(1, max_n + 1):
        N = 2 ** n
        # conservative memory check: assume orbit ~ 7543 rows, each N bytes
        est_mb = 7543 * N * 2 / 1e6
        if est_mb > 300:
            print(f"  n={n:2d}: skipping (est. {est_mb:.0f} MB)")
            continue

        sys.stdout.write(f"  n={n:2d}  N={N:5d}")
        sys.stdout.flush()

        profile = compute_Dn_k(n, max_k)
        all_dims[n] = {k: d for k, _, d in profile}
        if ball_sizes_ref is None:
            ball_sizes_ref = {k: bs for k, bs, _ in profile}

        for k in range(1, max_k + 1):
            d = all_dims[n].get(k, 0)
            sys.stdout.write(f"  {d:4d}")
        sys.stdout.write("\n")
        sys.stdout.flush()

    # Summary: for each fixed k, show D_n(k) vs n
    print()
    print("D_n(k) by column (fixed k, varying n) — check if each column stabilizes:")
    for k in range(1, max_k + 1):
        row = [all_dims[n].get(k, "?") for n in sorted(all_dims)]
        bs = ball_sizes_ref.get(k, "?")
        print(f"  k={k}: |B_k|={bs:6}  D_n: {row}")

    # Total orbit dim for the infinite tree (sum over levels, lower bound)
    print()
    print("Sum of D_n(k) over n=1..{} (lower bound on true orbit dim on infinite tree):".format(max_n))
    print(f"{'k':>4} {'|B_k|':>8} {'sum_D':>8} {'ratio':>8}")
    for k in range(1, max_k + 1):
        total = sum(all_dims[n].get(k, 0) for n in all_dims)
        bs = ball_sizes_ref.get(k, 1)
        print(f"  {k:2d}  {bs:8d}  {total:8d}  {total/bs:.4f}")


if __name__ == "__main__":
    main()

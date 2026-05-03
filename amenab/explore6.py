"""
Track incremental rank contributions per level to test convergence.

For each level n added to the concatenated matrix, how much does the rank grow?
If increments go to 0, the true orbit dim converges; otherwise it diverges.

Memory: 7545 * (2 + 4 + ... + 2^n_max) bytes. Safe for n_max <= 12 (~62 MB).
"""

import numpy as np
import sys
import time

BALL_SIZES = {1: 5, 2: 17, 3: 53, 4: 153, 5: 421, 6: 1125, 7: 2945, 8: 7543}

def apply_a_int(x, n):
    if n == 0: return x
    half = 1 << (n - 1)
    return x if x < half else half + apply_b_int(x - half, n - 1)

def apply_b_int(x, n):
    if n == 0: return x
    half = 1 << (n - 1)
    return (half + x) if x < half else apply_a_int(x - half, n - 1)


class IncrementalZ2Basis:
    def __init__(self):
        self.basis = []
        self.pivots = {}  # col -> basis index

    def try_add(self, row):
        v = row.copy()
        for col in sorted(self.pivots):
            if v[col]:
                v ^= self.basis[self.pivots[col]]
        nz = np.nonzero(v)[0]
        if len(nz) == 0:
            return False
        col = int(nz[0])
        for i, b in enumerate(self.basis):
            if b[col]:
                self.basis[i] = b ^ v
        self.pivots[col] = len(self.basis)
        self.basis.append(v)
        return True

    def rank(self):
        return len(self.basis)

    def try_add_many(self, rows):
        for r in rows:
            self.try_add(r)


def build_gen_actions(n):
    N = 2 ** n
    pa = np.array([apply_a_int(x, n) for x in range(N)], dtype=np.int32)
    pb = np.array([apply_b_int(x, n) for x in range(N)], dtype=np.int32)
    ia = np.argsort(pa).astype(np.int32)
    ib = np.argsort(pb).astype(np.int32)
    return [ia, ib, pa, pb]


def enumerate_orbit_at_level(n, max_k, all_gen):
    """BFS to enumerate orbit of f_n under B_{max_k}.
    Returns list of (k, list_of_new_rows_as_uint8_arrays)."""
    N = 2 ** n
    gen_acts = all_gen[n]
    f0 = np.array([x & 1 for x in range(N)], dtype=np.uint8)

    seen = {}
    def key(f): return f.tobytes()

    seen[key(f0)] = True
    current_layer = [f0]
    layers = {0: [f0]}

    for k in range(1, max_k + 1):
        next_layer = []
        for f in current_layer:
            for act in gen_acts:
                new_f = f[act]
                fk = key(new_f)
                if fk not in seen:
                    seen[fk] = True
                    next_layer.append(new_f)
        current_layer = next_layer
        layers[k] = next_layer[:]
        if not next_layer:
            for kk in range(k + 1, max_k + 1):
                layers[kk] = []
            break

    return layers


def main():
    max_k = 8
    max_n = 12

    print(f"Incremental rank analysis: how much does each level n add to rank?")
    print(f"k={max_k}, levels 1..{max_n}")
    print()
    print("Step 1: Enumerate orbit at each level...")

    t0 = time.time()
    all_gen = {}
    for n in range(1, max_n + 1):
        all_gen[n] = build_gen_actions(n)
        sys.stdout.write(f"  built gen actions for n={n}\r")
        sys.stdout.flush()
    print(f"  Gen actions built in {time.time()-t0:.1f}s")

    # For each level n, enumerate the orbit of f_n under B_{max_k}
    level_orbits = {}
    for n in range(1, max_n + 1):
        t1 = time.time()
        layers = enumerate_orbit_at_level(n, max_k, all_gen)
        orbit_size = sum(len(v) for v in layers.values())
        level_orbits[n] = layers
        sys.stdout.write(f"  Level {n}: orbit size = {orbit_size} ({time.time()-t1:.1f}s)\n")
        sys.stdout.flush()

    print()
    print("Step 2: Compute cumulative rank as levels are added one by one (at k=8)...")
    print(f"{'n':>4}  {'D_n(8)':>8}  {'cum_rank':>10}  {'delta':>7}  {'level_N':>9}")

    cumulative_basis = IncrementalZ2Basis()
    prev_rank = 0

    for n in range(1, max_n + 1):
        # Collect all rows at level n for B_{max_k}
        all_rows_n = []
        for k_step in range(0, max_k + 1):
            all_rows_n.extend(level_orbits[n][k_step])

        # Individual rank at this level
        basis_n = IncrementalZ2Basis()
        for r in all_rows_n:
            basis_n.try_add(r)
        dn = basis_n.rank()

        # Add to cumulative
        cumulative_basis.try_add_many(all_rows_n)
        cum_rank = cumulative_basis.rank()
        delta = cum_rank - prev_rank
        prev_rank = cum_rank

        N = 2 ** n
        print(f"  {n:2d}  {dn:8d}  {cum_rank:10d}  {delta:7d}  {N:9d}")
        sys.stdout.flush()

    print()
    bs = BALL_SIZES.get(max_k, "?")
    cum = cumulative_basis.rank()
    print(f"True orbit dim (levels 1..{max_n}): {cum}")
    print(f"|B_{max_k}| (at level 8): {bs}")
    print(f"Ratio: {cum / bs:.4f}")

    print()
    print("Step 3: Also check for k=1..8 at full depth (n_max=12)...")
    print(f"{'k':>4}  {'orbit(12)':>10}  {'rank':>8}  {'|B_k|':>8}  {'ratio':>8}")

    for k in range(1, max_k + 1):
        # Collect all rows across all levels for this k
        basis_k = IncrementalZ2Basis()
        for n in range(1, max_n + 1):
            for k_step in range(0, k + 1):
                for r in level_orbits[n][k_step]:
                    basis_k.try_add(r)
        bs_k = BALL_SIZES.get(k, "?")
        rank_k = basis_k.rank()
        ratio = f"{rank_k / bs_k:.4f}" if isinstance(bs_k, int) else "?"
        orbit_12 = sum(len(level_orbits[12][j]) for j in range(k + 1))
        print(f"  {k:2d}  {orbit_12:10d}  {rank_k:8d}  {bs_k:>8}  {ratio:>8}")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

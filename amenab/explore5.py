"""
Compute the TRUE orbit dim of f='last bit' on the FULL TREE under B_k.

Key question: what is rank([M_1 | M_2 | ... | M_n]) as n grows?
Does it stabilize even though D_n(k) oscillates?

Uses tuple-BFS: each BFS state is (g·f_1, g·f_2, ..., g·f_{n_max}) concatenated.
Memory: orbit_size * (2 + 4 + ... + 2^n_max) bytes.
For n_max=10, orbit<=7543: ~15 MB. Safe.
"""

import numpy as np
import sys

BALL_SIZES = {1: 5, 2: 17, 3: 53, 4: 153, 5: 421, 6: 1125, 7: 2945, 8: 7543}

def apply_a_int(x, n):
    if n == 0: return x
    half = 1 << (n - 1)
    return x if x < half else half + apply_b_int(x - half, n - 1)

def apply_b_int(x, n):
    if n == 0: return x
    half = 1 << (n - 1)
    return (half + x) if x < half else apply_a_int(x - half, n - 1)

def build_all_gen_actions(n_max):
    gen = {}
    for n in range(1, n_max + 1):
        N = 2 ** n
        pa = np.array([apply_a_int(x, n) for x in range(N)], dtype=np.int32)
        pb = np.array([apply_b_int(x, n) for x in range(N)], dtype=np.int32)
        ia = np.argsort(pa).astype(np.int32)
        ib = np.argsort(pb).astype(np.int32)
        gen[n] = [ia, ib, pa, pb]  # [a, b, a^{-1}, b^{-1}] in function space
    return gen

def make_offsets(n_max):
    offsets = {}
    off = 0
    for n in range(1, n_max + 1):
        offsets[n] = off
        off += 2 ** n
    return offsets, off  # off = total length

def make_initial_tuple(n_max, offsets, total_len):
    t = np.zeros(total_len, dtype=np.uint8)
    for n in range(1, n_max + 1):
        N = 2 ** n
        off = offsets[n]
        t[off:off + N] = np.arange(N, dtype=np.uint8) & 1
    return t

def apply_gen_to_tuple(t, gen_idx, all_gen, n_max, offsets, total_len):
    new_t = np.empty(total_len, dtype=np.uint8)
    for n in range(1, n_max + 1):
        N = 2 ** n
        off = offsets[n]
        act = all_gen[n][gen_idx]
        new_t[off:off + N] = t[off:off + N][act]
    return new_t

def incremental_rank(all_rows, total_len):
    """Gaussian elimination over Z/2, incremental."""
    basis = []
    pivots = {}

    for row in all_rows:
        v = row.copy()
        for col, bi in sorted(pivots.items()):
            if v[col]:
                v ^= basis[bi]
        nz = np.nonzero(v)[0]
        if len(nz) == 0:
            continue
        col = nz[0]
        for i, b in enumerate(basis):
            if b[col]:
                basis[i] = b ^ v
        pivots[col] = len(basis)
        basis.append(v)

    return len(basis)

def run(n_max, max_k):
    total_N = sum(2 ** n for n in range(1, n_max + 1))
    offsets, total_len = make_offsets(n_max)
    all_gen = build_all_gen_actions(n_max)
    t0 = make_initial_tuple(n_max, offsets, total_len)

    seen = {}
    def key(t): return t.tobytes()

    seen[key(t0)] = True
    current_layer = [t0]
    all_rows = [t0.copy()]
    orbit_size = 1

    print(f"  Levels 1..{n_max}, total columns = {total_len}, est. max memory = {7543 * total_len // 1_000_000 + 1} MB")
    print(f"  {'k':>4}  {'orbit':>8}  {'rank':>8}  {'|B_k|':>8}  {'ratio':>8}")

    # rank for k=0
    r0 = incremental_rank(all_rows, total_len)
    print(f"  {0:4d}  {1:8d}  {r0:8d}")

    for k in range(1, max_k + 1):
        next_layer = []
        for t in current_layer:
            for gi in range(4):
                new_t = apply_gen_to_tuple(t, gi, all_gen, n_max, offsets, total_len)
                tk = key(new_t)
                if tk not in seen:
                    seen[tk] = True
                    next_layer.append(new_t)
                    all_rows.append(new_t.copy())
        current_layer = next_layer
        orbit_size += len(next_layer)

        rank = incremental_rank(all_rows, total_len)
        bs = BALL_SIZES.get(k, "?")
        ratio = f"{rank / bs:.4f}" if isinstance(bs, int) else "?"
        print(f"  {k:4d}  {orbit_size:8d}  {rank:8d}  {bs:>8}  {ratio:>8}")
        sys.stdout.flush()

        if not current_layer:
            print("  (orbit saturated)")
            break

def main():
    # Check: does rank([M_1|...|M_{n_max}]) stabilize as n_max grows?
    # Run for n_max = 8, 9, 10 and fixed k=8, compare ranks.

    max_k = 8

    print("=== True orbit dim vs n_max (fixed k, increasing n_max) ===")
    print(f"Shows rank of [M_1 | ... | M_{{n_max}}] for k=1..{max_k}\n")

    for n_max in [8, 9, 10]:
        print(f"\n--- n_max = {n_max} ---")
        run(n_max, max_k)

if __name__ == "__main__":
    main()

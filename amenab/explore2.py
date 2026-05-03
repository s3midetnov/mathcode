"""
More careful exploration: compute orbit dim vs k across multiple levels,
check group growth rate, and look for good f on the infinite tree.

Key question: for f(v) = v_{|v|-1} (last bit of v, defined at each level),
is sum_n orbit_dim(f_n, k) = o(|B_k|)?
"""

import numpy as np
from functools import lru_cache


def build_permutations(n):
    N = 2 ** n
    perm_a = np.zeros(N, dtype=np.int32)
    perm_b = np.zeros(N, dtype=np.int32)
    for x in range(N):
        perm_a[x] = apply_a_int(x, n)
        perm_b[x] = apply_b_int(x, n)
    return perm_a, perm_b


def apply_a_int(x, n):
    if n == 0:
        return x
    half = 1 << (n - 1)
    if x < half:
        return x
    else:
        return half + apply_b_int(x - half, n - 1)


def apply_b_int(x, n):
    if n == 0:
        return x
    half = 1 << (n - 1)
    if x < half:
        return half + x
    else:
        return apply_a_int(x - half, n - 1)


def gaussian_elim_z2(rows, N):
    """Gaussian elimination over Z/2, returns rank. rows: list of np.uint8 arrays of length N."""
    if not rows:
        return 0
    M = np.array(rows, dtype=np.uint8)
    m = M.shape[0]
    rank = 0
    for col in range(N):
        found = -1
        for row in range(rank, m):
            if M[row, col]:
                found = row
                break
        if found == -1:
            continue
        M[[rank, found]] = M[[found, rank]]
        mask = M[:, col].astype(bool)
        mask[rank] = False
        M[mask] = (M[mask] + M[rank]) % 2
        rank += 1
        if rank == m:
            break
    return rank


def compute_orbit_dim_profile(n, max_k, f_vec=None):
    """
    For level n, compute orbit dim vs k and group ball sizes.
    f_vec: function on {0,...,2^n-1}. Default = last bit.
    Returns: list of (k, ball_size, orbit_dim)
    """
    N = 2 ** n
    perm_a, perm_b = build_permutations(n)
    inv_a = np.argsort(perm_a).astype(np.int32)
    inv_b = np.argsort(perm_b).astype(np.int32)
    generators = [perm_a, perm_b, inv_a, inv_b]

    if f_vec is None:
        f_vec = np.array([x & 1 for x in range(N)], dtype=np.uint8)  # last bit

    identity = np.arange(N, dtype=np.int32)

    seen = {tuple(identity): True}
    current_layer = [identity]
    all_rows = [f_vec[np.arange(N)].astype(np.uint8)]  # identity acts trivially

    results = []
    ball_size = 1

    for k in range(1, max_k + 1):
        next_layer = []
        for elem in current_layer:
            for gen in generators:
                new_elem = gen[elem]
                key = tuple(new_elem)
                if key not in seen:
                    seen[key] = True
                    next_layer.append(new_elem)
                    inv_perm = np.argsort(new_elem)
                    all_rows.append(f_vec[inv_perm].astype(np.uint8))
        current_layer = next_layer
        ball_size += len(next_layer)
        dim = gaussian_elim_z2(all_rows, N)
        results.append((k, ball_size, dim))
        if not current_layer:
            for kk in range(k + 1, max_k + 1):
                results.append((kk, ball_size, dim))
            break

    return results


def compute_level_profiles(levels, max_k):
    """For each level, compute orbit dim of 'last bit' vs k."""
    all_profiles = {}
    for n in levels:
        print(f"\n=== Level n={n} (N={2**n} strings) ===")
        profile = compute_orbit_dim_profile(n, max_k)
        all_profiles[n] = profile
        for k, bs, d in profile:
            print(f"  k={k:2d}: |B_k|={bs:8d}, orbit_dim={d:4d}, ratio={d/bs:.5f}")
    return all_profiles


def compute_total_orbit_profile(levels, max_k):
    """
    Compute total orbit dim = sum over levels of orbit dim at that level.
    Also compute |B_k| (same across levels, use level max_level).
    """
    print("\n=== Computing profiles for all levels ===")
    level_profiles = {}
    ball_sizes = None

    for n in levels:
        profile = compute_orbit_dim_profile(n, max_k)
        level_profiles[n] = {k: (bs, d) for k, bs, d in profile}
        if ball_sizes is None:
            ball_sizes = {k: bs for k, bs, d in profile}
        else:
            # Update ball sizes to max across levels (should be same, but just in case)
            for k, bs, d in profile:
                ball_sizes[k] = max(ball_sizes[k], bs)
        last = profile[-1]
        print(f"  Level {n}: final dim={last[2]}, |B_k|={last[1]}")

    print("\n=== Total orbit dim (sum over levels) vs k ===")
    print(f"{'k':>4} {'|B_k|':>10} {'sum_dim':>10} {'ratio':>10}")
    for k in range(1, max_k + 1):
        bs = ball_sizes[k]
        total_dim = sum(level_profiles[n][k][1] for n in levels)
        ratio = total_dim / bs
        print(f"  {k:2d}  {bs:10d}  {total_dim:10d}  {ratio:.6f}")


def analyze_group_growth(n_for_growth=8, max_k=14):
    """Analyze growth rate of the group."""
    print(f"\n=== Group growth (level n={n_for_growth}) ===")
    N = 2 ** n_for_growth
    perm_a, perm_b = build_permutations(n_for_growth)
    inv_a = np.argsort(perm_a).astype(np.int32)
    inv_b = np.argsort(perm_b).astype(np.int32)
    generators = [perm_a, perm_b, inv_a, inv_b]

    identity = np.arange(N, dtype=np.int32)
    seen = {tuple(identity): True}
    current_layer = [identity]
    ball_size = 1

    print(f"  k=0: |B_k|=1")
    prev = 1
    for k in range(1, max_k + 1):
        next_layer = []
        for elem in current_layer:
            for gen in generators:
                new_elem = gen[elem]
                key = tuple(new_elem)
                if key not in seen:
                    seen[key] = True
                    next_layer.append(new_elem)
        current_layer = next_layer
        ball_size += len(next_layer)
        ratio = ball_size / prev if prev > 0 else 0
        print(f"  k={k:2d}: |B_k|={ball_size:10d}, growth ratio={ratio:.4f}, sphere={len(next_layer)}")
        prev = ball_size
        if not current_layer:
            print(f"  Group closed at k={k}!")
            break


if __name__ == "__main__":
    # 1. Analyze group growth rate
    analyze_group_growth(n_for_growth=8, max_k=12)

    # 2. Profile orbit dim at multiple levels
    levels = [3, 4, 5, 6, 7, 8]
    max_k = 10
    compute_total_orbit_profile(levels, max_k)

    # 3. Deep dive: look at different bit positions at level n=8
    print("\n=== Different bit positions at level n=8 ===")
    n = 8
    N = 2 ** n
    perm_a, perm_b = build_permutations(n)
    print(f"{'bit_pos':>8}", end="")
    for k in [2, 4, 6, 8, 10]:
        print(f"  k={k:2d}", end="")
    print()

    for bit_pos in range(n):
        f_vec = np.array([(x >> bit_pos) & 1 for x in range(N)], dtype=np.uint8)
        profile = compute_orbit_dim_profile(n, max_k=10, f_vec=f_vec)
        dims = {k: d for k, bs, d in profile}
        print(f"  bit[{n-1-bit_pos}]  ", end="")  # bit_pos=0 is LSB = last bit in MSB-first notation
        for k in [2, 4, 6, 8, 10]:
            print(f"  {dims[k]:5d}", end="")
        print()

"""
Verify total orbit dim growth for larger k, and understand why 'last bit' works.
Also: try to find f with even better (sub-linear) orbit dim growth.
"""

import numpy as np


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


def build_permutations(n):
    N = 2 ** n
    perm_a = np.array([apply_a_int(x, n) for x in range(N)], dtype=np.int32)
    perm_b = np.array([apply_b_int(x, n) for x in range(N)], dtype=np.int32)
    return perm_a, perm_b


def gaussian_elim_z2(rows, N):
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


def compute_orbit_dim_at_level(n, max_k, f_vec):
    N = 2 ** n
    perm_a, perm_b = build_permutations(n)
    inv_a = np.argsort(perm_a).astype(np.int32)
    inv_b = np.argsort(perm_b).astype(np.int32)
    generators = [perm_a, perm_b, inv_a, inv_b]

    identity = np.arange(N, dtype=np.int32)
    seen = {tuple(identity): True}
    current_layer = [identity]
    all_rows = [f_vec.astype(np.uint8)]

    dims = {}
    ball_sizes = {}
    ball_size = 1
    final_dim = gaussian_elim_z2(all_rows, N)

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
        final_dim = gaussian_elim_z2(all_rows, N)
        dims[k] = final_dim
        ball_sizes[k] = ball_size
        if not current_layer:
            for kk in range(k + 1, max_k + 1):
                dims[kk] = final_dim
                ball_sizes[kk] = ball_size
            break

    return dims, ball_sizes


def total_orbit_profile(max_k, max_level=10):
    """
    Compute total orbit dim = sum over levels of dim('last bit' at level n).
    Uses the ball size at the highest level computed as reference.
    """
    print(f"Computing total orbit dim profile, max_k={max_k}, levels 1..{max_level}")

    all_level_dims = {}
    ref_ball_sizes = None

    for n in range(1, max_level + 1):
        N = 2 ** n
        f_last = np.array([x & 1 for x in range(N)], dtype=np.uint8)  # last bit = LSB
        dims, ball_sizes = compute_orbit_dim_at_level(n, max_k, f_last)
        all_level_dims[n] = dims
        if ref_ball_sizes is None or max(ball_sizes.values()) > max(ref_ball_sizes.values()):
            ref_ball_sizes = ball_sizes
        final = dims[max_k]
        print(f"  Level {n:2d} (N={N:5d}): orbit_dim at k={max_k} = {final}")

    print(f"\nTotal orbit dim vs k:")
    print(f"{'k':>4} {'|B_k|':>12} {'total_dim':>12} {'ratio':>12}")
    for k in range(1, max_k + 1):
        total = sum(all_level_dims[n][k] for n in range(1, max_level + 1))
        bs = ref_ball_sizes[k]
        print(f"  {k:2d}  {bs:12d}  {total:12d}  {total/bs:12.6f}")

    return all_level_dims, ref_ball_sizes


def analyze_last_bit_recursion():
    """
    Understand why last bit has small orbit via the recursive structure.
    For a string v, last_bit(a(v)) and last_bit(b(v)) reduce to last_bit of shorter strings.
    """
    print("\n=== Recursive structure of last bit ===")
    print("ℓ(v) = last bit of v.")
    print("ℓ(a(0w)) = ℓ(0w) = ℓ(w)  [a fixes 0-strings]")
    print("ℓ(a(1w)) = ℓ(1·b(w)) = ℓ(b(w))")
    print("ℓ(b(0w)) = ℓ(1w) = ℓ(w)   [b(0w)=1w, last bit unchanged]")
    print("ℓ(b(1w)) = ℓ(0·a(w)) = ℓ(a(w))")
    print()
    print("So applying a or b to a length-n string:")
    print("  - if first bit is 0: ℓ doesn't change (both a,b reduce to ℓ(suffix))")
    print("  - if first bit is 1: ℓ reduces to ℓ after applying another generator to the suffix")
    print()
    print("After k applications, effect on last bit depends only on the 'carry chain'")
    print("of 1s from the start. Depth of effect = min(k, length of leading 1s block).")
    print()
    print("For a random string of length n, probability that all first k bits are 1 = 2^{-k}.")
    print("So only a 2^{-k} fraction of strings see 'deep' changes to last bit.")
    print("The orbit dim grows as O(k) because only O(k) distinct 'carry depths' matter.")


def try_other_candidates(max_k=10):
    """
    Try other candidate functions on the infinite tree and compare orbit dims.
    """
    n = 8
    N = 2 ** n
    perm_a, perm_b = build_permutations(n)

    print(f"\n=== Candidate functions at level n={n} ===")

    candidates = {
        "last_bit": np.array([x & 1 for x in range(N)], dtype=np.uint8),
        "xor_all_bits": np.array([bin(x).count('1') % 2 for x in range(N)], dtype=np.uint8),
        "bit[3]": np.array([(x >> 3) & 1 for x in range(N)], dtype=np.uint8),  # middle bit
        "last_two_xor": np.array([(x & 1) ^ ((x >> 1) & 1) for x in range(N)], dtype=np.uint8),
        "popcount_mod4": np.array([bin(x).count('1') % 4 // 2 for x in range(N)], dtype=np.uint8),
        # Thue-Morse like: f(x) = popcount(x) mod 2 -- same as xor_all_bits
        # Try: f = indicator of 'more 1s than 0s'
        "majority": np.array([1 if bin(x).count('1') > n // 2 else 0 for x in range(N)], dtype=np.uint8),
    }

    print(f"{'candidate':>20}", end="")
    for k in [2, 4, 6, 8, 10]:
        print(f"  k={k}", end="")
    print()

    for name, f_vec in candidates.items():
        dims, _ = compute_orbit_dim_at_level(n, max_k, f_vec)
        print(f"  {name:>20}", end="")
        for k in [2, 4, 6, 8, 10]:
            print(f"  {dims[k]:5d}", end="")
        print()


if __name__ == "__main__":
    # Main: total orbit dim for larger k
    all_dims, ball_sizes = total_orbit_profile(max_k=14, max_level=12)

    # Show why last bit works recursively
    analyze_last_bit_recursion()

    # Try other candidates
    try_other_candidates(max_k=10)

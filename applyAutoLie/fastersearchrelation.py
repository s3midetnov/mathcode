import random
from collections import defaultdict
from itertools import combinations

# Make sure this matches your actual filename
from free_lie_z2 import FreeNilpotentLieZ2, Elem


# ---------------------------------------------------------------------------
# Fast streaming search
# ---------------------------------------------------------------------------

def search_relations_fast(
        L: FreeNilpotentLieZ2,
        min_support: int = 2,
        max_support: int = 3,
        min_weight: int = 1,
        max_weight: int = 4,
        target_weight=None,
        max_results: int = 20,
        bucket_cap: int = 4,
        samples_per_x: int = 200,
):
    # 1. OPTIMIZATION: Pre-calculate basis weights and filter BEFORE generating combinations
    basis_weights = {i: L.basis[i].weight for i in range(L.n)}

    # We only want basis indices that don't exceed max_weight
    valid_basis_indices = [i for i in range(L.n) if basis_weights[i] <= max_weight]

    pool_data = []
    pool_idx = 0

    for k in range(max(1, min_support), max_support + 1):
        for comb in combinations(valid_basis_indices, k):
            # 2. OPTIMIZATION: Ensure at least one element meets the min_weight criteria
            if max(basis_weights[i] for i in comb) > min_weight:
                # Calculate integer bitmask for lightning-fast disjoint checks later
                mask = sum(1 << i for i in comb)
                e = Elem(L, frozenset(comb))

                # Store the element, its bitmask, and a unique integer ID
                pool_data.append((e, mask, pool_idx))
                pool_idx += 1

    # Bias toward larger supports (sorting by length of support descending)
    # Note: Removed random.shuffle(pool) because it instantly destroyed this sort
    pool_data.sort(key=lambda item: len(item[0].support), reverse=True)

    pool_size = len(pool_data)
    print(f"Pool size (support {min_support} to {max_support}): {pool_size}")

    target_indices = (
        frozenset(L._idx[id(e)] for e in L.layers[target_weight])
        if target_weight is not None else None
    )

    buckets = defaultdict(list)
    seen_pairs = set()
    results = []

    for i, (x, x_mask, x_id) in enumerate(pool_data):
        if i % 200 == 0:
            print(f"... {i}/{pool_size} | found: {len(results)}")

        # 3. OPTIMIZATION: Sample indices, not heavy objects
        sample_size = min(samples_per_x, pool_size)
        y_indices = random.sample(range(pool_size), sample_size)

        for j in y_indices:
            y, y_mask, y_id = pool_data[j]

            # 4. OPTIMIZATION: Fast integer tuple hashing instead of frozenset of frozensets
            pair_key = (x_id, y_id) if x_id < y_id else (y_id, x_id)
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            # 5. OPTIMIZATION: Bitwise disjoint check (SKIP TRIVIAL PADDING)
            if x_mask & y_mask != 0:
                continue

            b = L.bracket(x, y)
            if not b:
                continue

            if target_indices is not None and not b.support.issubset(target_indices):
                continue

            bucket = buckets[b.support]

            for (x2, y2, x2_mask, y2_mask) in bucket:
                # Prevent matching identical brackets or re-arrangements using fast masks
                if x_mask == x2_mask or x_mask == y2_mask or y_mask == x2_mask or y_mask == y2_mask:
                    continue

                # Ensure the matched pair ALSO doesn't contain trivial Z_2 padding
                if x2_mask & y2_mask != 0:
                    continue

                # Record the genuine relation
                results.append((x, y, x2, y2))

                print("\nFOUND RELATION:")
                print(f"[{x}] · [{y}]")
                print(f"= [{x2}] · [{y2}]")
                print(f"value: {Elem(L, b.support)}\n")

                if len(results) >= max_results:
                    return results

            if len(bucket) < bucket_cap:
                # Store masks in the bucket as well so we don't have to recompute
                bucket.append((x, y, x_mask, y_mask))

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Parameters
    CLASS = 10
    MIN_SUPPORT = 2
    MAX_SUPPORT = 4
    TARGET_WEIGHT = None
    MAX_RESULTS = 40
    MAX_SUMMAND_WEIGHT = 5
    MIN_SUMMAND_WEIGHT = 1

    L = FreeNilpotentLieZ2(c=CLASS)
    print(L)
    print()

    results = search_relations_fast(
        L,
        min_support=MIN_SUPPORT,
        max_support=MAX_SUPPORT,
        min_weight=MIN_SUMMAND_WEIGHT,
        max_weight=MAX_SUMMAND_WEIGHT,
        target_weight=TARGET_WEIGHT,
        max_results=MAX_RESULTS,
    )

    print(f"\nTotal found: {len(results)}")
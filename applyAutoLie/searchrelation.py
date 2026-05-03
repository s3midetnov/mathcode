from itertools import combinations
from collections import defaultdict
from free_lie_z2 import FreeNilpotentLieZ2, Elem


def all_elements_min_support(L: FreeNilpotentLieZ2, min_support: int = 2) -> list[Elem]:
    """All non-zero elements of L with support >= min_support.
    With min_support=2 this is 2^n - 1 - n elements (excluding zero and basis vectors).
    """
    return [
        Elem(L, frozenset(i for i in range(L.n) if mask >> i & 1))
        for mask in range(1, 1 << L.n)
        if bin(mask).count("1") >= min_support
    ]


def search_relations(
    L: FreeNilpotentLieZ2,
    min_support: int = 2,
    target_weight = None,
) -> list[tuple[Elem, Elem, Elem, Elem]]:
    """Find all relations  [x,y] = [z,w]  with [x,y] != 0,
    where all four of x,y,z,w have support >= min_support,
    and the two pairs are genuinely distinct (not a permutation).

    If target_weight is given, only keep relations where [x,y] is a
    non-zero element supported entirely on that weight layer.
    """
    pool = all_elements_min_support(L, min_support)
    print(f"Pool size (support >= {min_support}): {len(pool)} elements")

    target_indices = (
        frozenset(L._idx[id(e)] for e in L.layers[target_weight])
        if target_weight is not None else None
    )

    # Map: bracket_value (frozenset) -> list of unordered pairs {x, y}
    by_value: dict[frozenset, list[tuple[Elem, Elem]]] = defaultdict(list)
    seen_pair: set[frozenset] = set()

    total = len(pool)
    for i, x in enumerate(pool):
        if i % 500 == 0:
            print(f"  ... processing element {i}/{total}, "
                  f"buckets so far: {len(by_value)}")
        for y in pool[i + 1:]:
            b = L.bracket(x, y)
            if not b:
                continue
            if target_indices is not None and not b.support.issubset(target_indices):
                continue
            key = frozenset({x.support, y.support})
            if key in seen_pair:
                continue
            seen_pair.add(key)
            by_value[b.support].append((x, y))

    print(f"\nDistinct (x,y) pairs with non-zero bracket: "
          f"{sum(len(v) for v in by_value.values())}")
    print(f"Distinct bracket values hit: {len(by_value)}\n")

    results = []
    for bval, xy_list in by_value.items():
        if len(xy_list) < 2:
            continue
        belem = Elem(L, bval)
        for (x1, y1), (x2, y2) in combinations(xy_list, 2):
            if frozenset({x1.support, y1.support}) == frozenset({x2.support, y2.support}):
                continue
            results.append((x1, y1, x2, y2))

    print(f"Total relations found: {len(results)}\n")

    # Print sorted by 'messiness': total support size of all four elements
    results.sort(key=lambda t: sum(len(e.support) for e in t), reverse=True)
    for x1, y1, x2, y2 in results:
        belem = Elem(L, L.bracket(x1, y1).support)
        print(f"  [{x1}]")
        print(f"· [{y1}]")
        print(f"= [{x2}]")
        print(f"· [{y2}]")
        print(f"  value: {belem}")
        print()

    return results


if __name__ == "__main__":
    L = FreeNilpotentLieZ2(c=5)
    print(L)
    print()

    # All relations, no weight filter on the result, all 4 args must be sums
    rels = search_relations(L, min_support=2)

    # Or: restrict the bracket result to land in weight 5
    # rels = search_relations(L, min_support=2, target_weight=5)
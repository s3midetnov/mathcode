import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'commutators'))
from hall_basis import compute_hall_basis


class FreeNilpotentLieZ2:
    """Free nilpotent Lie algebra of class `c` on 2 generators over Z/2.

    Basis: Hall commutators of weight <= c.
    Coefficients: Z/2 = {0, 1}.
    """

    def __init__(self, c: int):
        self.c = c
        all_elems, layers = compute_hall_basis(c)
        self.basis = all_elems   # list[HallElem], Hall order
        self.layers = layers     # weight -> [HallElem]
        self.n = len(all_elems)

        self._idx = {id(e): i for i, e in enumerate(all_elems)}

        # (left_index, right_index) -> index of the corresponding Hall element
        self._hall_lookup: dict[tuple[int, int], int] = {}
        for i, e in enumerate(all_elems):
            if e.left is not None:
                li = self._idx[id(e.left)]
                ri = self._idx[id(e.right)]
                self._hall_lookup[(li, ri)] = i

        self._cache: dict[tuple[int, int], frozenset] = {}

    # ------------------------------------------------------------------
    # Bracket on basis indices
    # ------------------------------------------------------------------

    def _bracket(self, i: int, j: int) -> frozenset:
        """[basis[i], basis[j]] with i > j. Returns support as frozenset of indices."""
        key = (i, j)
        if key in self._cache:
            return self._cache[key]

        hi, hj = self.basis[i], self.basis[j]

        if hi.weight + hj.weight > self.c:
            result = frozenset()
        elif hi.left is None:
            # hi is a generator: [gen_i, gen_j] is a Hall element by definition
            k = self._hall_lookup.get((i, j))
            result = frozenset({k}) if k is not None else frozenset()
        else:
            p = self._idx[id(hi.left)]
            q = self._idx[id(hi.right)]
            if q <= j:
                # Hall condition satisfied: [[p,q], j] is itself a Hall element
                k = self._hall_lookup.get((i, j))
                result = frozenset({k}) if k is not None else frozenset()
            else:
                # Jacobi (char 2): [[p,q], j] = [p,[q,j]] + [q,[p,j]]
                result = (
                    self._bracket_linear(p, self._bracket_sym(q, j))
                    ^ self._bracket_linear(q, self._bracket_sym(p, j))
                )

        self._cache[key] = result
        return result

    def _bracket_sym(self, i: int, j: int) -> frozenset:
        """[basis[i], basis[j]] for any i != j.  Over Z/2: [x,y] = [y,x]."""
        if i == j:
            return frozenset()
        return self._bracket(i, j) if i > j else self._bracket(j, i)

    def _bracket_linear(self, i: int, support: frozenset) -> frozenset:
        """[basis[i], x] where x has given support. Extends linearly over Z/2."""
        result = frozenset()
        for k in support:
            result ^= self._bracket_sym(i, k)
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def zero(self) -> "Elem":
        return Elem(self, frozenset())

    def gen(self, name: str) -> "Elem":
        for i, e in enumerate(self.basis):
            if e.label == name:
                return Elem(self, frozenset({i}))
        raise KeyError(name)

    def basis_element(self, i: int) -> "Elem":
        return Elem(self, frozenset({i}))

    def bracket(self, x: "Elem", y: "Elem") -> "Elem":
        result = frozenset()
        for i in x.support:
            for j in y.support:
                result ^= self._bracket_sym(i, j)
        return Elem(self, result)

    def all_elements(self):
        """Yield all 2^n elements (only feasible for small n)."""
        for mask in range(1 << self.n):
            yield Elem(self, frozenset(i for i in range(self.n) if mask >> i & 1))

    def __repr__(self) -> str:
        lines = [f"FreeNilpotentLieZ2(c={self.c}), dim={self.n}"]
        for w in range(1, self.c + 1):
            elems = ", ".join(e.label for e in self.layers[w])
            lines.append(f"  weight {w}: {elems}")
        return "\n".join(lines)


class Elem:
    """Element of FreeNilpotentLieZ2. Stored as a frozenset of basis indices."""

    __slots__ = ("alg", "support")

    def __init__(self, alg: FreeNilpotentLieZ2, support):
        self.alg = alg
        self.support = frozenset(support)

    def __add__(self, other: "Elem") -> "Elem":
        return Elem(self.alg, self.support ^ other.support)

    def __eq__(self, other) -> bool:
        return isinstance(other, Elem) and self.support == other.support

    def __hash__(self) -> int:
        return hash(self.support)

    def __bool__(self) -> bool:
        return bool(self.support)

    def __repr__(self) -> str:
        if not self.support:
            return "0"
        return " + ".join(self.alg.basis[i].label for i in sorted(self.support))


# ---------------------------------------------------------------------------
# Ideal generation
# ---------------------------------------------------------------------------

def _z2_basis(L: FreeNilpotentLieZ2, elems: list) -> list:
    """Z/2 row-reduce `elems` and return a basis for their span."""
    pivots: dict[int, frozenset] = {}   # leading_index -> frozenset
    for e in elems:
        v = set(e.support)
        for p in sorted(pivots):        # reduce against existing pivots in order
            if p in v:
                v ^= pivots[p]
        if v:
            pivots[min(v)] = frozenset(v)
    return [Elem(L, v) for _, v in sorted(pivots.items())]


def ideal_basis(L: FreeNilpotentLieZ2, generators: list) -> list:
    """Return a Z/2 basis for the ideal generated by `generators`.

    Algorithm:
    1. BFS: for each element r in the ideal, bracket r with each generator
       (ad_a and ad_b) and enqueue the result if not yet seen. Repeat until
       no new elements appear. By nilpotency this always terminates.
    2. Z/2 row-reduce the collected spanning set to extract a basis.

    Correctness: [r1+r2, x] = [r1,x] + [r2,x], so the Z/2-span of all
    right-adjoint sequences applied to the initial generators is already
    closed under bracketing with all of L (by bilinearity + Jacobi induction
    on weight), hence equals the ideal.
    """
    adj_gens = [L.gen("a"), L.gen("b")]

    spanning: list = []
    seen: set[frozenset] = set()
    queue = [e for e in generators if e]

    while queue:
        r = queue.pop(0)
        if r.support in seen:
            continue
        seen.add(r.support)
        spanning.append(r)
        for g in adj_gens:
            rg = L.bracket(r, g)
            if rg and rg.support not in seen:
                queue.append(rg)

    return _z2_basis(L, spanning)


def rank_R_mod_RF(L: FreeNilpotentLieZ2, generators: list) -> int:
    """Rank of R / [R, F] as a Z/2-vector space.

    R   = ideal generated by `generators`.
    [R,F] = span{ [r, f] : r in R, f in F=L } — a subspace of R (R is an ideal).
    Rank = dim(R) - dim([R,F]).

    Interpretation: this is the minimum number of generators for R as an ideal
    (the F-module analogue of dim M/mM for modules over local rings).
    """
    R_basis = ideal_basis(L, generators)

    RF_span = []
    for r in R_basis:
        for j in range(L.n):
            br = L.bracket(r, L.basis_element(j))
            if br:
                RF_span.append(br)

    RF_basis = _z2_basis(L, RF_span)
    return len(R_basis) - len(RF_basis)


if __name__ == "__main__":
    L = FreeNilpotentLieZ2(c=8)
    print(L)
    print()

    a = L.gen("a")
    b = L.gen("b")

    print(f"[b, a]         = {L.bracket(b, a)}")
    print(f"[a, b]         = {L.bracket(a, b)}")
    print(f"[[b,a], a]     = {L.bracket(L.bracket(b, a), a)}")
    print(f"[[b,a], b]     = {L.bracket(L.bracket(b, a), b)}")
    print(f"[a, a]         = {L.bracket(a, a)}")
    print(f"Jacobi a,b,a:  = {L.bracket(L.bracket(a,b),a) + L.bracket(L.bracket(b,a),a) + L.bracket(L.bracket(a,a),b)}")
    print(f"check [a, b, a, b] + [a, b, b, a]:  = {L.bracket(L.bracket(L.bracket(a,b),a), b) + L.bracket(L.bracket(L.bracket(a,b),b), a)}")



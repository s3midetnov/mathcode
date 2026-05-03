"""
Generate the Hall basis for F2 = <a, b> up to a given weight and write it
as a GAP-parsable file.

Hall basis conditions for [u, v] to be basic:
  1. u and v are basic commutators
  2. u > v  (Hall order: higher weight is larger; within same weight, by insertion order)
  3. If u = [r, s] then s <= v  (right-factor of u is no larger than v)

No "disjoint letters" condition — both a and b may appear in the same commutator.
"""


class HallElem:
    """A basic commutator in the Hall basis of F2."""

    def __init__(self, label, gap_expr, weight, order_index, left=None, right=None):
        self.label = label          # human-readable string, e.g. "[b,a]"
        self.gap_expr = gap_expr    # GAP expression, e.g. "Comm(F.2,F.1)"
        self.weight = weight
        self.order_index = order_index  # position in the global list (determines order within weight)
        self.left = left            # HallElem: u  in [u,v], or None for letters
        self.right = right          # HallElem: v  in [u,v], or None for letters


def _gt(x, y):
    """True if x > y in the Hall order."""
    if x.weight != y.weight:
        return x.weight > y.weight
    return x.order_index > y.order_index


def _lte(x, y):
    """True if x <= y in the Hall order."""
    return not _gt(x, y)


def compute_hall_basis(k):
    """
    Return a list of all HallElem objects of weight <= k, in Hall order.
    Generators: a = F.1 (index 0), b = F.2 (index 1), so a < b.
    """
    all_elems = []   # master list in order; order_index = position here
    layers = {}      # weight -> [HallElem, ...]

    # Weight 1: a < b
    a = HallElem("a", "F.1", weight=1, order_index=0)
    b = HallElem("b", "F.2", weight=1, order_index=1)
    all_elems = [a, b]
    layers[1] = [a, b]

    for w in range(2, k + 1):
        new_elems = []
        for wu in range(1, w):
            wv = w - wu
            for u in layers[wu]:
                for v in layers[wv]:
                    if not _gt(u, v):
                        continue
                    # Hall condition: if u = [r, s], then s <= v
                    if u.left is not None and _gt(u.right, v):
                        continue
                    label = f"[{u.label},{v.label}]"
                    gap_expr = f"Comm({u.gap_expr},{v.gap_expr})"
                    elem = HallElem(
                        label, gap_expr, weight=w,
                        order_index=len(all_elems) + len(new_elems),
                        left=u, right=v,
                    )
                    new_elems.append(elem)

        layers[w] = new_elems
        all_elems.extend(new_elems)

    return all_elems, layers


def write_hall_basis(k, filename=None):
    """
    Compute all Hall basis elements of weight <= k for F2 = <a,b> and write
    them to a GAP file.

    The file defines a list `hallBasis` of records:
        rec( index := i, weight := w, label := "...", elt := <GAP expr> )

    F must already be defined in GAP as: F := FreeGroup("a","b");;

    Parameters
    ----------
    k        : int  — maximum weight
    filename : str  — output path; defaults to "hall_basis_<k>.g"
    """
    if filename is None:
        filename = f"hall_basis_{k}.g"

    all_elems, layers = compute_hall_basis(k)

    with open(filename, "w") as f:
        f.write(f"# Hall basis for F2 = <a,b>, weight <= {k}\n")
        f.write("# Requires: F := FreeGroup(\"a\",\"b\");;\n")
        f.write("#\n")
        f.write("# hallBasis[i] is a record with fields:\n")
        f.write("#   index  -- position in the Hall order (1-based)\n")
        f.write("#   weight -- weight of the basic commutator\n")
        f.write("#   label  -- string name, e.g. \"[b,a]\"\n")
        f.write("#   elt    -- the element of F as a GAP object\n")
        f.write("\n")
        f.write("hallBasis := [\n")

        for i, elem in enumerate(all_elems):
            comma = "," if i < len(all_elems) - 1 else ""
            f.write(
                f"    rec( index := {i+1}, weight := {elem.weight},"
                f' label := "{elem.label}", elt := {elem.gap_expr} ){comma}\n'
            )

        f.write("];\n")

    # Print a summary by weight
    for w in range(1, k + 1):
        print(f"Weight {w}: {len(layers[w])} basic commutator(s): "
              + ", ".join(e.label for e in layers[w]))

    print(f"\nTotal: {len(all_elems)} basic commutators written to '{filename}'")
    return all_elems, layers


if __name__ == "__main__":
    import sys
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    write_hall_basis(k)

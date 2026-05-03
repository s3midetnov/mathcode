"""
Lower Central Series Checker via Magnus Expansion
==================================================
Checks whether a word w in the free group F_2 = <x, y> lies in γ_k(F_2).

Algorithm: Magnus expansion
  Map  x  ↦  1 + X
       y  ↦  1 + Y
       X  ↦  (1+X)^{-1} = 1 - X + X² - X³ + ...   (truncated)
       Y  ↦  (1+Y)^{-1} = 1 - Y + Y² - Y³ + ...   (truncated)
  in the ring of non-commutative polynomials Z<X,Y>, truncated at degree k.

  Theorem (Magnus 1939):
    w ∈ γ_k(F_2)  ⟺  φ(w) ≡ 1  (mod degree k)
  i.e. all homogeneous terms of degree 1, 2, ..., k-1 vanish.

Word syntax:
  x, y          generators
  X, Y          inverses  (x⁻¹, y⁻¹)
  [u,v]         commutator  u·v·u⁻¹·v⁻¹
  *             explicit multiplication (optional)
  x^3, Y^-2    integer powers

Examples:
  [x,y]          → lies in γ_2 but not γ_3
  [[x,y],x]      → lies in γ_3 but not γ_4
  x*y*X*Y        → same as [x,y]
  [x,y]^2        → lies in γ_2 but not γ_3
"""

from collections import defaultdict
from itertools import product as iproduct


# ---------------------------------------------------------------------------
# Non-commutative truncated polynomial ring  Z<X, Y>
# ---------------------------------------------------------------------------
# A polynomial is a dict  {monomial: coefficient}
# where a monomial is a tuple of 0/1  (0 = X variable, 1 = Y variable).
# We drop all monomials of degree >= maxdeg and all zero coefficients.

VARS = ('X', 'Y')   # display names for the two non-commuting variables

def _clean(poly):
    return {m: c for m, c in poly.items() if c != 0}

def poly_add(p, q):
    r = dict(p)
    for m, c in q.items():
        r[m] = r.get(m, 0) + c
    return _clean(r)

def poly_scale(p, s):
    return _clean({m: c * s for m, c in p.items()})

def poly_mul(p, q, maxdeg):
    r = {}
    for (m1, c1), (m2, c2) in iproduct(p.items(), q.items()):
        m = m1 + m2
        if len(m) <= maxdeg:
            r[m] = r.get(m, 0) + c1 * c2
    return _clean(r)

def poly_one():
    return {(): 1}          # the constant polynomial 1

def poly_gen(var_idx, maxdeg):
    """Return 1 + X_{var_idx}, truncated at maxdeg."""
    p = {(): 1}
    if maxdeg >= 1:
        p[(var_idx,)] = 1
    return p

def poly_gen_inv(var_idx, maxdeg):
    """Return (1 + X_{var_idx})^{-1} = sum_{k=0}^{maxdeg} (-X)^k, truncated."""
    result = {}
    for k in range(maxdeg + 1):
        mono = (var_idx,) * k
        result[mono] = result.get(mono, 0) + ((-1) ** k)
    return _clean(result)

def poly_inv(p, maxdeg):
    """Invert an arbitrary polynomial with constant term ±1."""
    const = p.get((), 0)
    if const not in (1, -1):
        raise ValueError(f"Polynomial not invertible (constant term = {const})")
    sign = const
    # Work with sign*p so constant = 1, then use (1+A)^{-1} = sum (-A)^k
    # A = sign*p - 1
    norm = poly_scale(p, sign)
    A = dict(norm)
    A[()] = A.get((), 0) - 1
    A = _clean(A)

    result = poly_one()
    Apow = poly_one()
    for k in range(1, maxdeg + 1):
        Apow = poly_mul(Apow, A, maxdeg)
        contrib = poly_scale(Apow, (-1) ** k)
        result = poly_add(result, contrib)
    return poly_scale(result, sign)


# ---------------------------------------------------------------------------
# Word parser
# ---------------------------------------------------------------------------
# Produces a list of (var_idx, exponent) pairs, var_idx ∈ {0,1}, exp ∈ Z\{0}.

def parse_word(s):
    """
    Parse a word string into a list of (var_idx, exp) letters.
    Handles: x, y, X, Y, [u,v], *, x^n, spaces.
    """
    s = s.strip()
    letters = []
    _parse_seq(s, 0, len(s), letters)
    return letters

def _parse_seq(s, lo, hi, out):
    """Parse s[lo:hi] as a sequence of atoms, appending to out."""
    i = lo
    while i < hi:
        c = s[i]
        if c in (' ', '*'):
            i += 1
            continue
        if c == '[':
            j, inner = _match_bracket(s, i, hi)
            atom_letters = _parse_commutator(inner)
            # check for power after ]
            j, exp = _try_power(s, j, hi)
            if exp >= 0:
                out.extend(atom_letters * exp)
            else:
                inv = _invert_letters(atom_letters)
                out.extend(inv * (-exp))
            i = j
        elif c.lower() in ('x', 'y'):
            var = 0 if c.lower() == 'x' else 1
            base_exp = 1 if c.islower() else -1
            i += 1
            i, pw = _try_power(s, i, hi)
            exp = base_exp * pw
            if exp != 0:
                out.append((var, exp))
        else:
            i += 1   # skip unknown chars

def _parse_commutator(inner):
    """Parse [u,v] inner content, return letters for u v u^{-1} v^{-1}."""
    split = _find_comma(inner)
    if split < 0:
        raise ValueError(f"No comma found in commutator [{inner}]")
    u_letters, v_letters = [], []
    _parse_seq(inner, 0, split, u_letters)
    _parse_seq(inner, split + 1, len(inner), v_letters)
    return u_letters + v_letters + _invert_letters(u_letters) + _invert_letters(v_letters)

def _invert_letters(letters):
    return [(v, -e) for (v, e) in reversed(letters)]

def _match_bracket(s, i, hi):
    """i points to '['. Returns (end_pos, inner_string)."""
    depth = 0
    j = i
    while j < hi:
        if s[j] == '[': depth += 1
        elif s[j] == ']': depth -= 1
        if depth == 0:
            return j + 1, s[i + 1:j]
        j += 1
    raise ValueError("Unmatched '['")

def _find_comma(s):
    """Find top-level comma in s."""
    depth = 0
    for i, c in enumerate(s):
        if c == '[': depth += 1
        elif c == ']': depth -= 1
        elif c == ',' and depth == 0:
            return i
    return -1

def _try_power(s, i, hi):
    """If s[i] == '^', parse integer power. Returns (new_i, power)."""
    if i < hi and s[i] == '^':
        i += 1
        neg = False
        if i < hi and s[i] == '-':
            neg = True; i += 1
        j = i
        while j < hi and s[j].isdigit():
            j += 1
        if j == i:
            raise ValueError("Expected integer after '^'")
        pw = int(s[i:j]) * (-1 if neg else 1)
        return j, pw
    return i, 1


# ---------------------------------------------------------------------------
# Magnus expansion
# ---------------------------------------------------------------------------

def magnus(letters, maxdeg):
    """
    Compute φ(w) in Z<X,Y> truncated at degree maxdeg.
    letters: list of (var_idx, exp)
    """
    result = poly_one()
    for (var, exp) in letters:
        if exp > 0:
            factor = poly_gen(var, maxdeg)
            for _ in range(exp):
                result = poly_mul(result, factor, maxdeg)
        else:
            factor = poly_gen_inv(var, maxdeg)
            for _ in range(-exp):
                result = poly_mul(result, factor, maxdeg)
    return result


# ---------------------------------------------------------------------------
# LCS membership test
# ---------------------------------------------------------------------------

def check_lcs(word_str, k):
    """
    Check whether the word lies in γ_k(F_2).

    Returns a dict with:
      'in_lcs'    : bool
      'poly'      : the Magnus expansion (truncated at degree k)
      'bad_terms' : terms of degree < k that should be 0 (or constant ≠ 1)
      'word_str'  : original input
      'k'         : the tested level
    """
    if k < 1:
        raise ValueError("k must be a positive integer")
    letters = parse_word(word_str)
    poly = magnus(letters, k - 1)   # only need degrees 0 .. k-1

    bad = {}
    for mono, coeff in poly.items():
        deg = len(mono)
        if deg == 0:
            if coeff != 1:
                bad[mono] = coeff
        else:
            bad[mono] = coeff

    return {
        'in_lcs': len(bad) == 0,
        'poly': poly,
        'bad_terms': bad,
        'word_str': word_str,
        'k': k,
    }


# ---------------------------------------------------------------------------
# Pretty printing
# ---------------------------------------------------------------------------

def mono_str(mono):
    if not mono:
        return '1'
    return '·'.join(VARS[v] for v in mono)

def poly_str(poly):
    if not poly:
        return '0'
    terms = sorted(poly.items(), key=lambda kv: (len(kv[0]), kv[0]))
    parts = []
    for mono, c in terms:
        ms = mono_str(mono)
        if c == 1:
            parts.append(ms)
        elif c == -1:
            parts.append(f'-{ms}')
        else:
            parts.append(f'{c}·{ms}')
    return ' + '.join(parts).replace('+ -', '- ')

def print_result(res):
    k = res['k']
    w = res['word_str']
    verdict = "YES  ✓" if res['in_lcs'] else "NO   ✗"

    print(f"\n{'='*60}")
    print(f"  Word : {w}")
    print(f"  k    : {k}   (checking w ∈ γ_{k}(F₂))")
    print(f"{'─'*60}")

    poly = res['poly']
    by_deg = defaultdict(dict)
    for mono, c in poly.items():
        by_deg[len(mono)][mono] = c

    print("  Magnus expansion φ(w)  [degrees 0 to k-1]:")
    for d in range(k):
        p = by_deg.get(d, {})
        s = poly_str(p) if p else '0'
        marker = ''
        if d == 0:
            marker = '  ← must equal 1' if p.get((), 0) != 1 else '  ✓'
        else:
            marker = '  ← must be 0' if p else '  ✓'
        print(f"    deg {d}: {s}{marker}")

    print(f"{'─'*60}")
    print(f"  Result: w ∈ γ_{k}(F₂) ?  {verdict}")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# CLI / interactive demo
# ---------------------------------------------------------------------------

def run_examples():
    examples = [
        ("[x,y]",       1, "trivially in γ_1 (everything is)"),
        ("[x,y]",       2, "commutator lies in γ_2"),
        ("[x,y]",       3, "commutator does NOT lie in γ_3"),
        ("[[x,y],x]",   3, "double commutator lies in γ_3"),
        ("[[x,y],x]",   4, "double commutator does NOT lie in γ_4"),
        ("x*y*X*Y",     2, "x·y·x⁻¹·y⁻¹ = [x,y] ∈ γ_2"),
        ("x",           2, "generator does NOT lie in γ_2"),
        ("[x,y]^2",     2, "square of commutator in γ_2"),
        ("[[x,y],[x,Y]]", 4, "product of commutators in γ_4?"),
    ]

    print(__doc__)
    print("\nRunning built-in examples")
    print("=" * 60)
    for word, k, note in examples:
        print(f"\n  [{note}]")
        res = check_lcs(word, k)
        print_result(res)

def interactive():
    print("\nInteractive mode  (type 'quit' to exit)")
    print("Generators: x, y   |   Inverses: X, Y")
    print("Commutator syntax: [u,v]   |   Power: x^3")
    while True:
        try:
            w = input("\nEnter word  (or 'quit'): ").strip()
            if w.lower() in ('quit', 'q', 'exit'):
                break
            if not w:
                continue
            k = input("Enter k (LCS level): ").strip()
            k = int(k)
            res = check_lcs(w, k)
            print_result(res)
        except (ValueError, KeyboardInterrupt) as e:
            print(f"  Error: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 3:
        # Direct invocation: python lcs_checker.py "[x,y]" 2
        word_arg = sys.argv[1]
        k_arg = int(sys.argv[2])
        print_result(check_lcs(word_arg, k_arg))
    elif len(sys.argv) == 1:
        run_examples()
        interactive()
    else:
        print("Usage:")
        print("  python lcs_checker.py                   # run examples + interactive")
        print("  python lcs_checker.py \"[x,y]\" 3        # single check")
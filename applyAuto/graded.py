"""
Free Abelian Rank Checker in γₙ/γₙ₊₁
======================================
Given k words w₁,…,wₖ in F₂ = ⟨x,y⟩, all lying in γₙ(F₂),
checks whether they generate a free abelian subgroup of rank k
in the graded piece γₙ(F₂)/γₙ₊₁(F₂).

Theory
------
The Magnus expansion φ: F → ℤ⟨⟨X,Y⟩⟩ is injective and satisfies
  φ(γₙ) ≡ 1  (mod degree n)
For w ∈ γₙ, the degree-n part of φ(w) − 1 is a well-defined
noncommutative homogeneous polynomial of degree n, and the map
  w ↦ deg-n part of φ(w)−1
induces a group homomorphism
  γₙ/γₙ₊₁  →  (degree-n part of ℤ⟨X,Y⟩)  ≅  ℤ^{2^n}
which is injective (this follows from the Magnus–Witt theorem).

So w₁,…,wₖ generate a free abelian subgroup of rank k in γₙ/γₙ₊₁
⟺  their degree-n Magnus vectors are ℤ-linearly independent
⟺  the k×(2^n) integer matrix M has rank k over ℤ
⟺  Smith normal form of M has exactly k nonzero diagonal entries.

Note: the ambient free abelian group γₙ/γₙ₊₁ has rank given by the
necklace polynomial  (1/n)·Σ_{d|n} μ(n/d)·2^d,  which is < 2^n in
general (the Lie subalgebra is a proper submodule). The rank over ℤ
of the matrix nevertheless correctly detects linear independence
inside the full degree-n module, which suffices.
"""

from itertools import product as iproduct
from lcs_checker import parse_word, magnus, check_lcs, print_result, VARS


# ---------------------------------------------------------------------------
# Smith Normal Form over ℤ  (elementary row/col operations)
# Works on a list-of-lists matrix, returns diagonal of SNF.
# ---------------------------------------------------------------------------

def smith_normal_form(M):
    """
    Compute Smith Normal Form of integer matrix M (list of lists).
    Returns the list of nonzero diagonal entries of the SNF.
    """
    # Work on a copy
    A = [row[:] for row in M]
    rows, cols = len(A), len(A[0]) if A else 0

    def swap_rows(i, j):
        A[i], A[j] = A[j], A[i]

    def swap_cols(i, j):
        for row in A:
            row[i], row[j] = row[j], row[i]

    def add_row(i, j, factor):   # row[i] += factor * row[j]
        for c in range(cols):
            A[i][c] += factor * A[j][c]

    def add_col(i, j, factor):   # col[i] += factor * col[j]
        for r in range(rows):
            A[r][i] += factor * A[r][j]

    def negate_row(i):
        for c in range(cols):
            A[i][c] = -A[i][c]

    pivot = 0
    for col in range(cols):
        if pivot >= rows:
            break
        # Find pivot: any nonzero in A[pivot:, col:]
        # Standard SNF: iterate diagonally
        pass

    # Proper diagonal SNF
    diag = []
    pivot = 0
    for step in range(min(rows, cols)):
        # Find smallest nonzero in submatrix A[step:, step:]
        while True:
            # Find any nonzero
            found = False
            for r in range(step, rows):
                for c in range(step, cols):
                    if A[r][c] != 0:
                        found = True
                        break
                if found:
                    break
            if not found:
                break

            # Move smallest absolute nonzero to (step, step)
            best = None
            for r in range(step, rows):
                for c in range(step, cols):
                    if A[r][c] != 0:
                        if best is None or abs(A[r][c]) < abs(best[2]):
                            best = (r, c, A[r][c])
            br, bc, _ = best
            swap_rows(step, br)
            swap_cols(step, bc)

            # Make pivot positive
            if A[step][step] < 0:
                negate_row(step)

            # Eliminate column
            changed = False
            for r in range(step, rows):
                if r == step:
                    continue
                if A[r][step] != 0:
                    q = A[r][step] // A[step][step]
                    add_row(r, step, -q)
                    if A[r][step] != 0:
                        changed = True

            # Eliminate row
            for c in range(step, cols):
                if c == step:
                    continue
                if A[step][c] != 0:
                    q = A[step][c] // A[step][step]
                    add_col(c, step, -q)
                    if A[step][c] != 0:
                        changed = True

            if not changed:
                # Check divisibility condition for true SNF
                # (ensure pivot divides all remaining entries)
                all_div = all(
                    A[r][c] % A[step][step] == 0
                    for r in range(step, rows)
                    for c in range(step, cols)
                )
                if all_div:
                    break
                # Otherwise add a bad row to pivot row and continue
                for r in range(step + 1, rows):
                    if any(A[r][c] % A[step][step] != 0 for c in range(step, cols)):
                        add_row(step, r, 1)
                        break

        if A[step][step] == 0:
            break
        diag.append(A[step][step])
        pivot += 1

    return diag


def matrix_rank_Z(M):
    """Rank of integer matrix over ℤ (= over ℚ = number of nonzero SNF diagonals)."""
    return len(smith_normal_form(M))


# ---------------------------------------------------------------------------
# Degree-n monomials
# ---------------------------------------------------------------------------

def monomials_of_degree(n, num_vars=2):
    """All monomials of degree n in num_vars non-commuting variables, as tuples."""
    return list(iproduct(range(num_vars), repeat=n))


# ---------------------------------------------------------------------------
# Extract degree-n vector from Magnus expansion
# ---------------------------------------------------------------------------

def degree_n_vector(word_str, n):
    """
    Parse word, compute Magnus expansion truncated at degree n,
    return the degree-n homogeneous part of φ(w)−1 as an integer vector
    (coordinates w.r.t. the ordered monomial basis).
    """
    letters = parse_word(word_str)
    poly = magnus(letters, n)
    basis = monomials_of_degree(n)
    return [poly.get(m, 0) for m in basis]


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def check_free_abelian_rank(words, n, verbose=True):
    """
    Given a list of word strings and LCS level n, check whether the words
    (assumed to lie in γₙ) generate a free abelian subgroup of rank len(words)
    in γₙ/γₙ₊₁.

    Returns dict with:
      'rank'         : actual ℤ-rank of the degree-n Magnus vectors
      'expected_rank': k = len(words)
      'is_free_rank_k': bool
      'matrix'       : the k × 2^n integer matrix
      'snf_diag'     : Smith normal form diagonal
      'basis_monomials': ordered monomial basis
      'not_in_gamma_n': list of words NOT lying in γₙ (prerequisite check)
    """
    k = len(words)
    basis = monomials_of_degree(n)

    # Prerequisite: each word must lie in γₙ
    not_in = []
    for w in words:
        res = check_lcs(w, n)
        if not res['in_lcs']:
            not_in.append(w)

    # Build matrix: row i = degree-n vector of wᵢ
    matrix = []
    vectors = []
    for w in words:
        v = degree_n_vector(w, n)
        vectors.append(v)
        matrix.append(v)

    snf = smith_normal_form([row[:] for row in matrix]) if matrix else []
    rank = len(snf)

    result = {
        'rank': rank,
        'expected_rank': k,
        'is_free_rank_k': (rank == k) and len(not_in) == 0,
        'matrix': matrix,
        'snf_diag': snf,
        'basis_monomials': basis,
        'not_in_gamma_n': not_in,
        'words': words,
        'n': n,
        'vectors': vectors,
    }

    if verbose:
        print_rank_result(result)

    return result


# ---------------------------------------------------------------------------
# Pretty printing
# ---------------------------------------------------------------------------

def mono_str(mono):
    if not mono:
        return '1'
    return '·'.join(VARS[v] for v in mono)

def print_rank_result(res):
    n = res['n']
    words = res['words']
    k = res['expected_rank']
    basis = res['basis_monomials']

    print(f"\n{'='*65}")
    print(f"  Checking: do these {k} word(s) generate a free abelian")
    print(f"  subgroup of rank {k} in  γ_{n}(F₂) / γ_{n+1}(F₂) ?")
    print(f"{'─'*65}")

    # Prerequisite check
    if res['not_in_gamma_n']:
        print(f"  ⚠  PREREQUISITE FAILED: these words are not in γ_{n}:")
        for w in res['not_in_gamma_n']:
            print(f"       {w}")
        print(f"{'='*65}\n")
        return

    print(f"  Words: {', '.join(words)}")
    print(f"  Monomial basis of degree {n} (dim = {len(basis)}):")
    print(f"    { '  '.join(mono_str(m) for m in basis) }")
    print()

    # Matrix
    print(f"  Degree-{n} Magnus matrix  ({k} × {len(basis)}):")
    col_w = max(6, max(len(mono_str(m)) for m in basis) + 1)
    header = '  ' + ''.join(f"{mono_str(m):>{col_w}}" for m in basis)
    print(header)
    for i, (w, row) in enumerate(zip(words, res['matrix'])):
        row_str = '  ' + ''.join(f"{v:>{col_w}}" for v in row)
        print(f"  w{i+1}={w:<14}{row_str}")

    print()
    print(f"  Smith Normal Form diagonal: {res['snf_diag']}")
    print(f"  ℤ-rank of matrix          : {res['rank']}  (need {k} for free rank {k})")
    print(f"{'─'*65}")

    verdict = "YES  ✓" if res['is_free_rank_k'] else "NO   ✗"
    print(f"  Result: free abelian of rank {k} in γ_{n}/γ_{n+1} ?   {verdict}")
    if not res['is_free_rank_k']:
        if res['rank'] < k:
            print(f"  Reason: rank is only {res['rank']} — words are ℤ-linearly dependent mod γ_{n+1}.")
    print(f"{'='*65}\n")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    # Command-line: python lcs_graded.py n word1 word2 ...
    if len(sys.argv) >= 3:
        n_arg = int(sys.argv[1])
        words_arg = sys.argv[2:]
        check_free_abelian_rank(words_arg, n_arg)
        sys.exit(0)

    print(__doc__)
    print("\n" + "="*65)
    print("  EXAMPLES")
    print("="*65)

    # ── Example 1 ──────────────────────────────────────────────────
    print("\n[1] γ₂/γ₃ has rank 1 (spanned by [x,y]).")
    print("    One copy of [x,y]: should be rank 1.")
    check_free_abelian_rank(["[x,y]"], n=2)

    print("    Two copies [x,y] and [x,y]^2: linearly dependent over ℤ → rank 1, not 2.")
    check_free_abelian_rank(["[x,y]", "[x,y]^2"], n=2)

    # ── Example 2 ──────────────────────────────────────────────────
    print("\n[2] γ₃/γ₄ has rank 2 (spanned by [[x,y],x] and [[x,y],y]).")
    print("    These two basic commutators: should be rank 2.")
    check_free_abelian_rank(["[[x,y],x]", "[[x,y],y]"], n=3)

    print("    Just [[x,y],x] alone: rank 1 in a rank-2 group.")
    check_free_abelian_rank(["[[x,y],x]"], n=3)

    print("    Three words in γ₃/γ₄ (rank 2): can't have rank 3.")
    check_free_abelian_rank(["[[x,y],x]", "[[x,y],y]", "[[x,y],x]^2"], n=3)

    # ── Example 3 ──────────────────────────────────────────────────
    print("\n[3] γ₄/γ₅ has rank 3.")
    print("    Three basic weight-4 commutators: should be rank 3.")
    check_free_abelian_rank(
        ["[[[x,y],x],x]", "[[[x,y],x],y]", "[[[x,y],y],y]"],
        n=4
    )

    # ── Example 4: prerequisite failure ────────────────────────────
    print("\n[4] Prerequisite check: 'x' does not lie in γ₂.")
    check_free_abelian_rank(["x", "[x,y]"], n=2)
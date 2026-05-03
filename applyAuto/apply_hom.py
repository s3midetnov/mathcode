"""
Homomorphism utility for free group F(x, y).

apply_hom(word, wx, wy)  —  substitute x->wx, y->wy and reduce.
LCS_CANDIDATES           —  words deep in the LCS, for use as substitutions.
"""

from freegrouplib import reduce_word, inverse_word


def comm(u, v):
    """Free group commutator [u, v] = u v u^{-1} v^{-1}, reduced."""
    return reduce_word(u + v + inverse_word(u) + inverse_word(v))


def apply_hom(word, wx, wy):
    """
    Apply f : x -> wx, y -> wy  (X -> wx^{-1}, Y -> wy^{-1}) to word and reduce.
    word must contain only x, y, X, Y.
    """
    wX = inverse_word(wx)
    wY = inverse_word(wy)
    table = {'x': wx, 'X': wX, 'y': wy, 'Y': wY}
    return reduce_word(''.join(table[c] for c in word))


# ---------------------------------------------------------------------------
# Standard iterated commutators, built from x and y
# [gamma_i, gamma_j] <= gamma_{i+j}, so the depth labels are lower bounds.
# ---------------------------------------------------------------------------
#
# _c2  = comm('x', 'y')           # [x,y]                     depth >= 2
# _c3a = comm(_c2,  'x')          # [[x,y],x]                 depth >= 3
# _c3b = comm(_c2,  'y')          # [[x,y],y]                 depth >= 3
# _c4a = comm(_c3a, 'y')          # [[[x,y],x],y]             depth >= 4
# _c4b = comm(_c3a, 'x')          # [[[x,y],x],x]             depth >= 4
# _c4c = comm(_c3b, 'x')          # [[[x,y],y],x]             depth >= 4
# _c5a = comm(_c4a, 'x')          # [[[[x,y],x],y],x]         depth >= 5
# _c5b = comm(_c4a, 'y')          # [[[[x,y],x],y],y]         depth >= 5
# _c5c = comm(_c4b, 'y')          # [[[[x,y],x],x],y]         depth >= 5
# _c5d = comm(_c3a, _c2)          # [[[x,y],x],[x,y]]         depth >= 5 (=[gamma_3,gamma_2])
# _c6a = comm(_c5a, 'y')          # [[[[[x,y],x],y],x],y]     depth >= 6
# _c6b = comm(_c3a, _c3b)         # [[[x,y],x],[[x,y],y]]     depth >= 6 (=[gamma_3,gamma_3])
# _c6c = comm(_c2,  _c4a)         # [[x,y],[[[x,y],x],y]]     depth >= 6 (=[gamma_2,gamma_4])
#
# # Squares (same depth lower bound as the base word, different structure)
# _c2sq  = reduce_word(_c2  + _c2)   # [x,y]^2       depth >= 2
# _c3sq  = reduce_word(_c3a + _c3a)  # [[x,y],x]^2   depth >= 3
#
# _c2_c3 = reduce_word(_c2 + _c3b)
# _c3_c4 = reduce_word(_c3b + _c4b)

# ---------------------------------------------------------------------------
# Candidate list:  (min_depth, word_string, description)
# ---------------------------------------------------------------------------

# LCS_CANDIDATES = [
#     (2, _c2,   '[x,y]'),
#     (2, _c2sq, '[x,y]^2'),
#     (3, _c3a,  '[[x,y],x]'),
#     (3, _c3b,  '[[x,y],y]'),
#     (3, _c3sq, '[[x,y],x]^2'),
#     (4, _c4a,  '[[[x,y],x],y]'),
#     (4, _c4b,  '[[[x,y],x],x]'),
#     (4, _c4c,  '[[[x,y],y],x]'),
#     (5, _c5a,  '[[[[x,y],x],y],x]'),
#     (5, _c5b,  '[[[[x,y],x],y],y]'),
#     (5, _c5c,  '[[[[x,y],x],x],y]'),
#     (5, _c5d,  '[[[x,y],x],[x,y]]'),
#     (6, _c6a,  '[[[[[x,y],x],y],x],y]'),
#     (6, _c6b,  '[[[x,y],x],[[x,y],y]]'),
#     (6, _c6c,  '[[x,y],[[[x,y],x],y]]'),
#     (2, _c2_c3, 'c2c3'),
#     (3, _c3_c4, 'c3c4'),
# ]
# Assume comm(a,b) and reduce_word(w) are already defined

# Base commutator
_c2  = comm('x', 'y')                 # depth >= 2

# Build up to depth ≥ 5 first
_c3a = comm(_c2, 'x')                 # depth >= 3
_c3b = comm(_c2, 'y')                 # depth >= 3

_c4a = comm(_c3a, 'x')                # depth >= 4
_c4b = comm(_c3a, 'y')                # depth >= 4
_c4c = comm(_c3b, 'x')                # depth >= 4

# Depth ≥ 5 commutators
_c5a = comm(_c4a, 'x')                # [[[[x,y],x],x],x]
_c5b = comm(_c4a, 'y')                # [[[[x,y],x],x],y]
_c5c = comm(_c4b, 'x')                # [[[[x,y],x],y],x]
_c5d = comm(_c4b, 'y')                # [[[[x,y],x],y],y]
_c5e = comm(_c4c, 'x')                # [[[[x,y],y],x],x]
_c5f = comm(_c3a, _c2)                # [[[x,y],x],[x,y]]
_c5g = comm(_c3b, _c2)                # [[[x,y],y],[x,y]]

# Products / combinations (still depth ≥ 5)
_p5a = reduce_word(_c5a + _c5b)
_p5b = reduce_word(_c5c + _c5d)
_p5c = reduce_word(_c5e + _c5a)
_p5d = reduce_word(_c5f + _c5g)
_p5e = reduce_word(_c5a + _c5f)
_p5f = reduce_word(_c5b + _c5g)
_p5g = reduce_word(_c5c + _c5e)
_p5h = reduce_word(_c5d + _c5f)

# Final candidate list (~15 elements, all depth ≥ 5)
LCS_CANDIDATES = [
    (5, _c5a, '[[[[x,y],x],x],x]'),
    (5, _c5b, '[[[[x,y],x],x],y]'),
    (5, _c5c, '[[[[x,y],x],y],x]'),
    (5, _c5d, '[[[[x,y],x],y],y]'),
    (5, _c5e, '[[[[x,y],y],x],x]'),
    (5, _c5f, '[[[x,y],x],[x,y]]'),
    (5, _c5g, '[[[x,y],y],[x,y]]'),
    (5, _p5a, 'c5a * c5b'),
    (5, _p5b, 'c5c * c5d'),
    (5, _p5c, 'c5e * c5a'),
    (5, _p5d, 'c5f * c5g'),
    (5, _p5e, 'c5a * c5f'),
    (5, _p5f, 'c5b * c5g'),
    (5, _p5g, 'c5c * c5e'),
    (5, _p5h, 'c5d * c5f'),
]



# ---------------------------------------------------------------------------
# Quick self-check: print candidates with their actual computed depths
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    from lcs_checker import parse_word, magnus

    MAX_DEG = 12

    def lcs_depth(word_str):
        net_x = word_str.count('x') - word_str.count('X')
        net_y = word_str.count('y') - word_str.count('Y')
        if net_x != 0 or net_y != 0:
            return 1
        letters = parse_word(word_str)
        if not letters:
            return MAX_DEG + 1
        poly = magnus(letters, MAX_DEG)
        for d in range(1, MAX_DEG + 1):
            if any(len(mono) == d and coeff != 0 for mono, coeff in poly.items()):
                return d
        return MAX_DEG + 1

    print(f"{'description':<35}  {'min':>5}  {'actual':>7}  word")
    print('-' * 80)
    for min_d, w, desc in LCS_CANDIDATES:
        actual = lcs_depth(w)
        actual_s = f'>{MAX_DEG}' if actual > MAX_DEG else str(actual)
        print(f'{desc:<35}  {min_d:>5}  {actual_s:>7}  {w}')

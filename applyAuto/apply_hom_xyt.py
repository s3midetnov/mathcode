"""
apply_hom_xyt.py  —  run from within applyAuto/

Extends the applyAuto pipeline with a homomorphism into F(x, y, t).

get_4tuple_xyt(aut_key, u, v)
  1. Apply the named automorphism to {a, b, c, d} in F(a, b, c, d).
  2. Project to F(x, y) via map_word1: a↦x, b↦y, c↦y, d↦x.
  3. Send x↦u, y↦v to land in F(x, y, t).
  Returns (a_img, b_img, c_img, d_img) as reduced words over {x,y,t,X,Y,T}.
"""
from pi1S2auto import (aut1, aut2, aut3, aut4, aut5,
                       aut1n, aut2n, aut3n, aut4n, aut5n,
                       map_word1)
from freegrouplib import apply_aut

aut_map = {
    '1': aut1, '2': aut2, '3': aut3, '4': aut4, '5': aut5,
    '1n': aut1n, '2n': aut2n, '3n': aut3n, '4n': aut4n, '5n': aut5n,
}

_XYT_INV = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y', 't': 'T', 'T': 't'}
_XY_INV  = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y'}


def _red_xy(w):
    stack = []
    for c in w:
        if stack and _XY_INV.get(c) == stack[-1]:
            stack.pop()
        else:
            stack.append(c)
    return ''.join(stack)


def _red_xyt(w):
    stack = []
    for c in w:
        if stack and _XYT_INV.get(c) == stack[-1]:
            stack.pop()
        else:
            stack.append(c)
    return ''.join(stack)


def _inv_xyt(w):
    return ''.join(_XYT_INV[c] for c in reversed(w))


def _sub_xy(word_xy, u, v):
    """Apply x↦u, y↦v to word_xy ∈ F(x,y), producing a word in F(x,y,t)."""
    table = {'x': u, 'X': _inv_xyt(u), 'y': v, 'Y': _inv_xyt(v)}
    return _red_xyt(''.join(table[c] for c in word_xy))


def get_4tuple_xyt(aut_key, u, v):
    """
    Parameters
    ----------
    aut_key : str
        Key in aut_map — one of '1','2','3','4','5','1n','2n','3n','4n','5n'.
    u, v : str
        Reduced words in F(x,y,t) over letters x,y,t,X,Y,T.

    Returns
    -------
    tuple of 4 str
        (a_img, b_img, c_img, d_img) as reduced words in F(x,y,t).
    """
    aut = aut_map[aut_key]
    result = []
    for g in 'abcd':
        w_abcd = apply_aut(g, aut)
        w_xy   = _red_xy(map_word1(w_abcd))
        w_xyt  = _sub_xy(w_xy, u, v)
        result.append(w_xyt)
    return tuple(result)

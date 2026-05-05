"""
apply_hom_xyt.py  —  run from within applyAuto6/

Extends the applyAuto6 pipeline with a homomorphism into F(x, y, t).

get_6tuple_xyt(aut_key, p, q, r)
  1. Apply the named automorphism to {a,b,c,d,e,f} in F(a,b,c,d,e,f).
  2. Project to F(x,y,z) via map_word3: a↦x, b↦y, c↦z, d↦z, e↦y, f↦x.
  3. Send x↦p, y↦q, z↦r to land in F(x,y,t).
  Returns (a_img,...,f_img) as reduced words over {x,y,t,X,Y,T}.
"""
from automorphisms import aut_map, map_word3
from freegrouplib2 import apply_aut

_XYT_INV = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y', 't': 'T', 'T': 't'}
_XYZ_INV = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y', 'z': 'Z', 'Z': 'z'}


def _red_xyz(w):
    stack = []
    for c in w:
        if stack and _XYZ_INV.get(c) == stack[-1]:
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


def _sub_xyz(word_xyz, p, q, r):
    """Apply x↦p, y↦q, z↦r to word_xyz ∈ F(x,y,z), producing a word in F(x,y,t)."""
    table = {'x': p, 'X': _inv_xyt(p), 'y': q, 'Y': _inv_xyt(q),
             'z': r, 'Z': _inv_xyt(r)}
    return _red_xyt(''.join(table[c] for c in word_xyz))


def get_6tuple_xyt(aut_key, p, q, r):
    """
    Parameters
    ----------
    aut_key : str
        Key in aut_map — one of '1'–'8' and their 'n' inverses.
    p, q, r : str
        Reduced words in F(x,y,t) over letters x,y,t,X,Y,T.

    Returns
    -------
    tuple of 6 str
        (a_img, b_img, c_img, d_img, e_img, f_img) as reduced words in F(x,y,t).
    """
    aut = aut_map[aut_key]
    result = []
    for g in 'abcdef':
        w_abcdef = apply_aut(g, aut)
        w_xyz    = _red_xyz(map_word3(w_abcdef))
        w_xyt    = _sub_xyz(w_xyz, p, q, r)
        result.append(w_xyt)
    return tuple(result)

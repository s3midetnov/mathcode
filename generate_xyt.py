#!/usr/bin/env python3
"""
generate_xyt.py  —  run from the mathcode/ root directory.

Generates:
  tuples4_xyt.txt   — unique 4-tuples (a,b,c,d) in F(x,y,t)
  tuples6_xyt.txt   — unique 6-tuples (a,b,c,d,e,f) in F(x,y,t)
  successes_xyt.txt — success pairs with matching evidence

Pipeline for 4-tuples:
  aut ∈ AUT4 on F(a,b,c,d)  →  project via map_word1 to F(x,y)  →  x↦u, y↦v  →  F(x,y,t)

Pipeline for 6-tuples:
  aut ∈ AUT6 on F(a,b,c,d,e,f)  →  project via map_word3 to F(x,y,z)  →  x↦p, y↦q, z↦r  →  F(x,y,t)

Success condition for a pair (T4, T6):
  T4 = (a, b, c, d):    fixed pairs  P4_0={a,b},  P4_1={c,d}
  T6 = (p,q,r,s,u,v):  fixed pairs  P6_0={p,q},  P6_1={r,s},  P6_2={u,v}
  ∃ distinct i≠j in {0,1,2} such that
      (a∈P6_i or b∈P6_i)  and  (c∈P6_j or d∈P6_j)

Usage:
  python3 generate_xyt.py [max_len_uv] [max_len_pqr]

  max_len_uv  : max length of each of u,v   (default 3; ~350K combos)
  max_len_pqr : max length of each of p,q,r (default 2; ~810K combos)
"""

import os, sys, time
from collections import defaultdict

# ══════════════════════════════════════════════════════════════════════
# Free-group reduction / inverse helpers
# ══════════════════════════════════════════════════════════════════════

_ABCDEF_INV = {c: c.upper() for c in 'abcdef'}
_ABCDEF_INV.update({c: c.lower() for c in 'ABCDEF'})

_XY_INV  = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y'}
_XYZ_INV = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y', 'z': 'Z', 'Z': 'z'}
_XYT_INV = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y', 't': 'T', 'T': 't'}


def _reduce(word, inv):
    stack = []
    for c in word:
        if stack and inv.get(c) == stack[-1]:
            stack.pop()
        else:
            stack.append(c)
    return ''.join(stack)


def _inv(word, inv_map):
    return ''.join(inv_map[c] for c in reversed(word))


def red4(w):   return _reduce(w, _ABCDEF_INV)
def red6(w):   return _reduce(w, _ABCDEF_INV)
def red_xy(w): return _reduce(w, _XY_INV)
def red_xyz(w):return _reduce(w, _XYZ_INV)
def red_xyt(w):return _reduce(w, _XYT_INV)
def inv_xyt(w):return _inv(w, _XYT_INV)


def apply_aut(word, aut, red_fn):
    return red_fn(''.join(aut[c] for c in word))

# ══════════════════════════════════════════════════════════════════════
# Automorphisms of F(a,b,c,d)   [matches applyAuto/pi1S2auto.py]
# ══════════════════════════════════════════════════════════════════════

_id4 = {g: g for g in 'abcdABCD'}

AUT4 = {
    '1' : {**_id4, 'a': 'ab',  'A': 'BA'},
    '1n': {**_id4, 'a': 'aB',  'A': 'bA'},
    '2' : {**_id4, 'b': 'ba',  'B': 'AB'},
    '2n': {**_id4, 'b': 'bA',  'B': 'aB'},
    '3' : {**_id4, 'c': 'cd',  'C': 'DC'},
    '3n': {**_id4, 'c': 'cD',  'C': 'dC'},
    '4' : {**_id4, 'd': 'dc',  'D': 'CD'},
    '4n': {**_id4, 'd': 'dC',  'D': 'cD'},
    '5' : {**_id4, 'b': 'Adb', 'B': 'BDa', 'c': 'Adc', 'C': 'CDa'},
    '5n': {**_id4, 'b': 'Dab', 'B': 'BAd', 'c': 'Dac', 'C': 'CAd'},
}

# map_word1: F(a,b,c,d) → F(x,y)  (a↦x, b↦y, c↦y, d↦x)
_MAP4_XY = {'a':'x','A':'X','b':'y','B':'Y','c':'y','C':'Y','d':'x','D':'X'}
def proj4(w): return red_xy(''.join(_MAP4_XY[c] for c in w))

# ══════════════════════════════════════════════════════════════════════
# Automorphisms of F(a,b,c,d,e,f) [matches applyAuto6/automorphisms.py]
# ══════════════════════════════════════════════════════════════════════

_id6 = {g: g for g in 'abcdefABCDEF'}

AUT6 = {
    '1' : {**_id6, 'a': 'ab',    'A': 'BA'},
    '1n': {**_id6, 'a': 'aB',    'A': 'bA'},
    '2' : {**_id6, 'b': 'ba',    'B': 'AB'},
    '2n': {**_id6, 'b': 'bA',    'B': 'aB'},
    '3' : {**_id6, 'c': 'cd',    'C': 'DC'},
    '3n': {**_id6, 'c': 'cD',    'C': 'dC'},
    '4' : {**_id6, 'd': 'dc',    'D': 'CD'},
    '4n': {**_id6, 'd': 'dC',    'D': 'cD'},
    '5' : {**_id6, 'b': 'Adb',   'B': 'BDa',  'c': 'Adc',   'C': 'CDa',
                   'e': 'dAeaD', 'E': 'dAEaD', 'f': 'dAfaD', 'F': 'dAFaD'},
    '5n': {**_id6, 'b': 'Dab',   'B': 'BAd',  'c': 'Dac',   'C': 'CAd',
                   'e': 'aDedA', 'E': 'aDEdA', 'f': 'aDfdA', 'F': 'aDFdA'},
    '6' : {**_id6, 'c': 'Dec',   'C': 'CEd',  'f': 'Def',   'F': 'FEd',
                   'a': 'DeaEd', 'A': 'DeAEd', 'b': 'DebEd', 'B': 'DeBEd'},
    '6n': {**_id6, 'c': 'Edc',   'C': 'CDe',  'f': 'Edf',   'F': 'FDe',
                   'a': 'EdaDe', 'A': 'EdADe', 'b': 'EdbDe', 'B': 'EdBDe'},
    '7' : {**_id6, 'e': 'ef',    'E': 'FE'},
    '7n': {**_id6, 'e': 'eF',    'E': 'fE'},
    '8' : {**_id6, 'f': 'fe',    'F': 'EF'},
    '8n': {**_id6, 'f': 'fE',    'F': 'eF'},
}

# map_word3: F(a,b,c,d,e,f) → F(x,y,z)  (a↦x, b↦y, c↦z, d↦z, e↦y, f↦x)
_MAP6_XYZ = {'a':'x','A':'X','b':'y','B':'Y','c':'z','C':'Z',
             'd':'z','D':'Z','e':'y','E':'Y','f':'x','F':'X'}
def proj6(w): return red_xyz(''.join(_MAP6_XYZ[c] for c in w))

# ══════════════════════════════════════════════════════════════════════
# Homomorphisms into F(x,y,t)
# ══════════════════════════════════════════════════════════════════════

def sub_xy(word_xy, u, v):
    """F(x,y) → F(x,y,t): substitute x↦u, y↦v and reduce."""
    table = {'x': u, 'X': inv_xyt(u), 'y': v, 'Y': inv_xyt(v)}
    return red_xyt(''.join(table[c] for c in word_xy))


def sub_xyz(word_xyz, p, q, r):
    """F(x,y,z) → F(x,y,t): substitute x↦p, y↦q, z↦r and reduce."""
    table = {'x': p, 'X': inv_xyt(p), 'y': q, 'Y': inv_xyt(q),
             'z': r, 'Z': inv_xyt(r)}
    return red_xyt(''.join(table[c] for c in word_xyz))

# ══════════════════════════════════════════════════════════════════════
# Pipeline functions  (these mirror the per-directory modules)
# ══════════════════════════════════════════════════════════════════════

def get_4tuple_xyt(aut_key, u, v):
    """
    Apply AUT4[aut_key] to a,b,c,d, project via map_word1, then x↦u, y↦v.
    Returns (a_img, b_img, c_img, d_img) in F(x,y,t).
    """
    aut = AUT4[aut_key]
    result = []
    for g in 'abcd':
        w4   = apply_aut(g, aut, red4)
        wxy  = proj4(w4)
        wxyt = sub_xy(wxy, u, v)
        result.append(wxyt)
    return tuple(result)


def get_6tuple_xyt(aut_key, p, q, r):
    """
    Apply AUT6[aut_key] to a,...,f, project via map_word3, then x↦p, y↦q, z↦r.
    Returns (a_img, b_img, c_img, d_img, e_img, f_img) in F(x,y,t).
    """
    aut = AUT6[aut_key]
    result = []
    for g in 'abcdef':
        w6   = apply_aut(g, aut, red6)
        wxyz = proj6(w6)
        wxyt = sub_xyz(wxyz, p, q, r)
        result.append(wxyt)
    return tuple(result)

# ══════════════════════════════════════════════════════════════════════
# Word generation in F(x,y,t)
# ══════════════════════════════════════════════════════════════════════

def gen_words_xyt(max_len):
    """All reduced words in F(x,y,t) of length 0..max_len."""
    gens = 'xytXYT'
    words = ['']
    frontier = ['']
    for _ in range(max_len):
        nxt = []
        for w in frontier:
            last = w[-1] if w else None
            for g in gens:
                if last is not None and _XYT_INV[g] == last:
                    continue
                nxt.append(w + g)
        words.extend(nxt)
        frontier = nxt
    return words

# ══════════════════════════════════════════════════════════════════════
# Bulk generation
# ══════════════════════════════════════════════════════════════════════

def generate_4tuples(max_len_uv=3):
    words = gen_words_xyt(max_len_uv)
    total = len(AUT4) * len(words) ** 2
    print(f"  {len(AUT4)} auts × {len(words)}² = {total:,} combinations")
    seen = set()
    tuples = []
    for aut_key in AUT4:
        for u in words:
            for v in words:
                t = get_4tuple_xyt(aut_key, u, v)
                if t not in seen:
                    seen.add(t)
                    tuples.append(t)
    print(f"  → {len(tuples):,} unique 4-tuples")
    return tuples


def generate_6tuples(max_len_pqr=2):
    words = gen_words_xyt(max_len_pqr)
    total = len(AUT6) * len(words) ** 3
    print(f"  {len(AUT6)} auts × {len(words)}³ = {total:,} combinations")
    seen = set()
    tuples = []
    done = 0
    report_every = max(1, total // 20)
    for aut_key in AUT6:
        for p in words:
            for q in words:
                for r in words:
                    t = get_6tuple_xyt(aut_key, p, q, r)
                    done += 1
                    if t not in seen:
                        seen.add(t)
                        tuples.append(t)
                if done % report_every == 0:
                    pct = 100 * done // total
                    print(f"  {pct:3d}%  {done:,}/{total:,}  unique so far: {len(tuples):,}", end='\r')
    print()
    print(f"  → {len(tuples):,} unique 6-tuples")
    return tuples

# ══════════════════════════════════════════════════════════════════════
# Success detection  (streaming + reverse-index, low memory)
# ══════════════════════════════════════════════════════════════════════

def find_successes_streaming(f4_path, f6_path, out_path, min_shared_len=2):
    """
    Stream-based success detection to avoid loading both tuple sets into RAM.

    Phase 1: read tuples4 file once → build word_to_t4 index.
    Phase 2: stream tuples6 file → for each T6 look up matches via index
             → write successes directly to out_path.

    Success definition:
      T4=(a,b,c,d): P4_0={a,b}, P4_1={c,d}
      T6=(p,q,r,s,u,v): P6_0={p,q}, P6_1={r,s}, P6_2={u,v}
      ∃ distinct i≠j: P4_0∩P6_i≠∅ and P4_1∩P6_j≠∅

    min_shared_len: skip the identity '' and short generators as witnesses.
    Returns total number of successes written.
    """
    # ── Phase 1: build word → [(t4_line_idx, t4_pair)] index ──────────
    # t4_pair=0 means the word is in {a,b}; t4_pair=1 means it's in {c,d}
    word_to_t4 = defaultdict(list)
    t4_lines = []   # keep raw lines for output (only pair0+pair1 as words)

    print("  Phase 1: indexing 4-tuples...", end=' ', flush=True)
    t_p1 = time.time()
    with open(f4_path) as fh:
        for i, raw in enumerate(fh):
            line = raw.rstrip('\n')
            t4_lines.append(line)
            parts = [p.strip() for p in line.split(',')]
            if len(parts) != 4:
                continue
            for pair, ws in ((0, parts[:2]), (1, parts[2:])):
                for w in ws:
                    if len(w) >= min_shared_len:
                        word_to_t4[w].append((i, pair))
    n4 = len(t4_lines)
    print(f"{n4:,} 4-tuples, {len(word_to_t4):,} index words  [{time.time()-t_p1:.1f}s]")

    # ── Phase 2: stream 6-tuples ───────────────────────────────────────
    print("  Phase 2: streaming 6-tuples...", flush=True)
    t_p2 = time.time()
    total_successes = 0

    with open(f6_path) as fin, open(out_path, 'w') as fout:
        for j, raw6 in enumerate(fin):
            parts6 = [p.strip() for p in raw6.rstrip('\n').split(',')]
            if len(parts6) != 6:
                continue

            if j % 50000 == 0:
                print(f"    {j:,} 6-tuples done, {total_successes:,} successes", end='\r')

            # For each t4 that shares ≥1 word with T6, collect (t4_pair, t6_pair_k)
            # t4_events[i4] is a set of (t4_pair, t6_pair_k) events
            t4_events = defaultdict(set)
            for k in range(3):
                for w in parts6[2*k:2*k+2]:
                    if len(w) >= min_shared_len and w in word_to_t4:
                        for (i4, t4_pair) in word_to_t4[w]:
                            t4_events[i4].add((t4_pair, k))

            # Each i4 appears at most once in t4_events so no dedup needed
            for i4, events in t4_events.items():
                k0 = {k for (p, k) in events if p == 0}  # T6 pair indices matching T4-pair0
                k1 = {k for (p, k) in events if p == 1}  # T6 pair indices matching T4-pair1
                if not k0 or not k1:
                    continue
                if any(ka != kb for ka in k0 for kb in k1):
                    total_successes += 1
                    fout.write(f"4: {t4_lines[i4]}\n")
                    fout.write(f"6: {raw6.rstrip()}\n\n")

    print(f"\n  {total_successes:,} successes  [{time.time()-t_p2:.1f}s]")
    return total_successes

# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    MAX_LEN_UV      = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    MAX_LEN_PQR     = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    MIN_SHARED_LEN  = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    base = os.path.dirname(os.path.abspath(__file__))
    f4   = os.path.join(base, 'tuples4_xyt.txt')
    f6   = os.path.join(base, 'tuples6_xyt.txt')
    fs   = os.path.join(base, 'successes_xyt.txt')

    if not os.path.exists(f4):
        print(f"\n=== 4-tuples in F(x,y,t)  [max_len_uv={MAX_LEN_UV}] ===")
        t0 = time.time()
        t4 = generate_4tuples(MAX_LEN_UV)
        print(f"  Done in {time.time()-t0:.1f}s")
        with open(f4, 'w') as fh:
            for t in t4:
                fh.write(', '.join(t) + '\n')
        print(f"  Saved → {f4}")
    else:
        n4 = sum(1 for _ in open(f4))
        print(f"Using existing {f4}  ({n4:,} lines)")

    if not os.path.exists(f6):
        print(f"\n=== 6-tuples in F(x,y,t)  [max_len_pqr={MAX_LEN_PQR}] ===")
        t0 = time.time()
        t6 = generate_6tuples(MAX_LEN_PQR)
        print(f"  Done in {time.time()-t0:.1f}s")
        with open(f6, 'w') as fh:
            for t in t6:
                fh.write(', '.join(t) + '\n')
        print(f"  Saved → {f6}")
    else:
        n6 = sum(1 for _ in open(f6))
        print(f"Using existing {f6}  ({n6:,} lines)")

    print(f"\n=== Finding successes  [min_shared_len={MIN_SHARED_LEN}] ===")
    t0 = time.time()
    n_success = find_successes_streaming(f4, f6, fs, min_shared_len=MIN_SHARED_LEN)
    print(f"  Total time: {time.time()-t0:.1f}s")
    print(f"  Saved → {fs}")

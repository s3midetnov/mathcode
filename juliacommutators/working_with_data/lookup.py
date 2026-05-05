#!/usr/bin/env python3
"""
Lookup three_triples containing a given cross-pair (word1, word2).

Usage:
    python3 lookup.py "𝑥₁𝑥₂𝑋₁𝑋₂" "𝑥₂𝑥₁𝑋₂𝑋₁"
    python3 lookup.py --xy "xyXY" "yxYX"      # x=x1, y=x2, X=X1, Y=X2

Returns all three_triples (i,j,k) containing both words, with their complements.

Can also be imported:
    from lookup import lookup, encode_xy
    results = lookup(word1_str, word2_str)
"""

import sqlite3, sys

DB_FILE = "presentations.db"

POS = '\U0001d465'  # 𝑥
NEG = '\U0001d44b'  # 𝑋
SUB = [chr(0x2080+i) for i in range(10)]

_XY_MAP = {'x':(POS,1),'y':(POS,2),'z':(POS,3),
           'X':(NEG,1),'Y':(NEG,2),'Z':(NEG,3)}

def encode_xy(notation: str) -> str:
    """Convert x/y/z/X/Y/Z shorthand to Unicode FreeWord string (x=x1,y=x2,z=x3)."""
    return ''.join(sign + SUB[idx] for c in notation for sign, idx in [_XY_MAP[c]])

def _fetch_words(cur, ids):
    if not ids:
        return {}
    ph = ','.join('?' * len(ids))
    cur.execute(f"SELECT id, word_str FROM words WHERE id IN ({ph})", list(ids))
    return dict(cur.fetchall())

def lookup(word1: str, word2: str, db: str = DB_FILE) -> list[dict]:
    """
    Find all three_triples containing both word1 and word2.

    Returns a list of dicts:
        { 'triple': (str, str, str), 'complement': (str, str, str) }
    where triple contains both query words plus a third, and complement is the
    remaining word from each original commutator pair.
    """
    con = sqlite3.connect(db)
    cur = con.cursor()

    cur.execute("SELECT id FROM words WHERE word_str = ?", (word1,))
    r1 = cur.fetchone()
    cur.execute("SELECT id FROM words WHERE word_str = ?", (word2,))
    r2 = cur.fetchone()

    if r1 is None or r2 is None:
        missing = [w for w, r in [(word1,r1),(word2,r2)] if r is None]
        print(f"Not found in DB: {missing}", file=sys.stderr)
        con.close()
        return []

    id1, id2 = r1[0], r2[0]

    cur.execute("""
        SELECT t.i, t.j, t.k, c.comp_i, c.comp_j, c.comp_k
        FROM three_triples t
        JOIN three_triple_complements c
          ON c.tri_i = t.i AND c.tri_j = t.j AND c.tri_k = t.k
        WHERE (t.i = :a OR t.j = :a OR t.k = :a)
          AND (t.i = :b OR t.j = :b OR t.k = :b)
    """, {'a': id1, 'b': id2})
    rows = cur.fetchall()

    all_ids = set()
    for row in rows:
        all_ids.update(row)
    id_to_str = _fetch_words(cur, all_ids)
    con.close()

    seen, results = set(), []
    for ti, tj, tk, ci, cj, ck in rows:
        key = (ti, tj, tk, ci, cj, ck)
        if key in seen:
            continue
        seen.add(key)
        results.append({
            'triple':     (id_to_str[ti], id_to_str[tj], id_to_str[tk]),
            'complement': (id_to_str[ci], id_to_str[cj], id_to_str[ck]),
        })
    return results


if __name__ == "__main__":
    args = sys.argv[1:]
    xy_mode = False
    if args and args[0] == "--xy":
        xy_mode = True
        args = args[1:]
    if len(args) != 2:
        print("Usage: lookup.py [--xy] word1 word2")
        sys.exit(1)

    w1, w2 = args
    if xy_mode:
        w1, w2 = encode_xy(w1), encode_xy(w2)

    results = lookup(w1, w2)
    if not results:
        print("No matches found.")
    else:
        print(f"{len(results)} match(es):\n")
        for r in results:
            print(f"triple:     {r['triple']}")
            print(f"complement: {r['complement']}")
            print()

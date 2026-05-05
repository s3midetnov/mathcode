#!/usr/bin/env python3
"""
Append a twoRelatorsF3-format file into the database.
Usage: python3 db_append_two.py <input_file>
"""

import sqlite3, json, sys
from math import gcd
from functools import reduce, lru_cache

DB_FILE = "presentations.db"
BATCH   = 10_000

SUBSCRIPT = {'₀':0,'₁':1,'₂':2,'₃':3,'₄':4,'₅':5,'₆':6,'₇':7,'₈':8,'₉':9}

def parse_signed(word):
    result, i = [], 0
    while i < len(word):
        c = word[i]
        if c in ('𝑥', '𝑋'):
            sign = 1 if c == '𝑥' else -1
            i += 1; num = 0
            while i < len(word) and word[i] in SUBSCRIPT:
                num = num*10 + SUBSCRIPT[word[i]]; i += 1
            result.append(sign*num)
        else:
            i += 1
    return result

def abelianize(ints):
    v = [0, 0, 0]
    for g in ints:
        if 1 <= abs(g) <= 3:
            v[abs(g)-1] += 1 if g > 0 else -1
    return v

def snf_factors(u, v):
    d1 = reduce(gcd, (abs(x) for x in u+v), 0)
    if d1 == 0: return (0, 0)
    minors = [u[0]*v[1]-u[1]*v[0], u[0]*v[2]-u[2]*v[0], u[1]*v[2]-u[2]*v[1]]
    return (d1, reduce(gcd, (abs(x) for x in minors), 0) // d1)

def norm_pair(a, b): return (a,b) if a < b else (b,a)

infile = sys.argv[1] if len(sys.argv) > 1 else "twoRelatorsF3.txt"

con = sqlite3.connect(DB_FILE, isolation_level=None)
cur = con.cursor()
cur.executescript("""
PRAGMA journal_mode = WAL;
PRAGMA cache_size = -65536;
PRAGMA foreign_keys = ON;
""")

@lru_cache(maxsize=200_000)
def get_word_id(word_str):
    ints = parse_signed(word_str)
    cur.execute("INSERT OR IGNORE INTO words(word_str,word_ints,length) VALUES (?,?,?)",
                (word_str, json.dumps(ints), len(ints)))
    cur.execute("SELECT id FROM words WHERE word_str = ?", (word_str,))
    return cur.fetchone()[0], ints

count = 0
cur.execute("BEGIN")
with open(infile, encoding="utf-8") as f:
    for line in f:
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) != 4:
            continue
        (id_a, ia), (id_b, ib), (id_c, ic), (id_d, id_) = [get_word_id(p) for p in parts]
        ab_a, ab_b = abelianize(ia), abelianize(ib)
        ab_c, ab_d = abelianize(ic), abelianize(id_)

        for (wi, wj, abi, abj), (ci, cj) in [
            ((id_a, id_c, ab_a, ab_c), (id_b, id_d)),
            ((id_a, id_d, ab_a, ab_d), (id_b, id_c)),
            ((id_b, id_c, ab_b, ab_c), (id_a, id_d)),
            ((id_b, id_d, ab_b, ab_d), (id_a, id_c)),
        ]:
            if wi == wj:
                continue
            pi, pj = norm_pair(wi, wj)
            d1, d2 = snf_factors(abi, abj)
            cur.execute("INSERT OR IGNORE INTO two_pairs(i,j,d1,d2) VALUES (?,?,?,?)",
                        (pi, pj, d1, d2))
            cur.execute("INSERT OR IGNORE INTO two_pair_complements(pair_i,pair_j,comp_i,comp_j)"
                        " VALUES (?,?,?,?)", (pi, pj, ci, cj))

        count += 1
        if count % BATCH == 0:
            cur.execute("COMMIT"); cur.execute("BEGIN")
            print(f"  {count:,} lines")

cur.execute("COMMIT")
print(f"Done: {count:,} two-relator lines from {infile}")
con.close()

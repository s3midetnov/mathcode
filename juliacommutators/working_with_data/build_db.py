#!/usr/bin/env python3
"""
Build SQLite database from twoRelatorsF3.txt and threeRelatorsF3.txt.

Schema
------
words                  unique FreeWord strings with integer representation
two_pairs              unordered pairs (i<j), SNF abelianization, nullable non_trivial
two_pair_complements   join: one row per (pair → complement pair) observation
three_pairs            same as two_pairs for THREE-relator data
three_pair_complements join: one row per (pair → two complement pairs) from same line
"""

import sqlite3
import json
from math import gcd
from functools import reduce

DB_FILE    = "presentations.db"
TWO_FILE   = "twoRelatorsF3.txt"
THREE_FILE = "threeRelatorsF3.txt"
BATCH      = 10_000   # commit every this many lines

SUBSCRIPT = {'₀':0,'₁':1,'₂':2,'₃':3,'₄':4,'₅':5,'₆':6,'₇':7,'₈':8,'₉':9}

# ── Schema ────────────────────────────────────────────────────────────────────

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA cache_size = -131072;  -- 128 MB SQLite page cache
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS words (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    word_str  TEXT    UNIQUE NOT NULL,
    word_ints TEXT    NOT NULL,         -- JSON array of signed ints, e.g. [3,2,-3,-2]
    length    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS two_pairs (
    i           INTEGER NOT NULL REFERENCES words(id),
    j           INTEGER NOT NULL REFERENCES words(id),
    d1          INTEGER,                -- Smith Normal Form invariant factors of
    d2          INTEGER,                -- the 2x3 abelianization matrix [ab(i); ab(j)]
    non_trivial INTEGER,                -- NULL=unknown  0=trivial  1=nontrivial
    PRIMARY KEY (i, j),
    CHECK (i < j)
);

CREATE TABLE IF NOT EXISTS two_pair_complements (
    pair_i  INTEGER NOT NULL,
    pair_j  INTEGER NOT NULL,
    comp_i  INTEGER NOT NULL REFERENCES words(id),
    comp_j  INTEGER NOT NULL REFERENCES words(id),
    UNIQUE  (pair_i, pair_j, comp_i, comp_j),
    FOREIGN KEY (pair_i, pair_j) REFERENCES two_pairs(i, j)
);
CREATE INDEX IF NOT EXISTS idx_two_compl ON two_pair_complements(pair_i, pair_j);

CREATE TABLE IF NOT EXISTS three_pairs (
    i           INTEGER NOT NULL REFERENCES words(id),
    j           INTEGER NOT NULL REFERENCES words(id),
    d1          INTEGER,
    d2          INTEGER,
    non_trivial INTEGER,
    PRIMARY KEY (i, j),
    CHECK (i < j)
);

-- comp1 <= comp2 lexicographically (by (i,j)) to avoid storing the same pair of
-- complements in both orders
CREATE TABLE IF NOT EXISTS three_pair_complements (
    pair_i  INTEGER NOT NULL,
    pair_j  INTEGER NOT NULL,
    comp1_i INTEGER NOT NULL,
    comp1_j INTEGER NOT NULL,
    comp2_i INTEGER NOT NULL,
    comp2_j INTEGER NOT NULL,
    UNIQUE  (pair_i, pair_j, comp1_i, comp1_j, comp2_i, comp2_j),
    FOREIGN KEY (pair_i, pair_j)   REFERENCES three_pairs(i, j),
    FOREIGN KEY (comp1_i, comp1_j) REFERENCES three_pairs(i, j),
    FOREIGN KEY (comp2_i, comp2_j) REFERENCES three_pairs(i, j)
);
CREATE INDEX IF NOT EXISTS idx_three_compl ON three_pair_complements(pair_i, pair_j);
"""

# ── Parsing + math ────────────────────────────────────────────────────────────

def parse_signed(word: str) -> list[int]:
    result, i = [], 0
    while i < len(word):
        c = word[i]
        if c in ('𝑥', '𝑋'):
            sign = 1 if c == '𝑥' else -1
            i += 1
            num = 0
            while i < len(word) and word[i] in SUBSCRIPT:
                num = num * 10 + SUBSCRIPT[word[i]]
                i += 1
            result.append(sign * num)
        else:
            i += 1
    return result

def abelianize(ints: list[int]) -> list[int]:
    v = [0, 0, 0]
    for g in ints:
        if 1 <= abs(g) <= 3:
            v[abs(g)-1] += 1 if g > 0 else -1
    return v

def gcd_many(*nums):
    return reduce(gcd, (abs(x) for x in nums), 0)

def snf_factors(u: list[int], v: list[int]) -> tuple[int, int]:
    """
    Invariant factors (d1, d2) of the 2x3 integer matrix [u; v].
    Quotient Z^3 / <u,v>  =  Z/d1 ⊕ Z/d2 ⊕ Z   (0 means free Z factor).
    """
    d1 = gcd_many(*u, *v)
    if d1 == 0:
        return (0, 0)
    minors = [u[0]*v[1]-u[1]*v[0], u[0]*v[2]-u[2]*v[0], u[1]*v[2]-u[2]*v[1]]
    return (d1, gcd_many(*minors) // d1)

def norm_pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)

def norm_comp_pair(p: tuple, q: tuple) -> tuple[tuple, tuple]:
    return (p, q) if p <= q else (q, p)

# ── Word lookup (no Python-side cache — SQLite page cache handles hot words) ──

def get_word(cur, word_str: str) -> tuple[int, list[int]]:
    ints = parse_signed(word_str)
    cur.execute(
        "INSERT OR IGNORE INTO words(word_str, word_ints, length) VALUES (?,?,?)",
        (word_str, json.dumps(ints), len(ints))
    )
    cur.execute("SELECT id FROM words WHERE word_str = ?", (word_str,))
    return cur.fetchone()[0], ints

def insert_pair(cur, table: str, wi: int, wj: int, abi: list, abj: list) -> tuple[int,int]:
    pi, pj = norm_pair(wi, wj)
    d1, d2 = snf_factors(abi, abj)
    cur.execute(
        f"INSERT OR IGNORE INTO {table}(i, j, d1, d2) VALUES (?,?,?,?)",
        (pi, pj, d1, d2)
    )
    return pi, pj

# ── Main ──────────────────────────────────────────────────────────────────────

con = sqlite3.connect(DB_FILE, isolation_level=None)   # manual transaction control
cur = con.cursor()
cur.executescript(SCHEMA)

# ── two-relator lines ─────────────────────────────────────────────────────────
cur.execute("SELECT COUNT(*) FROM two_pair_complements")
if cur.fetchone()[0] > 0:
    print(f"two_pair_complements already populated, skipping {TWO_FILE}")
else:
    print(f"Loading {TWO_FILE} ...")
count = 0
cur.execute("BEGIN")
with open(TWO_FILE, encoding="utf-8") as f:
    for line in f:
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) != 4:
            continue

        (id_a, ia), (id_b, ib), (id_c, ic), (id_d, id_) = [get_word(cur, p) for p in parts]
        ab_a, ab_b, ab_c, ab_d = abelianize(ia), abelianize(ib), abelianize(ic), abelianize(id_)

        # 4 cross-pairs: one word from each original commutator pair (a,b) and (c,d)
        for (wi, wj, abi, abj), (ci, cj) in [
            ((id_a, id_c, ab_a, ab_c), (id_b, id_d)),
            ((id_a, id_d, ab_a, ab_d), (id_b, id_c)),
            ((id_b, id_c, ab_b, ab_c), (id_a, id_d)),
            ((id_b, id_d, ab_b, ab_d), (id_a, id_c)),
        ]:
            if wi == wj:
                continue   # same word on both sides — degenerate pair, skip
            pi, pj = insert_pair(cur, "two_pairs", wi, wj, abi, abj)
            cur.execute(
                "INSERT OR IGNORE INTO two_pair_complements(pair_i,pair_j,comp_i,comp_j)"
                " VALUES (?,?,?,?)",
                (pi, pj, ci, cj)
            )

        count += 1
        if count % BATCH == 0:
            cur.execute("COMMIT")
            cur.execute("BEGIN")
            print(f"  {count:,} lines")

cur.execute("COMMIT")
print(f"  Done: {count:,} two-relator lines")

# ── three-relator lines ───────────────────────────────────────────────────────
print(f"Loading {THREE_FILE} ...")
count = 0
cur.execute("BEGIN")
with open(THREE_FILE, encoding="utf-8") as f:
    for line in f:
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) != 6:
            continue

        words = [get_word(cur, p) for p in parts]
        ids   = [w[0] for w in words]
        abs_  = [abelianize(w[1]) for w in words]

        # 3 pairs from the line: (0,1), (2,3), (4,5)
        pairs = []
        for k in range(3):
            wi, wj = ids[2*k], ids[2*k+1]
            if wi == wj:
                pairs.append(None)
                continue
            pi, pj = insert_pair(cur, "three_pairs", wi, wj, abs_[2*k], abs_[2*k+1])
            pairs.append((pi, pj))

        # For each pair, record its two complement pairs (normalized so comp1 ≤ comp2)
        for k in range(3):
            main   = pairs[k]
            others = [pairs[m] for m in range(3) if m != k]
            if main is None or any(p is None for p in others):
                continue   # skip if any pair in the line is degenerate
            c1, c2 = norm_comp_pair(others[0], others[1])
            cur.execute(
                "INSERT OR IGNORE INTO three_pair_complements"
                "(pair_i,pair_j,comp1_i,comp1_j,comp2_i,comp2_j) VALUES (?,?,?,?,?,?)",
                (main[0], main[1], c1[0], c1[1], c2[0], c2[1])
            )

        count += 1
        if count % BATCH == 0:
            cur.execute("COMMIT")
            cur.execute("BEGIN")
            print(f"  {count:,} lines")

cur.execute("COMMIT")
print(f"  Done: {count:,} three-relator lines")

con.close()
print(f"\nDatabase written to {DB_FILE}")

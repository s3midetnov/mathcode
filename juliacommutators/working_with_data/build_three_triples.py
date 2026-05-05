#!/usr/bin/env python3
"""
Rebuild three-relator tables as cross-triples.

For a line (a, b, c, d, e, f) with commutator pairs (a,b), (c,d), (e,f):
  - 8 cross-triples: one word from each pair, e.g. (a,c,e), (a,c,f), ...
  - complement of (a,c,e) is (b,d,f)
  - each triple stored sorted by word id (i < j < k)

Drops and recreates three_pairs / three_pair_complements.
Keeps words, two_pairs, two_pair_complements intact.
"""

import sqlite3
import json
from functools import lru_cache

DB_FILE    = "presentations.db"
THREE_FILE = "threeRelatorsF3.txt"
BATCH      = 10_000

SUBSCRIPT = {'₀':0,'₁':1,'₂':2,'₃':3,'₄':4,'₅':5,'₆':6,'₇':7,'₈':8,'₉':9}

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

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA cache_size = -131072;
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS three_pair_complements;
DROP TABLE IF EXISTS three_pairs;

CREATE TABLE IF NOT EXISTS three_triples (
    i  INTEGER NOT NULL REFERENCES words(id),
    j  INTEGER NOT NULL REFERENCES words(id),
    k  INTEGER NOT NULL REFERENCES words(id),
    PRIMARY KEY (i, j, k),
    CHECK (i < j AND j < k)
);
CREATE INDEX IF NOT EXISTS idx_tri_i ON three_triples(i);
CREATE INDEX IF NOT EXISTS idx_tri_j ON three_triples(j);
CREATE INDEX IF NOT EXISTS idx_tri_k ON three_triples(k);

CREATE TABLE IF NOT EXISTS three_triple_complements (
    tri_i  INTEGER NOT NULL,
    tri_j  INTEGER NOT NULL,
    tri_k  INTEGER NOT NULL,
    comp_i INTEGER NOT NULL REFERENCES words(id),
    comp_j INTEGER NOT NULL REFERENCES words(id),
    comp_k INTEGER NOT NULL REFERENCES words(id),
    UNIQUE (tri_i, tri_j, tri_k, comp_i, comp_j, comp_k),
    FOREIGN KEY (tri_i, tri_j, tri_k) REFERENCES three_triples(i, j, k)
);
CREATE INDEX IF NOT EXISTS idx_tric ON three_triple_complements(tri_i, tri_j, tri_k);
"""

con = sqlite3.connect(DB_FILE, isolation_level=None)
cur = con.cursor()
cur.executescript(SCHEMA)

@lru_cache(maxsize=500_000)
def get_word_id(word_str: str) -> int:
    cur.execute("SELECT id FROM words WHERE word_str = ?", (word_str,))
    row = cur.fetchone()
    if row is not None:
        return row[0]
    ints = parse_signed(word_str)
    cur.execute(
        "INSERT OR IGNORE INTO words(word_str, word_ints, length) VALUES (?,?,?)",
        (word_str, json.dumps(ints), len(ints))
    )
    cur.execute("SELECT id FROM words WHERE word_str = ?", (word_str,))
    return cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM three_triples")
if cur.fetchone()[0] > 0:
    print("three_triples already populated, skipping")
else:
    print(f"Loading {THREE_FILE} ...")
    count = 0
    cur.execute("BEGIN")
    with open(THREE_FILE, encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.strip().split(",")]
            if len(parts) != 6:
                continue

            ids = [get_word_id(p) for p in parts]
            wa, wb, wc, wd, we, wf = ids  # pairs: (wa,wb), (wc,wd), (we,wf)

            for pa, ca in ((wa, wb), (wb, wa)):
                for pc, cc in ((wc, wd), (wd, wc)):
                    for pe, ce in ((we, wf), (wf, we)):
                        trip = tuple(sorted((pa, pc, pe)))
                        if trip[0] == trip[1] or trip[1] == trip[2]:
                            continue  # degenerate: repeated word
                        comp = tuple(sorted((ca, cc, ce)))

                        cur.execute(
                            "INSERT OR IGNORE INTO three_triples(i,j,k) VALUES (?,?,?)",
                            trip
                        )
                        cur.execute(
                            "INSERT OR IGNORE INTO three_triple_complements"
                            "(tri_i,tri_j,tri_k,comp_i,comp_j,comp_k) VALUES (?,?,?,?,?,?)",
                            (*trip, *comp)
                        )

            count += 1
            if count % BATCH == 0:
                cur.execute("COMMIT")
                cur.execute("BEGIN")
                print(f"  {count:,} lines")

    cur.execute("COMMIT")
    print(f"  Done: {count:,} three-relator lines")

con.close()
print(f"\nDatabase updated: {DB_FILE}")

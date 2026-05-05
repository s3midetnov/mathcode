#!/usr/bin/env python3
"""
Append a threeRelatorsF3-format file into the database as cross-triples.
For a line (a,b,c,d,e,f) with pairs (a,b),(c,d),(e,f), inserts all 8
cross-triples (one word from each pair) with their complements.
Usage: python3 db_append_three.py <input_file>
"""

import sqlite3, json, sys
from functools import lru_cache

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

infile = sys.argv[1] if len(sys.argv) > 1 else "threeRelatorsF3.txt"

con = sqlite3.connect(DB_FILE, isolation_level=None)
cur = con.cursor()
cur.executescript("""
PRAGMA journal_mode = WAL;
PRAGMA cache_size = -65536;
PRAGMA foreign_keys = ON;

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
""")

@lru_cache(maxsize=200_000)
def get_word_id(word_str):
    cur.execute("SELECT id FROM words WHERE word_str = ?", (word_str,))
    row = cur.fetchone()
    if row is not None:
        return row[0]
    ints = parse_signed(word_str)
    cur.execute("INSERT OR IGNORE INTO words(word_str,word_ints,length) VALUES (?,?,?)",
                (word_str, json.dumps(ints), len(ints)))
    cur.execute("SELECT id FROM words WHERE word_str = ?", (word_str,))
    return cur.fetchone()[0]

count = 0
cur.execute("BEGIN")
with open(infile, encoding="utf-8") as f:
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
                        continue
                    comp = tuple(sorted((ca, cc, ce)))
                    cur.execute("INSERT OR IGNORE INTO three_triples(i,j,k) VALUES (?,?,?)", trip)
                    cur.execute(
                        "INSERT OR IGNORE INTO three_triple_complements"
                        "(tri_i,tri_j,tri_k,comp_i,comp_j,comp_k) VALUES (?,?,?,?,?,?)",
                        (*trip, *comp)
                    )

        count += 1
        if count % BATCH == 0:
            cur.execute("COMMIT"); cur.execute("BEGIN")
            print(f"  {count:,} lines")

cur.execute("COMMIT")
print(f"Done: {count:,} three-relator lines from {infile}")
con.close()

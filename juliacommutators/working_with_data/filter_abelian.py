#!/usr/bin/env python3
"""
Filter successes_sorted_smaller.txt: keep only blocks where there exists a pair
(u, v) with u ∈ {a,b} and v ∈ {c,d} (TWO line: a,b,c,d) such that:
  1. Z^3 / <ab(u), ab(v)> is free abelian (no torsion), i.e. quotient is Z^2, Z, or 0
  2. {u, v} appears as one of the three consecutive pairs in the THREE line

Result written to successes_abelian.txt.
"""

from math import gcd
from functools import reduce

in_file  = "v1/successes_sorted_smaller.txt"
out_file = "v1/successes_abelian.txt"

SUBSCRIPT = {'₀': 0, '₁': 1, '₂': 2, '₃': 3, '₄': 4,
             '₅': 5, '₆': 6, '₇': 7, '₈': 8, '₉': 9}


def parse_words(line: str) -> list[str]:
    prefix_end = line.index(":") + 1
    return [w.strip() for w in line[prefix_end:].split(",")]


def parse_signed(word: str) -> tuple[int, ...]:
    """Parse a FreeWord string into a tuple of signed generator indices."""
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
    return tuple(result)


def canonical_word(word: str) -> tuple[int, ...]:
    """Canonical key treating w and inv(w) as identical."""
    signed = parse_signed(word)
    inverse = tuple(-g for g in reversed(signed))
    return min(signed, inverse)


def abelianization(word: str) -> tuple[int, int, int]:
    """Exponent sum vector in Z^3 for a word over generators {1,2,3}."""
    v = [0, 0, 0]
    i = 0
    while i < len(word):
        c = word[i]
        if c in ('𝑥', '𝑋'):
            sign = 1 if c == '𝑥' else -1
            i += 1
            num = 0
            while i < len(word) and word[i] in SUBSCRIPT:
                num = num * 10 + SUBSCRIPT[word[i]]
                i += 1
            if 1 <= num <= 3:
                v[num - 1] += sign
        else:
            i += 1
    return (v[0], v[1], v[2])


def gcd_of(*nums: int) -> int:
    return reduce(gcd, (abs(x) for x in nums), 0)


def is_free_abelian_quotient(u: tuple, v: tuple) -> bool:
    """
    Check whether Z^3 / <u, v> is torsion-free (free abelian).
    Uses Smith normal form invariant factors:
      d1 = gcd of all entries
      d1*d2 = gcd of all 2x2 minors
    Torsion-free iff d1 in {0,1} and d2 in {0,1}.
    """
    d1 = gcd_of(*u, *v)
    if d1 > 1:
        return False
    # 2×2 minors of the matrix [u; v]
    minors = (
        u[0]*v[1] - u[1]*v[0],
        u[0]*v[2] - u[2]*v[0],
        u[1]*v[2] - u[2]*v[1],
    )
    d2 = gcd_of(*minors)  # equals d1*d2 = 1*d2 since d1=1 (or 0 case)
    return d2 in (0, 1)


def qualifying_pair(two_words: list[str], three_words: list[str]):
    """
    Return the first qualifying (u, v) pair, or None.
    u is from {a, b} (indices 0,1), v is from {c, d} (indices 2,3).
    """
    a, b, c, d = two_words
    three_pairs = [
        frozenset({three_words[0], three_words[1]}),
        frozenset({three_words[2], three_words[3]}),
        frozenset({three_words[4], three_words[5]}),
    ]
    ab_cache: dict[str, tuple] = {}

    def ab(w):
        if w not in ab_cache:
            ab_cache[w] = abelianization(w)
        return ab_cache[w]

    for u, v in [(a, c), (a, d), (b, c), (b, d)]:
        if frozenset({u, v}) in three_pairs and is_free_abelian_quotient(ab(u), ab(v)):
            return (u, v)
    return None


# ── Parse blocks ──────────────────────────────────────────────────────────────
blocks = []
with open(in_file, encoding="utf-8") as f:
    current = []
    for line in f:
        stripped = line.rstrip("\n")
        if stripped == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(stripped)
    if current:
        blocks.append(current)

# ── Filter ────────────────────────────────────────────────────────────────────
kept = []
for block in blocks:
    two_words = three_words = None
    for line in block:
        if line.startswith("TWO:"):
            two_words = parse_words(line)
        elif line.startswith("THREE:"):
            three_words = parse_words(line)
    if two_words and three_words and qualifying_pair(two_words, three_words):
        kept.append(block)

# ── Write ─────────────────────────────────────────────────────────────────────
with open(out_file, "w", encoding="utf-8") as f:
    for block in kept:
        f.write("\n".join(block) + "\n\n")

print(f"{len(blocks):,} blocks in → {len(kept):,} kept → {out_file}")

# ── Also write version with all 4 TWO words pairwise distinct ─────────────────
unique_file = "v1/successes_abelian_unique.txt"
def all_unique_up_to_inverse(block: list[str], prefix: str) -> bool:
    line = next((l for l in block if l.startswith(prefix)), None)
    if line is None:
        return True
    keys = [canonical_word(w) for w in parse_words(line)]
    return len(set(keys)) == len(keys)

unique_kept = [
    b for b in kept
    if all_unique_up_to_inverse(b, "TWO:") and all_unique_up_to_inverse(b, "THREE:")
]

with open(unique_file, "w", encoding="utf-8") as f:
    for block in unique_kept:
        f.write("\n".join(block) + "\n\n")

print(f"{len(kept):,} → {len(unique_kept):,} with all-unique TWO words → {unique_file}")

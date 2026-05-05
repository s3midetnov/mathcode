#!/usr/bin/env python3
"""
Sift successes_sorted.txt in place, removing blocks where any commutator pair
has both words equal. Pairs are consecutive within each line:
  TWO:   w1, w2, w3, w4       — pairs (w1,w2) and (w3,w4)
  THREE: w1, w2, w3, w4, w5, w6 — pairs (w1,w2), (w3,w4), (w5,w6)

Also writes successes_sorted_smaller.txt: one block per equivalence class of
TWO lines under permutations of generator indices {1,2,3}.
"""

from itertools import permutations as _permutations

file = "v1/successes_sorted.txt"

SUBSCRIPT = {'₀': 0, '₁': 1, '₂': 2, '₃': 3, '₄': 4,
             '₅': 5, '₆': 6, '₇': 7, '₈': 8, '₉': 9}

ALL_PERMS: list[dict[int, int]] = [
    {1: p[0], 2: p[1], 3: p[2]} for p in _permutations([1, 2, 3])
]


def has_repeated_pair(words: list[str]) -> bool:
    return any(words[i] == words[i + 1] for i in range(0, len(words) - 1, 2))


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


def apply_perm(word: tuple[int, ...], perm: dict[int, int]) -> tuple[int, ...]:
    return tuple((1 if g > 0 else -1) * perm[abs(g)] for g in word)


def canonical_two(two_line: str) -> tuple:
    """Canonical form of the 4-word TWO line under all 6 permutations of {1,2,3}."""
    raw_words = [w.strip() for w in two_line[two_line.index(":") + 1:].split(",")]
    words = [parse_signed(w) for w in raw_words]
    return min(
        tuple(apply_perm(w, perm) for w in words)
        for perm in ALL_PERMS
    )


def parse_words(line: str) -> list[str]:
    prefix_end = line.index(":") + 1
    return [w.strip() for w in line[prefix_end:].split(",")]


# ── Parse blocks ──────────────────────────────────────────────────────────────
blocks = []
with open(file, encoding="utf-8") as f:
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

total = len(blocks)

# ── Filter ────────────────────────────────────────────────────────────────────
def is_good(block: list[str]) -> bool:
    for line in block:
        if line.startswith("TWO:") or line.startswith("THREE:"):
            if has_repeated_pair(parse_words(line)):
                return False
    return True

blocks = [b for b in blocks if is_good(b)]
removed = total - len(blocks)

# ── Rewrite in place ──────────────────────────────────────────────────────────
with open(file, "w", encoding="utf-8") as f:
    for block in blocks:
        f.write("\n".join(block) + "\n\n")

print(f"Removed {removed:,} blocks with repeated pairs, {len(blocks):,} remain → {file}")

# ── Deduplicate by canonical TWO line → successes_sorted_smaller.txt ─────────
def get_two_line(block: list[str]) -> str:
    for line in block:
        if line.startswith("TWO:"):
            return line
    return ""

smaller_file = "v1/successes_sorted_smaller.txt"
seen_canonical: set[tuple] = set()
deduped = []
for block in blocks:
    two_line = get_two_line(block)
    key = canonical_two(two_line) if two_line else ()
    if key not in seen_canonical:
        seen_canonical.add(key)
        deduped.append(block)

with open(smaller_file, "w", encoding="utf-8") as f:
    for block in deduped:
        f.write("\n".join(block) + "\n\n")

print(f"Deduplicated {len(blocks):,} → {len(deduped):,} up to generator permutation → {smaller_file}")

# ── Further filter: all 4 TWO words pairwise distinct → successes_sorted_unique.txt ──
unique_file = "successes_sorted_unique.txt"
unique_blocks = [
    b for b in deduped
    if (lambda ws: len(set(ws)) == len(ws))(parse_words(get_two_line(b)))
]

with open(unique_file, "w", encoding="utf-8") as f:
    for block in unique_blocks:
        f.write("\n".join(block) + "\n\n")

print(f"Unique TWO words: {len(deduped):,} → {len(unique_blocks):,} → {unique_file}")

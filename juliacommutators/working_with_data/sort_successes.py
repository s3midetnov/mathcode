#!/usr/bin/env python3
"""
Sort successes.txt by total character length of the words on the TWO: line.
Filters out blocks where any word has <= 2 letter switches
(positions where consecutive generator indices differ).
"""

in_file  = "v1/successes.txt"
out_file = "v1/successes_sorted.txt"

SUBSCRIPT = {'₀': 0, '₁': 1, '₂': 2, '₃': 3, '₄': 4,
             '₅': 5, '₆': 6, '₇': 7, '₈': 8, '₉': 9}

def parse_generators(word: str) -> list[int]:
    """Return sequence of generator indices (absolute values) from a printed FreeWord."""
    gens = []
    i = 0
    while i < len(word):
        c = word[i]
        if c in ('𝑥', '𝑋'):
            i += 1
            num = 0
            while i < len(word) and word[i] in SUBSCRIPT:
                num = num * 10 + SUBSCRIPT[word[i]]
                i += 1
            gens.append(num)
        else:
            i += 1
    return gens

def letter_switches(word: str) -> int:
    """Count positions where consecutive generator indices differ."""
    gens = parse_generators(word)
    return sum(1 for a, b in zip(gens, gens[1:]) if a != b)

def is_interesting(block: list[str]) -> bool:
    """True iff every word in the block has > 2 letter switches."""
    for line in block:
        if line.startswith("TWO:") or line.startswith("THREE:"):
            prefix_len = line.index(":") + 1
            words_part = line[prefix_len:].strip()
            for word in words_part.split(","):
                if letter_switches(word.strip()) <= 2:
                    return False
    return True

# ── Parse blocks ─────────────────────────────────────────────────────────────
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

total = len(blocks)
blocks = [b for b in blocks if is_interesting(b)]
filtered = total - len(blocks)

# ── Score each block by total length of words on the TWO: line ───────────────
def two_length(block):
    for line in block:
        if line.startswith("TWO:"):
            words_part = line[len("TWO:"):].strip()
            words = [w.strip() for w in words_part.split(",")]
            return sum(len(w) for w in words)
    return 0

blocks.sort(key=two_length)

# ── Write output ──────────────────────────────────────────────────────────────
with open(out_file, "w", encoding="utf-8") as f:
    for block in blocks:
        f.write("\n".join(block) + "\n\n")

print(f"Filtered {filtered:,} boring blocks, kept {len(blocks):,} → {out_file}")

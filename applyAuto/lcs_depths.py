"""
For each four-tuple (a, b, c, d) in testCases/test_cases.txt,
compute the LCS depth of each word: the unique d such that w lies in γ_d but not γ_{d+1}.

Usage:
    python3 lcs_depths.py            # default MAX_DEG=10
    python3 lcs_depths.py 15         # override MAX_DEG
"""

import os
import sys
from lcs_checker import parse_word, magnus

MAX_DEG = int(sys.argv[1]) if len(sys.argv) > 1 else 10


def lcs_depth(word_str):
    """
    Return the LCS depth d: w ∈ γ_d but w ∉ γ_{d+1}.
    Returns MAX_DEG+1 if depth exceeds MAX_DEG (includes the identity element).
    """
    # Degree-1 check via abelianization: O(n) string scan — no Magnus expansion needed.
    # A word lies in γ_2 iff its abelianization is trivial (net x-count = net y-count = 0).
    net_x = word_str.count('x') - word_str.count('X')
    net_y = word_str.count('y') - word_str.count('Y')
    if net_x != 0 or net_y != 0:
        return 1

    letters = parse_word(word_str)
    if not letters:
        return MAX_DEG + 1  # identity lies in every γ_k

    # Compute the full Magnus expansion once, then find the lowest non-zero degree.
    poly = magnus(letters, MAX_DEG)
    for d in range(1, MAX_DEG + 1):
        if any(len(mono) == d and coeff != 0 for mono, coeff in poly.items()):
            return d

    return MAX_DEG + 1


def main():
    cases_file = os.path.join(os.path.dirname(__file__), "testCases", "test_cases.txt")

    with open(cases_file) as f:
        lines = [line.strip() for line in f if line.strip()]

    inf_label = f">{MAX_DEG}"
    header = f"{'#':>4}  {'depth(a)':>9}  {'depth(b)':>9}  {'depth(c)':>9}  {'depth(d)':>9}"
    print(header)
    print("-" * len(header))

    for i, line in enumerate(lines, 1):
        parts = [s.strip() for s in line.split(",")]
        if len(parts) != 4:
            continue
        depths = [lcs_depth(w) for w in parts]
        if max(depths) < 2:
            continue
        depth_strs = [inf_label if d > MAX_DEG else str(d) for d in depths]
        print(f"{i:>4}  {depth_strs[0]:>9}  {depth_strs[1]:>9}  {depth_strs[2]:>9}  {depth_strs[3]:>9}")


if __name__ == "__main__":
    main()

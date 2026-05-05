#!/usr/bin/env python3
"""
Find success pairs: one line from twoRelators.txt and one from threeRelators.txt.

A pair (a,b,c,d) x (x,y,z,f,t,w) is a SUCCESS when there exist distinct
indices i,j in {0,1,2} such that:
  - the i-th three-relator pair shares a word with {a,b}
  - the j-th three-relator pair shares a word with {c,d}

Words are interned as integer IDs so every set operation is O(1).
Three-relator pair-sets are precomputed once at load time.
"""

from collections import deque
from typing import Optional

# ── Configurable slice limits ────────────────────────────────────────────────
THREE_HEAD = 1_000_000   # first N lines from threeRelators
THREE_TAIL = 1_000_000   # last  N lines from threeRelators
TWO_HEAD   = 1_000_000   # first N lines from twoRelators
TWO_TAIL   = 1_000_000   # last  N lines from twoRelators
# Set any of these to None to disable that limit (load everything).
# ────────────────────────────────────────────────────────────────────────────


def iter_head_tail(path: str, head: Optional[int], tail: Optional[int], field_count: int):
    """
    Yield parsed word-tuples from `path`, keeping only:
      - the first `head` valid lines  (None = unlimited)
      - the last  `tail` valid lines  (None = unlimited)
    Duplicates across the two windows are yielded only once.
    """
    if head is None and tail is None:
        # Fast path: stream everything
        with open(path, encoding="utf-8") as f:
            for line in f:
                words = tuple(w.strip() for w in line.strip().split(","))
                if len(words) == field_count:
                    yield words
        return

    tail_buf: Optional[deque] = deque(maxlen=tail) if tail else None
    head_count = 0
    head_set   = set()   # raw lines already yielded, for dedup

    with open(path, encoding="utf-8") as f:
        for line in f:
            words = tuple(w.strip() for w in line.strip().split(","))
            if len(words) != field_count:
                continue

            # Head window
            if head is None or head_count < head:
                head_count += 1
                head_set.add(words)
                yield words

            # Tail window (always buffer, dedup on flush)
            if tail_buf is not None:
                tail_buf.append(words)

    # Flush tail, skipping anything already yielded in the head window
    if tail_buf:
        for words in tail_buf:
            if words not in head_set:
                yield words


def main():
    three_file = "threeRelatorsF3.txt"
    two_file   = "v1/twoRelatorsF3.txt"
    out_file   = "v1/successes.txt"

    word_id: dict[str, int] = {}

    def intern(w: str) -> int:
        n = word_id.get(w)
        if n is None:
            word_id[w] = n = len(word_id)
        return n

    # ── Phase 1: load and index threeRelators ────────────────────────────────
    label3 = f"first {THREE_HEAD:,}" if THREE_HEAD else ""
    if THREE_TAIL:
        label3 += (" + " if label3 else "") + f"last {THREE_TAIL:,}"
    print(f"Indexing {three_file} ({label3 or 'all'} lines) ...")

    three_pair_sets: list[tuple] = []
    three_raw:       list[tuple] = []
    word_index: dict[int, list[tuple[int, int]]] = {}

    for words in iter_head_tail(three_file, THREE_HEAD, THREE_TAIL, 6):
        li  = len(three_pair_sets)
        ids = tuple(intern(w) for w in words)
        three_pair_sets.append((
            frozenset((ids[0], ids[1])),
            frozenset((ids[2], ids[3])),
            frozenset((ids[4], ids[5])),
        ))
        three_raw.append(words)
        for pi in range(3):
            for wid in (ids[2 * pi], ids[2 * pi + 1]):
                word_index.setdefault(wid, []).append((li, pi))

    print(f"  {len(three_pair_sets):,} three-relator lines loaded, {len(word_id):,} unique words")

    # ── Phase 2: scan twoRelators ────────────────────────────────────────────
    label2 = f"first {TWO_HEAD:,}" if TWO_HEAD else ""
    if TWO_TAIL:
        label2 += (" + " if label2 else "") + f"last {TWO_TAIL:,}"
    print(f"Scanning {two_file} ({label2 or 'all'} lines) ...")

    successes: list[tuple] = []
    two_total = 0

    for words in iter_head_tail(two_file, TWO_HEAD, TWO_TAIL, 4):
        two_total += 1

        ids = tuple(intern(w) for w in words)
        ab  = frozenset((ids[0], ids[1]))
        cd  = frozenset((ids[2], ids[3]))

        candidates: set[int] = set()
        for wid in ids:
            for li, _ in word_index.get(wid, []):
                candidates.add(li)

        for li in candidates:
            p0, p1, p2 = three_pair_sets[li]
            if (
                (ab & p0 and (cd & p1 or cd & p2)) or
                (ab & p1 and (cd & p0 or cd & p2)) or
                (ab & p2 and (cd & p0 or cd & p1))
            ):
                successes.append((words, three_raw[li]))

    print(f"  {two_total:,} two-relator lines scanned")
    print(f"  {len(successes):,} successes found")

    with open(out_file, "w", encoding="utf-8") as out:
        for two, three in successes:
            out.write(f"TWO:   {', '.join(two)}\n")
            out.write(f"THREE: {', '.join(three)}\n\n")

    print(f"Written to {out_file}")


if __name__ == "__main__":
    main()
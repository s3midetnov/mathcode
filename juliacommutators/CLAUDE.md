# juliacommutators

## Mathematical goal

Find elements of F₂ (or F₃) that are products of exactly 2 commutators and also appear as a factor pair in a product of 3 commutators. This is related to the commutator length problem on surface groups.

The two surface group relations are:
- genus-2: `[a,b][c,d] = 1` in π₁(Σ₂)
- genus-3: `[a,b][c,d][e,f] = 1` in π₁(Σ₃)

Commutator convention throughout: `[u,v] = u·v·u⁻¹·v⁻¹`.

## How examples are generated

### twocommutatorproduct.jl — generates `twoRelators.txt`

Works in F₄ = ⟨a,b,c,d⟩. Automorphisms (Nielsen moves on F₄, from `../applyAuto/pi1S2auto.py`):
- A1: a↦ab, A2: b↦ba, A3: c↦cd, A4: d↦dc
- A5: b↦a⁻¹db, c↦a⁻¹dc (and their inverses)

These automorphisms preserve `[a,b][c,d] = 1` when projected via Q.

Projection Q (= map_word1 from Python): `FreeGroupEndomorphism{4}([1],[2],[2],[1])`  
Maps a↦x, b↦y, c↦y, d↦x — collapses F₄ into F₂ = ⟨x,y⟩.

For each automorphism g (from ball enumeration + random walks), outputs the 4-tuple:
```
Q(g(a)), Q(g(b)), Q(g(c)), Q(g(d))
```
Filter: skip if any image is the identity word, or if any image has length ≤ 3.

### threecommutatorproduct.jl — generates `threeRelators.txt`

Works in F₆ = ⟨a,b,c,d,e,f⟩. Automorphisms (from `../applyAuto6/automorphisms.py`): A1–A8 and inverses. These are automorphisms of π₁(Σ₃) — they preserve `[a,b][c,d][e,f] = 1`.

Projection Q (= map_word3 from Python): `FreeGroupEndomorphism{6}([1],[2],[3],[3],[2],[1])`  
Maps a,f↦x, b,e↦y, c,d↦z — gives 6 words in F₃ = ⟨x,y,z⟩.

Then applies a variable homomorphism `homo32(im1,im2,im3)`: F₃→F₂, sending x↦im1, y↦im2, z↦im3, where im1,im2,im3 are short words in F₂ = ⟨1,2⟩ drawn from `ball(gens_2_small, 3)`.

For each (g, im1, im2, im3) outputs the 6-tuple of F₂ words:
```
homo32(im1,im2,im3)(Q(g(a))), ..., homo32(im1,im2,im3)(Q(g(f)))
```
Filter: skip if any of the 6 intermediate Q-images (before homo32) has length ≤ 3, or if any final image has length ≤ 3.

**Key invariant**: for any g in the automorphism group, the 3-commutator product `[im1,im2][im3,im4][im5,im6]` is always the identity in F₂ (because Q∘g preserves the genus-3 relation and homo32 is a homomorphism).

### Sampling strategy (both files)

Two phases written to the same file:
1. **Ball enumeration**: exhaustive, `ball(gens, 3–4)` — systematic short words
2. **Random walks**: `foldl(*, rand(gens, n))` for n ~ rand(10:rand(10:30)) — long words, same as Python's `random_iter`

## Success condition (`find_successes.py`)

A pair of lines — `(a,b,c,d)` from twoRelators and `(x,y,z,f,t,w)` from threeRelators — is a **success** if there exists an injective matching from the two two-relator pairs to two distinct three-relator pairs, each sharing at least one word:

- Three-relator pairs: P₀={x,y}, P₁={z,f}, P₂={t,w}
- Need distinct i≠j with {a,b}∩Pᵢ ≠ ∅ and {c,d}∩Pⱼ ≠ ∅

Example successes: `(a,b,c,d)` vs `(a,y,z,c,t,w)` ✓ (a∈P₀, c∈P₁, i≠j)  
Non-success: `(a,b,c,d)` vs `(a,d,z,f,t,w)` — both a and d land in the same P₀={a,d}.

Implementation: words are interned as integer IDs; three-relator pair-sets are precomputed as frozensets of ints; for each two-relator line only three-relator lines sharing at least one word are checked (indexed lookup).

## Running

```bash
./pipeline.sh          # generates twoRelators.txt, threeRelators.txt, successes.txt
```

Or individually:
```bash
julia twocommutatorproduct.jl
julia threecommutatorproduct.jl
python3 find_successes.py
```

## Files

| File | Purpose |
|---|---|
| `twocommutatorproduct.jl` | Generates 2-commutator examples (F₄ automorphisms + Q projection) |
| `threecommutatorproduct.jl` | Generates 3-commutator examples (F₆ automorphisms + Q + homo32) |
| `experiment.jl` | Earlier experiment: surface group automorphisms on F₄, prints [a,b][c,d] products |
| `commlength.jl` | Library: commutator length computation (`cl`, `clbound`, `clsols`) |
| `find_successes.py` | Matches twoRelators vs threeRelators, writes successes.txt |
| `pipeline.sh` | Runs all three steps in order |
| `twoRelators.txt` | Output: one line per example, 4 comma-separated F₂ words |
| `threeRelators.txt` | Output: one line per example, 6 comma-separated F₂ words |
| `successes.txt` | Output: matched pairs |

## Dependencies

- Julia package: `GroupElements` at `~/Desktop/GroupElements.jl` (local, not registered)
- Python 3 (stdlib only) for `find_successes.py`
- `GroupElements` types used: `FreeWord{N}`, `FreeGroupEndomorphism{N}`, `FreeGroupAutomorphism{N}`, `ball(gens, radius)`

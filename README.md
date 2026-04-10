# MathCode: Collections of Mathematical Computations

This repository contains a collection of scripts, notebooks, and programs for various mathematical computations, including group theory, Lie algebras, and symbolic algebra.

## Braid Groups (`braidGroups/`)
Computations related to braid groups.
- `dehornoy/`: Implementation of the Dehornoy reduction algorithm (word problem solver). This is a copy of [abhikpal/dehornoy](https://github.com/abhikpal/dehornoy).
- SageMath notebooks for other braid group computations.

## Apply Automorphisms (`applyAuto/`)
- Tools for applying automorphisms of π₁(S_2) and generating test cases of group presentations.
- Includes free group utilities, random automorphism sampling, abelianization checks, and batch processing scripts.

## Commutators (`commutators/`)
- `commutators.py`: Iteratively builds Mal'tsev bases.
- `usecommutators.ipynb`: Examples and usage.

## Lie Algebras (`LieAlgebras/`)
- `gapLieRingCompute/`: Checks if elements are (non-)zero in nilpotent quotients of specific Lie algebras.
- `iterateRipsElements/`: Python script for generating examples satisfying certain conditions in $D_4$.
- `findBasisForLie/`: GAP and Python scripts for finding bases and working with congruences in Lie algebras.
    - Usage (on macOS): `\gap -q -b unified_search.g`

## Symmetric Group Ring (`symmetricGroupRing/`)
- SageMath code for computations within the symmetric group ring.

## Other Utilities
- `freegroup.py`: Basic implementation of free group word reduction and automorphisms.
- `automorphismspi1S2.py`: Specific automorphism definitions and projections.
- `sudokuGraphs/`: Exploration of Sudoku-related graphs.


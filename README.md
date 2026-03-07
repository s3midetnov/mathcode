# README: some math-related code

## braidGroups
Some computations in the braid groups. 
The folder "dehornoy" contains a copy of the repo https://github.com/abhikpal/dehornoy with an implementation of the Dehornoy reduction algorithm.
This serves as a way to solve word problem in the braid group.
Other notebooks contain SageMath code for some other computations.

## commutators
The file commutators.py builds Mal'tsev bases iteratively. 
The notebook contains some examples.

## LieAlgebras
The folder gapLieRingCompute contains a file that reads the file input.txt and tells whether some element is (non-)zero in the nilpotent quotient of a specific Lie algebra defined by the read data.
The folder iterateRipsElements contains a python script that creates a lot of examples of (k1, k2, k3, a11, ..., a33, b12, b23, b13) satisfying conditions that the corresponding element lies in D_4. 
The folder findBasisForLie contains a script isZeroModLCS.g which is a version of gapLieRingCompute/process.g, a script findBasisCongruences.g which finds a basis for subgroup of Z^3 defined by a set of congruences, 
a script interface.py which allows to apply iteratively the two scripts above and the file unified_search.g which is a version of the script interface.py but full in gap. 

N.B. Usage of gap is via 
```bash
\gap -q -b unified_search.g
```
(on MacOS). 

## symmetricGroupRing
Contains some SageMath code for computations in the symmetric group ring.


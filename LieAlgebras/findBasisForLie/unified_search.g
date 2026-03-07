LoadPackage("liering");

Reset(GlobalMersenneTwister, 876543);

# 1. Define the function to find the subgroup basis
FindSubgroupBasis := function(k1, k2, k3, a)
    local C, M, W, W_trans, N, N_sub, basis, i;

    # Define the 9x3 coefficient matrix C
    C := [
        [ a[2][1], a[3][1], 0 ],
        [ a[2][2], a[3][2], 0 ],
        [ a[2][3], a[3][3], 0 ],
        [ 2^(k2-k1)*a[1][1], 0, -a[3][1] ],
        [ 2^(k2-k1)*a[1][2], 0, -a[3][2] ],
        [ 2^(k2-k1)*a[1][3], 0, -a[3][3] ],
        [ 0, 2^(k3-k1)*a[1][1], 2^(k3-k2)*a[2][1] ],
        [ 0, 2^(k3-k1)*a[1][2], 2^(k3-k2)*a[2][2] ],
        [ 0, 2^(k3-k1)*a[1][3], 2^(k3-k2)*a[2][3] ]
    ];

    # Define the 9x9 diagonal modulo matrix M
    M := DiagonalMat([
        2^k1, 2^k1, 2^k1,
        2^k1, 2^k2, 2^k2,
        2^k1, 2^k2, 2^k3
    ]);

    # Construct the 9x12 block matrix W = (C | M)
    W := [];
    for i in [1..9] do
        Add(W, Concatenation(C[i], M[i]));
    od;

    # Find the right nullspace of W
    W_trans := TransposedMat(W);
    N := NullspaceIntMat(W_trans);

    # Extract the first 3 columns corresponding to [b12, t, b23]
    N_sub := List(N, row -> row{[1..3]});

    # Find a Z-basis
    basis := BaseIntMat(N_sub);

    return basis;
end;

# 2. Initialize global structures for the Lie Ring once
L := FreeLieRing(Integers, ["x1", "x2", "x3", "x4"]);
x1 := L.x1; x2 := L.x2; x3 := L.x3; x4 := L.x4;

# 3. Search parameters
k_min := 4; k_max := 15;
a_min := -12; a_max := 12;

found_false := false;
iterations := 0;

Print("Starting randomized search...\n");
# 4. Main Search Loop
while not found_false do
    iterations := iterations + 1;

    # Generate random parameters
    k1 := Random([k_min .. k_max - 4]);
    k2 := Random([k1 + 2 .. k_max - 2]);
    k3 := Random([k2 + 2 .. k_max]);

    aa12 := Random([a_min .. a_max]);
    aa13 := Random([a_min .. a_max]);
    aa23 := Random([a_min .. a_max]);
    a := [
        [0, aa12, aa13],
        [aa12, 0, aa23],
        [aa13, aa23, 0]
    ];

    Print("\n--- Iteration ", iterations, " ---\n");
    Print("Randomized values: k1 = ", k1, ", k2 = ", k2, ", k3 = ", k3, "\n");
    Print(" a11 = ", a[1][1], ", a12 = ", a[1][2], ", a13 = ", a[1][3], "\n");
    Print(" a21 = ", a[2][1], ", a22 = ", a[2][2], ", a23 = ", a[2][3], "\n");
    Print(" a31 = ", a[3][1], ", a32 = ", a[3][2], ", a33 = ", a[3][3], "\n");

    # Find the basis
    basis := FindSubgroupBasis(k1, k2, k3, a);
    Print("Output from GAP for basis:\n", basis, "\n");

    # --- NEW: Check if the basis is diagonal and skip if true ---
    if IsDiagonalMat(basis) then
        Print("Basis is diagonal. Skipping this example...\n");
        continue;
    fi;
    # ------------------------------------------------------------

    # Iterate through the elements of the found basis
    for basic_element in basis do
        # GAP lists are 1-indexed (unlike Python which is 0-indexed)
        b12 := basic_element[1];
        b13 := basic_element[2] * (2^(k3 - k2));
        b23 := basic_element[3];

        param_string := Concatenation(
            "k1=", String(k1), ", k2=", String(k2), ", k3=", String(k3),
            ", a11=", String(a[1][1]), ", a12=", String(a[1][2]), ", a13=", String(a[1][3]),
            ", a21=", String(a[2][1]), ", a22=", String(a[2][2]), ", a23=", String(a[2][3]),
            ", a31=", String(a[3][1]), ", a32=", String(a[3][2]), ", a33=", String(a[3][3]),
            ", b12=", String(b12), ", b13=", String(b13), ", b23=", String(b23)
        );

        # Construct the relations using the parameters
        R := [
            2^k1 * x1 - a[1][1] * (x4 * x1) - a[1][2] * (x4 * x2) - a[1][3] * (x4 * x3),
            2^k2 * x2 - a[2][1] * (x4 * x1) - a[2][2] * (x4 * x2) - a[2][3] * (x4 * x3),
            2^k3 * x3 - a[3][1] * (x4 * x1) - a[3][2] * (x4 * x2) - a[3][3] * (x4 * x3)
        ];

        K := FpLieRing(L, R : maxdeg := 3);
        f := CanonicalProjection(K);

        # Check the condition
        check_val := f( (2^k2 * b12) * (x1 * x2) +
                        (2^k2 * b13) * (x1 * x3) +
                        (2^k3 * b23) * (x2 * x3) );

        if not IsZero(check_val) then
            Print("\n[FALSE] THE ELEMENT IS NON-ZERO MOD LCS WITH PARAMETERS:\n", param_string, "\n");
            Print("Found [FALSE] element. Stopping.\n");
            found_false := true;
            break; # Break out of the basis for-loop
        else
            Print("[TRUE] element is zero mod lcs with parameters: ", param_string, "\n");
        fi;
    od;
od;

QUIT;
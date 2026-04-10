# 1. Define the 5 base automorphisms as 4x4 matrices
M1 := [[1, 0, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
M2 := [[1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
M3 := [[1, -1, -1, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 1, 1, 1]];
M4 := [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 1, 1]];
M5 := [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]];

# 2. Store them and their inverses in a list of tuples: [Matrix, "Name"]
# This helps us keep track of the sequence as a readable string
generators := [
    [M1, "M1"], [M2, "M2"], [M3, "M3"], [M4, "M4"], [M5, "M5"],
    [M1^-1, "M1^-1"], [M2^-1, "M2^-1"], [M3^-1, "M3^-1"],
    [M4^-1, "M4^-1"], [M5^-1, "M5^-1"]
];

# 3. Define the projection matrix F mapping Z^4 to Z^2
F := [
    [1, 0, 0, 1],
    [0, 1, 1, 0]
];

# Function to test a random sequence
TestRandomSequence := function( seq_length )
    local M, FM, col1, col3, basis_matrix, det, is_basis, seq_names, i, choice;

    seq_names := [];
    M := IdentityMat( 4 );

    # Pick random generators and multiply them
    for i in [1..seq_length] do
        choice := Random( generators );
        Add( seq_names, choice[2] );
        M := M * choice[1];
    od;

    # Apply the projection map f
    FM := F * M;

    # Extract the 1st and 3rd columns.
    # In GAP, matrices are lists of row lists. FM[row][col]
    col1 := [ FM[1][1], FM[2][1] ];
    col3 := [ FM[1][3], FM[2][3] ];

    # Create the 2x2 matrix.
    # Since det(A) = det(A^T), we can safely use col1 and col3 as rows
    # for the determinant calculation to save an extra transpose step.
    basis_matrix := [ col1, col3 ];
    det := DeterminantMat( basis_matrix );

    # It is a basis of Z^2 if and only if the absolute value of the determinant is 1
    is_basis := (AbsInt(det) = 1);

    # Return a record with the results
    return rec(
        sequence := seq_names,
        determinant := det,
        isBasis := is_basis
    );
end;

# --- Example Execution ---
RunExperiments := function()
    local found_basis, found_non_basis, attempts, result;

    found_basis := false;
    found_non_basis := false;
    attempts := 0;

    Print("Testing random sequences of length 5...\n\n");

    while attempts < 100 do
        result := TestRandomSequence( 5 );

        if result.isBasis then
            Print("SUCCESSFUL SEQUENCE FOUND:\n");
            Print("Sequence: ", result.sequence, "\n");
            Print("Determinant: ", result.determinant, "\n\n");
            found_basis := true;

        elif not result.isBasis then
            Print("FAILED SEQUENCE FOUND:\n");
            Print("Sequence: ", result.sequence, "\n");
            Print("Determinant: ", result.determinant, "\n\n");
            found_non_basis := true;
        fi;

        attempts := attempts + 1;
    od;
end;

# Call the experiment runner
RunExperiments();
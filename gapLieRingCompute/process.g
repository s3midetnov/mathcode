# process.g
LoadPackage("liering");

# Initialize global structures once
L := FreeLieRing(Integers, ["x1", "x2", "x3", "x4"]);
x1 := L.x1; x2 := L.x2; x3 := L.x3; x4 := L.x4;

# Open the input file
stream := InputTextFile("input.txt");

if stream = fail then
    Print("Error: input.txt not found.\n");
else
    Print("Starting optimized processing...\n");
    line_num := 0;

    # Read and process line by line
    while true do
        line := ReadLine(stream);
        if line = fail then break; fi; # End of file
        
        # Count the line immediately
        line_num := line_num + 1;
        
        # Create a clean version of the line for printing (modifying in-place)
        clean_line := ShallowCopy(line);
        RemoveCharacters(clean_line, "\n\r");
        
        # Split purely by comma first
        parts := SplitString(line, ",");
        if Length(parts) = 0 then continue; fi;
        
        # Parse the line into a GAP Record
        params := rec();
        for p in parts do
            kv := SplitString(p, "=");
            if Length(kv) = 2 then
                # GAP modifies strings IN-PLACE! It does not return a new string.
                key := kv[1];
                RemoveCharacters(key, " \t\n\r");
                
                val_str := kv[2];
                RemoveCharacters(val_str, " \t\n\r");
                
                # Only try to convert if there is actually a number
                if Length(val_str) > 0 then
                    params.(key) := Int(val_str); 
                fi;
            fi;
        od;
        
        # Ensure we actually parsed data before calculating
        if not IsBound(params.k1) then 
            Print("\n[WARN] Skipping unparsable line ", line_num, ": ", clean_line);
            continue; 
        fi;

        # Construct the relations using the parameters
        R := [ 
            2^(params.k1) * x1 - (params.a11) * (x4 * x1) - (params.a12) * (x4 * x2) - (params.a13) * (x4 * x3),
            2^(params.k2) * x2 - (params.a21) * (x4 * x1) - (params.a22) * (x4 * x2) - (params.a23) * (x4 * x3),
            2^(params.k3) * x3 - (params.a31) * (x4 * x1) - (params.a32) * (x4 * x2) - (params.a33) * (x4 * x3)
        ];
        
        K := FpLieRing(L, R : maxdeg := 3);
        f := CanonicalProjection(K);
        
        # Check the condition
        check_val := f( (2^(params.k2) * params.b12) * (x1 * x2) + 
                        (2^(params.k2) * params.b13) * (x1 * x3) + 
                        (2^(params.k3) * params.b23) * (x2 * x3) );
                        
        if not IsZero(check_val) then
            Print("\n[FAIL] Output is False for parameters: ", clean_line);
        fi;
        
        # Print progress
        if line_num mod 10 = 0 then
            Print("\rProcessing line ", line_num, " ...");
        fi;
    od;

    CloseStream(stream);
    Print("\nProcessing complete. Total lines read: ", line_num, "\n");
fi;

QUIT;

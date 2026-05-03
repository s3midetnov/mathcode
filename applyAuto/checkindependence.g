LoadPackage("nq");

CosetTableDefaultMaxLimit := 100000;

ParseWord := function(str, x, y)
    local result, c, i;
    result := One(x);
    for i in [1..Length(str)] do
        c := str[i];
        if c = 'x' then result := result * x;
        elif c = 'X' then result := result * x^-1;
        elif c = 'y' then result := result * y;
        elif c = 'Y' then result := result * y^-1;
        fi;
    od;
    return result;
end;

ProcessTriple := function(rel1str, rel2str, rel3str)
    local F, x, y, rels, G, ord, res, Q, cl;
    F := FreeGroup("x", "y");
    x := F.1;
    y := F.2;

    rels := [
        ParseWord(rel1str, x, y),
        ParseWord(rel2str, x, y),
        ParseWord(rel3str, x, y)
    ];

    G := F / rels;

    res := CALL_WITH_CATCH(function() return Order(G); end, []);

    if res[1] = false then
        Print("  Order: FAILED (too large or hopeless)\n");
    else
        ord := res[2];
        Print("  Order of G: ", ord, "\n");
        if ord = infinity then
            Print("  Group is infinite. Nilpotent quotients:\n");
            for cl in [1..6] do
                res := CALL_WITH_CATCH(function()
                    return NilpotentQuotient(G, cl);
                end, []);
                if res[1] = false then
                    Print("    Class ", cl, ": FAILED\n");
                else
                    Q := res[2];
                    Print("    Class ", cl,
                          ": Hirsch length = ", HirschLength(Q),
                          ", Size = ", Size(Q), "\n");
                fi;
            od;
        else
            Print("  Is nilpotent: ", IsNilpotent(G), "\n");
            Print("  Is solvable:  ", IsSolvable(G), "\n");
        fi;
    fi;
end;

filename := "testCases/reducedb.txt";
lines := SplitString(StringFile(filename), "\n");

lineNum := 0;
for line in lines do
    line := NormalizedWhitespace(line);
    if Length(line) = 0 then continue; fi;

    lineNum := lineNum + 1;
    parts := SplitString(line, ",");

    if Length(parts) <> 3 then
        Print("Line ", lineNum, ": SKIPPED (expected 3 comma-separated words, got ",
              Length(parts), ")\n");
        continue;
    fi;

    r1 := NormalizedWhitespace(parts[1]);
    r2 := NormalizedWhitespace(parts[2]);
    r3 := NormalizedWhitespace(parts[3]);

    Print("Line ", lineNum, ": [", r1, ", ", r2, ", ", r3, "]\n");
    CALL_WITH_CATCH(ProcessTriple, [r1, r2, r3]);
    Print("\n");
od;
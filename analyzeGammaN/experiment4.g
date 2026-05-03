LoadPackage("nq");;

F := FreeGroup("a", "b");;
a := F.1;;
b := F.2;;

# ------------------------------------------------------------
# Nilpotent quotient + gamma test
# ------------------------------------------------------------

NilpotentQuotientMap := function(F, c)
    local H, Fgens, Hgens;
    H := NilpotentQuotient(F, c);
    Fgens := GeneratorsOfGroup(F);
    Hgens := GeneratorsOfGroup(H);
    return GroupHomomorphismByImages(F, H, Fgens, Hgens{[1..Length(Fgens)]});
end;;

InGamma := function(w, n)
    local phi;
    if n <= 1 then return true; fi;
    phi := NilpotentQuotientMap(F, n - 1);
    return IsOne(Image(phi, w));
end;;

CheckKStep := function(k, x, y)
    local w;
    w := Comm(a, x) * Comm(b, y);
    return InGamma(w, k + 2);
end;;

# ------------------------------------------------------------
# Incremental search up to k = 4
# ------------------------------------------------------------

SearchUpTo4 := function(bound, outname)
    local c2, u, v, w1, w2, w3,
          p, q, r, s,
          i, j, m, n,
          a1, a2, a3, b1, b2, b3,
          x1, y1, x2, y2, x3, y3, x4, y4,
          sol1, sol2, sol3, sol4,
          rec1, rec2, rec3;

    if outname = fail then
        outname := "step4-results.md";
    fi;

    # commutators
    c2 := Comm(a, b);;
    u  := Comm(a, c2);;
    v  := Comm(b, c2);;

    w1 := Comm(a, u);;
    w2 := Comm(b, u);;
    w3 := Comm(b, v);;

    sol1 := [];;
    sol2 := [];;
    sol3 := [];;
    sol4 := [];;

    PrintTo(outname, "# Incremental search up to k = 4\n\n");;
    AppendTo(outname, "bound = ", String(bound), "\n\n");;

    # -----------------------
    # STEP 1
    # -----------------------
    for p in [-bound..bound] do
        for q in [-bound..bound] do
            x1 := a^p * b^q;
            for r in [-bound..bound] do
                for s in [-bound..bound] do
                    y1 := a^r * b^s;
                    if CheckKStep(1, x1, y1) then
                        Add(sol1, rec(x:=x1, y:=y1));
                    fi;
                od;
            od;
        od;
    od;

    # -----------------------
    # STEP 2
    # -----------------------
    for rec1 in sol1 do
        x1 := rec1.x; y1 := rec1.y;
        for i in [-bound..bound] do
            x2 := x1 * c2^i;
            for j in [-bound..bound] do
                y2 := y1 * c2^j;
                if CheckKStep(2, x2, y2) then
                    Add(sol2, rec(x:=x2, y:=y2));
                fi;
            od;
        od;
    od;

    # -----------------------
    # STEP 3
    # -----------------------
    for rec2 in sol2 do
        x2 := rec2.x; y2 := rec2.y;
        for i in [-bound..bound] do
            for j in [-bound..bound] do
                x3 := x2 * u^i * v^j;
                for m in [-bound..bound] do
                    for n in [-bound..bound] do
                        y3 := y2 * u^m * v^n;
                        if CheckKStep(3, x3, y3) then
                            Add(sol3, rec(x:=x3, y:=y3));
                        fi;
                    od;
                od;
            od;
        od;
    od;

    # -----------------------
    # STEP 4
    # -----------------------
    AppendTo(outname, "## k = 4 solutions\n\n");;

    for rec3 in sol3 do
        x3 := rec3.x; y3 := rec3.y;

        for a1 in [-bound..bound] do
            for a2 in [-bound..bound] do
                for a3 in [-bound..bound] do
                    x4 := x3 * w1^a1 * w2^a2 * w3^a3;

                    for b1 in [-bound..bound] do
                        for b2 in [-bound..bound] do
                            for b3 in [-bound..bound] do
                                y4 := y3 * w1^b1 * w2^b2 * w3^b3;

                                if CheckKStep(4, x4, y4) then
                                    Add(sol4, rec(x:=x4, y:=y4));
                                    AppendTo(outname,
                                        "- x4 = ", String(x4), "\n  y4 = ",
                                        String(y4), "\n\n");
                                fi;

                            od;
                        od;
                    od;

                od;
            od;
        od;

    od;

    AppendTo(outname, "\nTotal k=4 solutions: ", String(Length(sol4)), "\n");;

    return sol4;
end;;

# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------

results := SearchUpTo4(1, "step4-results.md");;
Print("Done. Found ", Length(results), " solutions at k=4\n");;

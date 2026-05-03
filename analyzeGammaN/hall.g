LoadPackage("nq");;

F := FreeGroup("a", "b");;
a := F.1;; b := F.2;;

# F -> F/gamma_{c+1}, the class-c nilpotent quotient
NilpotentQuotientMap := function(F, c)
    local H, Fgens, Hgens;
    H := NilpotentQuotient(F, c);
    Fgens := GeneratorsOfGroup(F);
    Hgens := GeneratorsOfGroup(H);
    return GroupHomomorphismByImages(F, H, Fgens, Hgens{[1..Length(Fgens)]});
end;;

# True iff w lies in gamma_n(F)  (gamma_1 = F, gamma_2 = [F,F], ...)
InGamma := function(w, n)
    local phi;
    if n <= 1 then return true; fi;
    phi := NilpotentQuotientMap(F, n - 1);
    return IsOne(Image(phi, w));
end;;

# Given x, y in F (written in basic form with commutators of weight <= k),
# check whether [a, x]*[b, y] lies in gamma_{k+2}.
CheckKStep := function(k, x, y)
    local w, result;
    w := Comm(a, x) * Comm(b, y);
    result := InGamma(w, k + 2);
    if result then
        Print("YES: [a,x]*[b,y] in gamma_", k + 2, "\n");
    else
        # Show the image in F/gamma_{k+2} to see how far it misses
        Print("NO:  image in class-", k + 1, " quotient = ",
              Image(NilpotentQuotientMap(F, k + 1), w), "\n");
    fi;
    return result;
end;;

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

Print("=== k=1 ===\n");
# In F/gamma_3 (class-2 quotient):  [a, a^p*b^q]*[b, a^r*b^s] = [a,b]^{q-r}
# so the condition is q = r  (exp of b in x = exp of a in y).

# q=3, r=3  -> YES
CheckKStep(1, a^2*b^3, a^3*b^5);

# q=3, r=2  -> NO
CheckKStep(1, a^2*b^3, a^2*b^5);

Print("\n=== k=2 ===\n");
# x = a^2 * b^3 * Comm(b,a),  y = a^3 * b^5 * Comm(b,a)^2
# (prefixes of weight <= 1 match the k=1 example above with q=r=3)
x2 := a^2 * b^3 * Comm(b,a);;
y2 := a^3 * b^5 * Comm(b,a)^2;;
CheckKStep(2, x2, y2);

Print("\n=== image diagnostic (class 1..5) ===\n");
w := Comm(a, x2) * Comm(b, y2);;
for c in [1..5] do
    Print("  F/gamma_", c+1, ": ", Image(NilpotentQuotientMap(F, c), w), "\n");
od;

F := FreeGroup("t1", "t2", "t3", "t12", "t23", "t13", "t123");
t1 := F.1;
t2 := F.2;
t3 := F.3;
t12 := F.4;
t23 := F.5;
t13 := F.6;
t123 := F.7;

rels := [
    t1^2,
    t2^2,
    t3^2,
    t12^2,
    t23^2,
    t13^2,
    t123^2, # commutators [t1, ...]
    t1 * t2 * t1^-1 * t2^-1, # don't intersect
    t1 * t3 * t1^-1 * t3^-1,
    t1 * t23 * t1^-1 * t23^-1,
    t1 * t12 * t1^-1 * t12^-1, # subset
    t1 * t13 * t1^-1 * t13^-1,
    t1 * t123 * t1^-1 * t123^-1,
    t2 * t3 * t2^-1 * t3^-1, # don't intersect
    t2 * t13 * t2^-1 * t13^-1,
    t2 * t12 * t2^-1 * t12^-1, #subset
    t2 * t23 * t2^-1 * t23^-1,
    t2 * t123 * t2^-1 * t123^-1,
    t3 * t12 * t3^-1 * t12^-1,
    t3 * t12 * t3^-1 * t12^-1, # don't intersect
    t3 * t13 * t3^-1 * t13^-1, # subset
    t3 * t23 * t3^-1 * t23^-1,
    t3 * t123 * t3^-1 * t123^-1,
    t12 * t123 * t12^-1 * t123^-1,
    t13 * t123 * t13^-1 * t123^-1,
    t23 * t123 * t23^-1 * t123^-1
];

G := F / rels;

T1 := G.1;
T2 := G.2;
T3 := G.3;
T12 := G.4;
T23 := G.5;
T13 := G.6;
T123 := G.7;

# generators: t123 * t12

gensH := [T123 * T12, T23 * T2, T13 * T3, T3];


H := Subgroup(G, gensH);
iso := IsomorphismFpGroup(H);
Hfp := Image(iso);
Print(GeneratorsOfGroup(Hfp), "\n");
Print(RelatorsOfFpGroup(Hfp), "\n");
Print(T1 in H, "\n");
Print(T2 in H, "\n");
Print(T3 in H, "\n");
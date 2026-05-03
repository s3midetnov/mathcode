LoadPackage("kbmag");

F := FreeGroup("x", "y");
x := F.1; y := F.2;

# Define your relations as a list
rels := [ y^2 * x^-1 * y^-1 * x^-1, x * y * x^-3 * y * x * y^-1 ];

# Create the finitely presented group
G := F / rels;
w1 := x * y * x^-1 * x^-1 * y * x * y^-1 * y^-1;
w2 := y * x^-1 * y * x^-1 * y^-1 * x * x * x * y^-1 * x^-1;

group_size := Size(G);
Print(group_size, "\n");

rws := KBMAGRewritingSystem(G);
KnuthBendix(rws);
Print("w1 = ", ReducedWord(rws, w1), "\n");
Print("w2 = ", ReducedWord(rws, w2), "\n");

hom := NaturalHomomorphism(F, G);
w1_in_G := Image(hom, w1);
w2_in_G := Image(hom, w2);

sub1 := Subgroup(G, [w1_in_G]);
sub2 := Subgroup(G, [w2_in_G]);

# Compute the normal closures
norm1 := NormalClosure(G, sub1);
norm2 := NormalClosure(G, sub2);

# Compare them
Print("comparing normal closures\n");
Print(norm1 = norm2);
LoadPackage("nq");

F := FreeGroup("x", "y");
x := F.1;
y := F.2;

rels := [
    x^3 * y^-2,
    x^2*y^2*x^2*y*x^-1*y*x^-1*y*x^2*y*x^-2,
    y^-1*x^-1*y * x^-2
];

G := F / rels;

# First: check if the group is finite and what it is
Print("Attempting to compute order...\n");
ord := Order(G);
Print("Order of G: ", ord, "\n");

# Check nilpotent quotients at each class
for cl in [1..6] do
    Q := NilpotentQuotient(G, cl);
    Print("Class ", cl,
          ": Hirsch length = ", HirschLength(Q),
          ", Size = ", Size(Q), "\n");
od;
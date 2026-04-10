F := FreeGroup("x", "y");;
x := F.1;; y := F.2;;
G := F / [
x*y^-1*x^-1*y^-1*x^-1*y^-1*x*y^-1*x^-1*y*x*y*x^-1*y^-1,
x*y^-1*x^-1*y^-1*y^-1*x^-1*y^-1*x*y*y*y,
x^2,
y^2
];;
Size(G);
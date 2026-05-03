LoadPackage("polycyclic");
LoadPackage("nq");
LoadPackage("DeepThought");


F := FreeGroup(2);
G := NilpotentQuotient(F, 7);
coll := Collector(G);;

DTObj := DTP_DTObjFromCollector(coll);
Display(DTObj);

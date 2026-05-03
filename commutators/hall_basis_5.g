# Hall basis for F2 = <a,b>, weight <= 5
# Requires: F := FreeGroup("a","b");;
#
# hallBasis[i] is a record with fields:
#   index  -- position in the Hall order (1-based)
#   weight -- weight of the basic commutator
#   label  -- string name, e.g. "[b,a]"
#   elt    -- the element of F as a GAP object

hallBasis := [
    rec( index := 1, weight := 1, label := "a", elt := F.1 ),
    rec( index := 2, weight := 1, label := "b", elt := F.2 ),
    rec( index := 3, weight := 2, label := "[b,a]", elt := Comm(F.2,F.1) ),
    rec( index := 4, weight := 3, label := "[[b,a],a]", elt := Comm(Comm(F.2,F.1),F.1) ),
    rec( index := 5, weight := 3, label := "[[b,a],b]", elt := Comm(Comm(F.2,F.1),F.2) ),
    rec( index := 6, weight := 4, label := "[[[b,a],a],a]", elt := Comm(Comm(Comm(F.2,F.1),F.1),F.1) ),
    rec( index := 7, weight := 4, label := "[[[b,a],a],b]", elt := Comm(Comm(Comm(F.2,F.1),F.1),F.2) ),
    rec( index := 8, weight := 4, label := "[[[b,a],b],b]", elt := Comm(Comm(Comm(F.2,F.1),F.2),F.2) ),
    rec( index := 9, weight := 5, label := "[[[b,a],a],[b,a]]", elt := Comm(Comm(Comm(F.2,F.1),F.1),Comm(F.2,F.1)) ),
    rec( index := 10, weight := 5, label := "[[[b,a],b],[b,a]]", elt := Comm(Comm(Comm(F.2,F.1),F.2),Comm(F.2,F.1)) ),
    rec( index := 11, weight := 5, label := "[[[[b,a],a],a],a]", elt := Comm(Comm(Comm(Comm(F.2,F.1),F.1),F.1),F.1) ),
    rec( index := 12, weight := 5, label := "[[[[b,a],a],a],b]", elt := Comm(Comm(Comm(Comm(F.2,F.1),F.1),F.1),F.2) ),
    rec( index := 13, weight := 5, label := "[[[[b,a],a],b],b]", elt := Comm(Comm(Comm(Comm(F.2,F.1),F.1),F.2),F.2) ),
    rec( index := 14, weight := 5, label := "[[[[b,a],b],b],b]", elt := Comm(Comm(Comm(Comm(F.2,F.1),F.2),F.2),F.2) )
];

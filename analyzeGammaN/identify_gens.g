LoadPackage("nq");;

K := 7;;

F := FreeGroup("a", "b");;
fa := F.1;; fb := F.2;;

BuildWeightData := function(K)
    local H, hgens, ngens, sizes, weights, weightGroups, w, i, prev;
    H     := NilpotentQuotient(F, K + 1);;
    hgens := GeneratorsOfGroup(H);;
    ngens := Length(hgens);;
    sizes := [];;
    for w in [1..K+1] do sizes[w] := Length(GeneratorsOfGroup(NilpotentQuotient(F,w)));; od;;
    weights := ListWithIdenticalEntries(ngens, 0);;
    for w in [1..K+1] do
        prev := 0;; if w > 1 then prev := sizes[w-1];; fi;;
        for i in [prev+1..sizes[w]] do weights[i] := w;; od;;
    od;;
    weightGroups := [];;
    for w in [1..K+1] do
        weightGroups[w] := Filtered([1..ngens], i -> weights[i] = w);;
    od;;
    return rec(H:=H, hgens:=hgens, ngens:=ngens,
               weights:=weights, weightGroups:=weightGroups);;
end;;

data     := BuildWeightData(K);;
H        := data.H;;
hgens    := data.hgens;;
ngens    := data.ngens;;
weights  := data.weights;;
weightGroups := data.weightGroups;;
ha       := hgens[1];; hb := hgens[2];;

freeBasis := [];;
hBasis    := [];;
genName   := [];;
rightPart := ListWithIdenticalEntries(ngens, 0);;

freeBasis[1] := fa;;  hBasis[1] := ha;;  genName[1] := "a";;
freeBasis[2] := fb;;  hBasis[2] := hb;;  genName[2] := "b";;

IdentifyWeight := function(w)
    local wkIdx, matched, ui, vi, fComm, hComm, exps, idx, gj, ok, gk;
    wkIdx   := weightGroups[w];;
    matched := ListWithIdenticalEntries(Length(wkIdx), false);;

    for ui in [1..ngens] do
        if weights[ui] >= w then continue;; fi;;
        for vi in [1..ui-1] do
            if weights[vi] >= w then continue;; fi;;
            if weights[ui] + weights[vi] <> w then continue;; fi;;
            if rightPart[ui] > 0 and rightPart[ui] > vi then continue;; fi;;
            if not IsBound(freeBasis[ui]) or not IsBound(freeBasis[vi]) then
                continue;;
            fi;;

            fComm := Comm(freeBasis[ui], freeBasis[vi]);;
            hComm := Comm(hBasis[ui], hBasis[vi]);;
            exps  := Exponents(hComm);;

            for idx in [1..Length(wkIdx)] do
                gj := wkIdx[idx];;
                if matched[idx] then continue;; fi;;
                if exps[gj] <> 1 then continue;; fi;;
                ok := true;;
                for gk in wkIdx do
                    if gk <> gj and exps[gk] <> 0 then ok := false;; break;; fi;;
                od;;
                if ok then
                    freeBasis[gj] := fComm;;
                    hBasis[gj]    := hComm;;
                    rightPart[gj] := vi;;
                    genName[gj]   := Concatenation("[", genName[ui], ",", genName[vi], "]");;
                    matched[idx]  := true;;
                    break;;
                fi;;
            od;;
        od;;
    od;;

    for idx in [1..Length(wkIdx)] do
        gj := wkIdx[idx];;
        if not matched[idx] then
            Print("  g", gj, " (w=", w, "): NOT IDENTIFIED — checking exps:\n");;
            for ui in [1..ngens] do
                if weights[ui] >= w then continue;; fi;;
                for vi in [1..ui-1] do
                    if weights[vi] >= w then continue;; fi;;
                    if weights[ui] + weights[vi] <> w then continue;; fi;;
                    if rightPart[ui] > 0 and rightPart[ui] > vi then continue;; fi;;
                    if not IsBound(freeBasis[ui]) or not IsBound(freeBasis[vi]) then continue;; fi;;
                    exps := Exponents(Comm(hBasis[ui], hBasis[vi]));;
                    if exps[gj] <> 0 then
                        Print("    [g", ui, ",g", vi, "]: exps at weight-", w, " = ",
                              List(wkIdx, k -> exps[k]), "\n");;
                    fi;;
                od;;
            od;;
            genName[gj] := Concatenation("g", String(gj), "?");;
        fi;;
    od;;
end;;

for w in [2..K] do
    IdentifyWeight(w);;
od;;

Print("\n=== Generator identification ===\n");;
for w in [1..K] do
    Print("Weight ", w, ":\n");;
    for i in weightGroups[w] do
        Print("  g", i, " = ", genName[i], "\n");;
    od;;
od;;

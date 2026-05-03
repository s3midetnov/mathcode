## hall_coords.g
##
## Converts cy (in nq Pcp coordinates) to standard Hall basis coordinates,
## then pretty-prints y in commutator notation.
##
## The Hall basis for F_2 = <a,b>, a < b:
##   Weight 1: a, b
##   Weight 2: [b,a]
##   Weight 3: [[b,a],a], [[b,a],b]
##   Weight 4: [[[b,a],a],a], [[[b,a],a],b], [[[b,a],b],b]
##   Weight 5: [g4,g3],[g5,g3],[g6,a],[g6,b],[g7,b],[g8,b]   (6 elements)
##   ... (continues recursively)
##
## Algorithm:
##   1. Build Hall basis as free group words (using standard Hall conditions).
##   2. Map each free group Hall word to H using phi.
##   3. Get its Exponents in H (= its Pcp coordinate vector) = one row of matrix M.
##   4. cy_Hall = M_w^{-1} * cy_Pcp|_w  (at each weight w independently).

LoadPackage("nq");;

K := 10;;   ## compute Hall coords up to weight K

F := FreeGroup("a","b");;
fa := F.1;; fb := F.2;;

## ---- Setup ----
BuildSetup := function(K)
    local H, hgens, ngens, sizes, weights, wGroups, w, i, prev;
    H     := NilpotentQuotient(F, K+1);;
    hgens := GeneratorsOfGroup(H);;
    ngens := Length(hgens);;
    sizes := [];;
    for w in [1..K+1] do sizes[w] := Length(GeneratorsOfGroup(NilpotentQuotient(F,w)));; od;;
    weights := ListWithIdenticalEntries(ngens, 0);;
    for w in [1..K+1] do
        prev := 0;; if w > 1 then prev := sizes[w-1];; fi;;
        for i in [prev+1..sizes[w]] do weights[i] := w;; od;;
    od;;
    wGroups := [];;
    for w in [1..K+1] do
        wGroups[w] := Filtered([1..ngens], i -> weights[i] = w);;
    od;;
    return rec(H:=H, hgens:=hgens, ngens:=ngens,
               weights:=weights, wGroups:=wGroups);;
end;;

setup := BuildSetup(K);;
H      := setup.H;;
ha     := setup.hgens[1];;   ## image of a
hb     := setup.hgens[2];;   ## image of b
ngens  := setup.ngens;;

## ---- Build Hall basis (as free group words + images in H) ----
## hfree[i] = free group word  (weight = hallWt[i])
## himg[i]  = its image in H
## hname[i] = string name
## hallRight[i] = index of right factor (for Hall condition: if i=[u,v], hallRight[i]=v)

hallFree  := [];;  hallImg  := [];;  hallName  := [];;  hallRight := [];;
hallWt    := [];;  hallIdx  := [];;  ## hallIdx[w] = list of Hall basis indices at weight w

hallFree[1]  := fa;;  hallImg[1]  := ha;;  hallName[1]  := "a";;
hallRight[1] := 0;;   hallWt[1]   := 1;;
hallFree[2]  := fb;;  hallImg[2]  := hb;;  hallName[2]  := "b";;
hallRight[2] := 0;;   hallWt[2]   := 1;;

hallIdx[1] := [1,2];;
nh := 2;;  ## current number of Hall basis elements

BuildHallWeight := function(w)
    ## For each pair (u,v) with hallWt[u]+hallWt[v]=w, u>v (by index), Hall cond,
    ## compute [u,v] in F and H.  These ARE the Hall basis elements at weight w
    ## (by definition).
    local u, v, fw, hw, nm, newElts, e;
    newElts := [];;
    for u in [1..nh] do
        if hallWt[u] >= w then continue;; fi;;
        for v in [1..u-1] do
            if hallWt[v] >= w then continue;; fi;;
            if hallWt[u] + hallWt[v] <> w then continue;; fi;;
            ## Hall condition: hallRight[u] = 0 (generator) or hallRight[u] <= v
            if hallRight[u] > 0 and hallRight[u] > v then continue;; fi;;
            ## Compute [u,v]
            fw := Comm(hallFree[u], hallFree[v]);;
            hw := Comm(hallImg[u],  hallImg[v]);;
            nm := Concatenation("[", hallName[u], ",", hallName[v], "]");;
            Add(newElts, rec(u:=u, v:=v, fw:=fw, hw:=hw, nm:=nm));;
        od;;
    od;;
    ## Sort: first by left factor index (u), then by right factor index (v)
    Sort(newElts, function(a,b)
        if a.u <> b.u then return a.u < b.u;;
        else return a.v < b.v;; fi;;
    end);;
    hallIdx[w] := [];;
    for e in newElts do
        nh := nh + 1;;
        hallFree[nh]  := e.fw;;
        hallImg[nh]   := e.hw;;
        hallName[nh]  := e.nm;;
        hallRight[nh] := e.v;;
        hallWt[nh]    := w;;
        Add(hallIdx[w], nh);;
    od;;
end;;

for w in [2..K] do BuildHallWeight(w);; od;;

Print("Hall basis built: ", nh, " elements up to weight ", K, "\n");;
for w in [1..K] do
    Print("  weight ", w, ": ", Length(hallIdx[w]), " elements\n");;
od;;

## ---- Build change-of-basis matrix M_w for each weight w ----
## M_w is a (d_w x d_w) integer matrix (d_w = # Hall basis elts at weight w)
## Row i = Exponents of hallImg[hallIdx[w][i]] restricted to wGroups[w]
## M_w * (Hall coords) = Pcp coords  (approximately; up to higher-weight terms)

## ---- Solve for y in Hall coordinates ----
## The linear solver (same as solve_exact.g but with output)

EltFromPcpCoords := function(cy)
    local elt, i;
    elt := One(H);;
    for i in [1..ngens] do
        if cy[i] <> 0 then elt := elt * setup.hgens[i]^cy[i];; fi;;
    od;;
    return elt;;
end;;

SolveWeightLevel := function(k, cy)
    local imgX, imgY, wPrev, exps, wkIdx, wk1Idx, nk, nk1, r, M, j, brkj, col, sol, i;
    imgX  := setup.hgens[2];;
    imgY  := EltFromPcpCoords(cy);;
    wPrev := Comm(setup.hgens[1], imgX) * Comm(setup.hgens[2], imgY);;
    exps  := Exponents(wPrev);;
    wkIdx  := setup.wGroups[k];;
    wk1Idx := setup.wGroups[k+1];;
    nk := Length(wkIdx);; nk1 := Length(wk1Idx);;
    if nk = 0 then return ShallowCopy(cy);; fi;;
    r := List(wk1Idx, i -> exps[i]);;
    M := [];;
    for j in [1..nk] do
        brkj := Comm(setup.hgens[2], setup.hgens[wkIdx[j]]);;
        col  := Exponents(brkj);;
        M[j] := List(wk1Idx, i -> col[i]);;
    od;;
    sol := SolutionMat(M, -r);;
    if sol = fail then Print("FAIL at k=", k, "\n");; return fail;; fi;;
    cy := ShallowCopy(cy);;
    for j in [1..nk] do cy[wkIdx[j]] := Int(sol[j]);; od;;
    return cy;;
end;;

## Compute cy (Pcp coords of y)
Print("Solving for y...\n");;
cy := ListWithIdenticalEntries(ngens, 0);;
cy[setup.wGroups[1][1]] := 1;;
cy[setup.wGroups[1][2]] := -1;;
for k in [2..K] do
    cy := SolveWeightLevel(k, cy);;
    if cy = fail then break;; fi;;
od;;

## ---- Convert cy to Hall basis coordinates ----
hallCy := [];;  ## hallCy[i] = coefficient of i-th Hall basis element in y

hallCy[1] := cy[setup.wGroups[1][1]];;  ## coeff of a
hallCy[2] := cy[setup.wGroups[1][2]];;  ## coeff of b

Print("\nConverting to Hall basis...\n");;

for w in [2..K] do
    wPcpIdx  := setup.wGroups[w];;   ## Pcp generator indices at weight w
    wHallIdx := hallIdx[w];;         ## Hall basis indices at weight w
    d        := Length(wHallIdx);;

    ## Build M_w: M_w[i][j] = Exponents(hallImg[wHallIdx[i]])[wPcpIdx[j]]
    ## (how the i-th Hall basis element looks in Pcp coordinates at weight w)
    Mw := [];;
    for i in [1..d] do
        Mw[i] := List(wPcpIdx, p -> Exponents(hallImg[wHallIdx[i]])[p]);;
    od;;

    ## cy_pcp_w = Pcp coords of y at weight w
    cyPcpW := List(wPcpIdx, j -> cy[j]);;

    ## Solve Mw * hallCoords = cyPcpW
    solHall := SolutionMat(Mw, cyPcpW);;
    if solHall = fail then
        Print("  w=", w, ": change-of-basis FAILED\n");;
        for i in [1..d] do hallCy[wHallIdx[i]] := 0;; od;;
    else
        for i in [1..d] do hallCy[wHallIdx[i]] := Int(solHall[i]);; od;;
    fi;;
od;;

## ---- Print y in Hall basis notation ----
Print("\n=== y in standard Hall basis (up to weight ", K, ") ===\n\n");;
Print("y_", K, " = ");;
first := true;;
for w in [1..K] do
    for i in hallIdx[w] do
        c := hallCy[i];;
        if c = 0 then continue;; fi;;
        if first then
            if   c = 1  then Print(hallName[i]);;
            elif c = -1 then Print(hallName[i],"^{-1}");;
            else             Print(hallName[i],"^{",c,"}");;
            fi;;
            first := false;;
        else
            if   c = 1  then Print("\n  · ", hallName[i]);;
            elif c = -1 then Print("\n  · ", hallName[i],"^{-1}");;
            else             Print("\n  · ", hallName[i],"^{",c,"}");;
            fi;;
        fi;;
    od;;
od;;
Print("\n\n");;

Print("=== Breakdown by weight ===\n");;
for w in [1..K] do
    nonz := Filtered(hallIdx[w], i -> hallCy[i] <> 0);;
    if Length(nonz) = 0 then continue;; fi;;
    Print("w=", w, ": ");;
    for i in nonz do
        c := hallCy[i];;
        if c = 1  then Print("+",hallName[i]," ");;
        elif c = -1 then Print("-",hallName[i]," ");;
        else Print(c,"·",hallName[i]," ");;
        fi;;
    od;;
    Print("\n");;
od;;

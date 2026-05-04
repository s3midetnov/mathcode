using GroupElements
import GroupElements.rmul!, GroupElements.letters, GroupElements.minimalconjugate

# F6 = free group on 6 generators: 1=a, 2=b, 3=c, 4=d, 5=e, 6=f
# negatives = inverses: -1=A, -2=B, -3=C, -4=D, -5=E, -6=F

FW6 = FreeWord{6}
FE6 = FreeGroupEndomorphism{6}
FA6 = FreeGroupAutomorphism{6}

# aut1 = id_aut.copy(); aut1.update({"a":"ab","A":"BA"})
# aut1n = id_aut.copy(); aut1n.update({"a":"aB","A":"bA"})
A1 = FA6(FE6([1,2],[2],[3],[4],[5],[6]), FE6([1,-2],[2],[3],[4],[5],[6]))

# aut2 = id_aut.copy(); aut2.update({"b":"ba","B":"AB"})
# aut2n = id_aut.copy(); aut2n.update({"b":"bA","B":"aB"})
A2 = FA6(FE6([1],[2,1],[3],[4],[5],[6]), FE6([1],[2,-1],[3],[4],[5],[6]))

# aut3 = id_aut.copy(); aut3.update({"c":"cd","C":"DC"})
# aut3n = id_aut.copy(); aut3n.update({"c":"cD","C":"dC"})
A3 = FA6(FE6([1],[2],[3,4],[4],[5],[6]), FE6([1],[2],[3,-4],[4],[5],[6]))

# aut4 = id_aut.copy(); aut4.update({"d":"dc","D":"CD"})
# aut4n = id_aut.copy(); aut4n.update({"d":"dC","D":"cD"})
A4 = FA6(FE6([1],[2],[3],[4,3],[5],[6]), FE6([1],[2],[3],[4,-3],[5],[6]))

# aut5.update({
#     "b": "Adb", "B": "BDa",
#     "c": "Adc", "C": "CDa",
#     "e": "dAeaD", "E": "dAEaD",
#     "f": "dAfaD", "F": "dAFaD"
# })
# aut5n.update({
#     "b": "Dab", "B": "BAd",
#     "c": "Dac", "C": "CAd",
#     "e": "aDedA", "E": "aDEdA",
#     "f": "aDfdA", "F": "aDFdA"
# })
A5 = FA6(FE6([1],[-1,4,2],[-1,4,3],[4],[4,-1,5,1,-4],[4,-1,6,1,-4]),
         FE6([1],[-4,1,2],[-4,1,3],[4],[1,-4,5,4,-1],[1,-4,6,4,-1]))

# aut6.update({
#     "a": "DeaEd", "A": "DeAEd",
#     "b": "DebEd", "B": "DeBEd",
#     "c": "Dec", "C": "CEd",
#     "f": "Def", "F": "FEd"
# })
# aut6n.update({
#     "c": "Edc", "C": "CDe",
#     "f": "Edf", "F": "FDe",
#     "a": "EdaDe", "A": "EdADe",
#     "b": "EdbDe", "B": "EdBDe"
# })
A6 = FA6(FE6([-4,5,1,-5,4],[-4, 5, 2, -5, 4],[-4, 5, 3],[4],[5],[-4, 5, 6]),
         FE6([-5,4,1,-4,5],[-5,4,2,-4,5],[-5,4,3],[4],[5],[-5, 4, 6]))



# aut7 = id_aut.copy(); aut7.update({"e":"ef","E":"FE"})
# aut7n = id_aut.copy(); aut7n.update({"e":"eF","E":"fE"})
A7 = FA6(FE6([1],[2],[3],[4],[5,6],[6]), FE6([1],[2],[3],[4],[5,-6],[6]))

# aut8 = id_aut.copy(); aut8.update({"f":"fe","F":"EF"})
# aut8n = id_aut.copy(); aut8n.update({"f":"fE","F":"eF"})
A8 = FA6(FE6([1],[2],[3],[4],[5],[6,5]), FE6([1],[2],[3],[4],[5],[6,-5]))

FW3 = FreeWord{3}
FE3 = FreeGroupEndomorphism{3}

# mapping = {
#     'a': 'x', 'A': 'X',
#     'b': 'y', 'B': 'Y',
#     'c': 'z', 'C': 'Z',
#     'd': 'z', 'D': 'Z',
#     'e': 'y', 'E': 'Y',
#     'f': 'x', 'F': 'X',
# }
Q = FreeGroupEndomorphism{6}([1],[2],[3],[3],[2],[1])  # not sure of exact constructor — see note below

commutator(u, v) = u * v * inv(u) * inv(v)
# gens = [((A1,B1,B2,G1).|>positive)...,((A1,B1,B2,G1).|>inv.|>positive)...,G1^2|>positive,C1,C1i,Y3,Y3i]
# gens6 = [((A1, A2, A3, A4, A5, A6, A7, A8).|>positive)...,((A1, A2, A3, A4, A5, A6, A7, A8).|>inv.|>positive)]
gens6 = [A1,A2,A3,A4,A5,A6,A7,A8,inv(A1),inv(A2),inv(A3),inv(A4),inv(A5),inv(A6),inv(A7),inv(A8)]


# homo32(im1, im2, im3) = FreeGroupEndomorphism{6}(FreeWord{6}(im1), FreeWord{6}(im2), FreeWord{6}(im3), FreeWord{6}([6]), FreeWord{6}([6]), FreeWord{6}([6]))
homo32(im1::FreeWord{6}, im2::FreeWord{6}, im3::FreeWord{6}) = FreeGroupEndomorphism{6}(im1, im2, im3, FreeWord{6}([6]), FreeWord{6}([6]), FreeWord{6}([6]))

gens_2_small = [FreeWord{6}([1]), FreeWord{6}([2])]
# true && begin
#
#     for g in ball(gens6, 3)
#         images = [Q(g(FreeWord{6}([i]))) for i in 1:6]
#         result = commutator(images[1], images[2]) * commutator(images[3], images[4]) * commutator(images[5], images[6])
# #         println(g)
# #         println(images[1], ", ", images[2], ", ",  images[3], ", ",  images[4], ", ",  images[5], ", ",  images[6])
#         println(result)
# #         println("---------------------")
#     end
# end
false && begin
    open("threeRelators.txt", "w") do file
        for g in ball(gens6, 3)
            images = [Q(g(FreeWord{6}([i]))) for i in 1:6]
            #  commutator(images[1], images[2]) * commutator(images[3], images[4]) * commutator(images[5], images[6]) == 1
            println(file, "$(images[1]), $(images[2]), $(images[3]), $(images[4]), $(images[5]), $(images[6])")
            println(homo32([1], [2], [2])(images[1]))
        end
    end
end

true && begin
    open("threeRelators.txt", "w") do file
        for g in ball(gens6, 3)
            for im1 in ball(gens_2_small, 2)
                for im2 in ball(gens_2_small, 2)
                    for im3 in ball(gens_2_small, 2)
                        images = [homo32(im1, im2, im3)(Q(g(FreeWord{6}([i])))) for i in 1:6]
                        #  commutator(images[1], images[2]) * commutator(images[3], images[4]) * commutator(images[5], images[6]) == 1
                        println(file, "$(images[1]), $(images[2]), $(images[3]), $(images[4]), $(images[5]), $(images[6])")
                    end
                end
            end
        end
    end
end
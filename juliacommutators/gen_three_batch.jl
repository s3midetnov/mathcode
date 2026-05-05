using GroupElements, Random

FW6 = FreeWord{6}
FE6 = FreeGroupEndomorphism{6}
FA6 = FreeGroupAutomorphism{6}

A1 = FA6(FE6([1,2],[2],[3],[4],[5],[6]),        FE6([1,-2],[2],[3],[4],[5],[6]))
A2 = FA6(FE6([1],[2,1],[3],[4],[5],[6]),         FE6([1],[2,-1],[3],[4],[5],[6]))
A3 = FA6(FE6([1],[2],[3,4],[4],[5],[6]),         FE6([1],[2],[3,-4],[4],[5],[6]))
A4 = FA6(FE6([1],[2],[3],[4,3],[5],[6]),         FE6([1],[2],[3],[4,-3],[5],[6]))
A5 = FA6(FE6([1],[-1,4,2],[-1,4,3],[4],[4,-1,5,1,-4],[4,-1,6,1,-4]),
         FE6([1],[-4,1,2],[-4,1,3],[4],[1,-4,5,4,-1],[1,-4,6,4,-1]))
A6 = FA6(FE6([-4,5,1,-5,4],[-4,5,2,-5,4],[-4,5,3],[4],[5],[-4,5,6]),
         FE6([-5,4,1,-4,5],[-5,4,2,-4,5],[-5,4,3],[4],[5],[-5,4,6]))
A7 = FA6(FE6([1],[2],[3],[4],[5,6],[6]),         FE6([1],[2],[3],[4],[5,-6],[6]))
A8 = FA6(FE6([1],[2],[3],[4],[5],[6,5]),         FE6([1],[2],[3],[4],[5],[6,-5]))
gens6 = [A1,A2,A3,A4,A5,A6,A7,A8,inv(A1),inv(A2),inv(A3),inv(A4),inv(A5),inv(A6),inv(A7),inv(A8)]

Q  = FreeGroupEndomorphism{6}([1],[2],[3],[3],[2],[1])
Q1 = FreeGroupEndomorphism{6}([1],[1],[2],[3],[3],[2])
Q2 = FreeGroupEndomorphism{6}([1],[1],[2],[3],[3],[2])

outfile = get(ARGS, 1, "three_batch.txt")
N       = parse(Int, get(ARGS, 2, "500"))

cnt = 0
open(outfile, "w") do file
    for _ in 1:N
        n = rand(10:rand(10:30))
        g = foldl(*, rand(gens6, n))
        for q in [Q, Q1, Q2]
            imgs = [q(g(FW6([i]))) for i in 1:6]
            any(w -> length(w) <= 3, imgs) && continue
            println(file, "$(imgs[1]), $(imgs[2]), $(imgs[3]), $(imgs[4]), $(imgs[5]), $(imgs[6])")
            cnt += 1
        end
    end
end
println("Generated $cnt three-relator lines → $outfile")

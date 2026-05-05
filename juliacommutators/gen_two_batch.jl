using GroupElements, Random

FW4 = FreeWord{4}
FE4 = FreeGroupEndomorphism{4}
FA4 = FreeGroupAutomorphism{4}

A1 = FA4(FE4([1,2],[2],[3],[4]),    FE4([1,-2],[2],[3],[4]))
A2 = FA4(FE4([1],[2,1],[3],[4]),    FE4([1],[2,-1],[3],[4]))
A3 = FA4(FE4([1],[2],[3,4],[4]),    FE4([1],[2],[3,-4],[4]))
A4 = FA4(FE4([1],[2],[3],[4,3]),    FE4([1],[2],[3],[4,-3]))
A5 = FA4(FE4([1],[-1,4,2],[-1,4,3],[4]), FE4([1],[-4,1,2],[-4,1,3],[4]))
gens4 = [A1,A2,A3,A4,A5,inv(A1),inv(A2),inv(A3),inv(A4),inv(A5)]

Q = FreeGroupEndomorphism{4}([1],[2],[2],[1])

is_almost_pure(w) = min(count(l -> abs(l)==1, letters(w)),
                        count(l -> abs(l)==2, letters(w))) <= 1

outfile = get(ARGS, 1, "two_batch.txt")
N       = parse(Int, get(ARGS, 2, "50000"))

cnt = 0
open(outfile, "w") do file
    for _ in 1:N
        n = rand(10:rand(15:50))
        g = foldl(*, rand(gens4, n))
        imgs = [Q(g(FW4([i]))) for i in 1:4]
        any(isone, imgs) && continue
        any(w -> length(w) <= 3, imgs) && continue
        any(is_almost_pure, imgs) && continue
        println(file, "$(imgs[1]), $(imgs[2]), $(imgs[3]), $(imgs[4])")
        cnt += 1
    end
end
println("Generated $cnt two-relator lines → $outfile")

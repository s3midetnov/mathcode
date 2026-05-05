using GroupElements

FW6 = FreeWord{6}
FE6 = FreeGroupEndomorphism{6}

homo33(im1::FW6, im2::FW6, im3::FW6) = FE6(im1, im2, im3, FW6([4]), FW6([5]), FW6([6]))

gens_3_small = [FW6([1]), FW6([2]), FW6([3])]

const SUB_TO_DIGIT = Dict('₀'=>0,'₁'=>1,'₂'=>2,'₃'=>3,'₄'=>4,
                          '₅'=>5,'₆'=>6,'₇'=>7,'₈'=>8,'₉'=>9)
function parse_fw6(s::AbstractString)::FW6
    ls = Int8[]; i = firstindex(s)
    while i <= lastindex(s)
        c = s[i]
        if c == '𝑥' || c == '𝑋'
            sign = c == '𝑥' ? Int8(1) : Int8(-1)
            i = nextind(s, i); num = 0
            while i <= lastindex(s) && haskey(SUB_TO_DIGIT, s[i])
                num = num*10 + SUB_TO_DIGIT[s[i]]; i = nextind(s, i)
            end
            push!(ls, sign*Int8(num))
        else; i = nextind(s, i)
        end
    end
    FW6(ls)
end

infile  = get(ARGS, 1, "three_batch.txt")
outfile = get(ARGS, 2, "three_batch_F3.txt")

im_ball = collect(ball(gens_3_small, 2))
cnt = 0
open(outfile, "w") do file
    for raw in eachline(infile)
        parts = split(raw, ", ")
        length(parts) == 6 || continue
        ws = parse_fw6.(parts)
        any(isone, ws) && continue
        for im1 in im_ball, im2 in im_ball, im3 in im_ball
            h = homo33(im1, im2, im3)
            imgs = h.(ws)
            any(isone, imgs) && continue
            any(w -> length(w) <= 3, imgs) && continue
            println(file, "$(imgs[1]), $(imgs[2]), $(imgs[3]), $(imgs[4]), $(imgs[5]), $(imgs[6])")
            cnt += 1
        end
    end
end
println("Generated $cnt lifted three-relator lines → $outfile")

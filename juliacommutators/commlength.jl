"""Find an element w of the free group F₂ which has commutator length at least 3, and is also a solution to s₁t₁S₁T₁s₂t₂S₂t₂ = 1.
   This equation is equivalent to x₁²x₂²x₃²x₄² = 1.
"""

using GroupElements
import GroupElements.rmul!, GroupElements.letters, GroupElements.minimalconjugate

function cl(w::FreeWord{N}, maxlen = typemax(Int), dict = Dict{FreeWord{N},Int}()) where N
    n = length(w)
    n==0 && return 0
    maxlen==0 && return typemax(Int)÷2
    
    haskey(dict,w) && return dict[w]
    
    maxcl = typemax(Int)
    wl = letters(w)
    v = FreeWord{N}([])
    for i=1:n, k=i+1:n
        wl[i]==-wl[k] || continue
        for j=i+1:k-1, l=k+1:n
            wl[j]==-wl[l] || continue
            empty!(v.x)
            for s=1:i-1 rmul!(v,wl[s]) end
            for s=k+1:l-1 rmul!(v,wl[s]) end
            for s=j+1:k-1 rmul!(v,wl[s]) end
            for s=i+1:j-1 rmul!(v,wl[s]) end
            for s=l+1:n rmul!(v,wl[s]) end
            v = minimalconjugate(v)[1]
            newcl = cl(v, maxlen-1, dict) + 1
            if newcl < maxcl
                maxcl = newcl
            end
        end
    end
    dict[w] = maxcl
    maxcl
end

# clbound(w, Val(n)) returns whether w has commutator length ≤ n
function clbound(w::FreeWord{N}, ::Val{0}) where N
    return isone(w)
end

#Mat = SA{Int64}
function rmul!(M::Array, i::Int8)
    @inbounds if i==1
        M[1,2] += 2M[1,1]; M[2,2] += 2M[2,1]
    elseif i==2
        M[1,1] += 2M[1,2]; M[2,1] += 2M[2,2]
    elseif i==-1
        M[1,2] -= 2M[1,1]; M[2,2] -= 2M[2,1]
    else # i==-2
        M[1,1] -= 2M[1,2]; M[2,1] -= 2M[2,2]
    end
    M
end
function lmul!(M::Array, i::Int8)
    @inbounds if i==1
        M[1,1] += 2M[2,1]; M[1,2] += 2M[2,2]
    elseif i==2
        M[2,1] += 2M[1,1]; M[2,2] += 2M[1,2]
    elseif i==-1
        M[1,1] -= 2M[2,1]; M[1,2] -= 2M[2,2]
    else # i==-2
        M[2,1] -= 2M[1,1]; M[2,2] -= 2M[1,2]
    end
    M
end
function setprod!(M::Array, A::Array, B::Array) # in M₂
    M[1,1] = A[1,1]*B[1,1] + A[1,2]*B[2,1]
    M[1,2] = A[1,1]*B[1,2] + A[1,2]*B[2,2]
    M[2,1] = A[2,1]*B[1,1] + A[2,2]*B[2,1]
    M[2,2] = A[2,1]*B[1,2] + A[2,2]*B[2,2]
    M
end
function isinverse(A::Array, B::Array) # in SL₂ℤ
    A[1,1]==B[2,2] && A[2,2]==B[1,1] && A[1,2]==-B[1,2] && A[2,1] == -B[2,1]
end

function sl2conjugate(A::Array, B::Array) # for matrices in SL₂ℤ, conj. in SL₂ℚ
    A[1,1]+A[2,2]==B[1,1]+B[2,2]
end
    
const onemat = Int64[1 0;0 1]

# to compute clbound(w, Val(n)), check whether
# there are a,b with w=w₁aw₂bw₃Aw₄Bw₅ and clbound(w₁w₄w₃w₂w₅, n-1)
# fast method for n=1: compute w₁w₄w₃w₂w₅ using matrices
function clbound(w::FreeWord{N}, ::Val{1}) where N
    n = length(w)
    n==0 && return true

    wl = letters(w)
    m23451 = Int128[1 0;0 1]
    for i=1:n rmul!(m23451,wl[i]) end
    m23 = similar(m23451)
    m451 = similar(m23451)
    m32 = similar(m23451)
    m514 = similar(m23451)
    for i=1:n
        lmul!(m23451,-wl[i])
        copy!(m23,onemat)
        copy!(m451,m23451)
        for k=i+1:n
            lmul!(m451,-wl[k])
            if wl[i]==-wl[k] && sl2conjugate(m451,m23)
                copy!(m32,m23)
                for j=i+1:k-1
                    lmul!(m32,-wl[j])
                    copy!(m514,m451)
                    for l=k+1:n
                        lmul!(m514,-wl[l])
                        if wl[j]==-wl[l] && isinverse(m514,m32)
                            return true
                        end
                        rmul!(m514,wl[l])
                    end
                    rmul!(m32,wl[j])
                end
            end
            rmul!(m23,wl[k])
        end
        rmul!(m23451,wl[i])
    end
    return false
end

function clbound(w::FreeWord{N}, ::Val{T}) where {N,T}
    n = length(w)
    n==0 && return true
    
    wl = letters(w)
    v = FreeWord{N}([])
    for i=1:n, k=i+1:n
        wl[i]==-wl[k] || continue
        for j=i+1:k-1, l=k+1:n
            wl[j]==-wl[l] || continue
            empty!(v.x)
            for s=1:i-1 rmul!(v,wl[s]) end
            for s=k+1:l-1 rmul!(v,wl[s]) end
            for s=j+1:k-1 rmul!(v,wl[s]) end
            for s=i+1:j-1 rmul!(v,wl[s]) end
            for s=l+1:n rmul!(v,wl[s]) end
            v = minimalconjugate(v)[1]
            clbound(v, Val(T-1)) && return true
        end
    end
    return false
end

function clsols(w::FreeWord{N}, g::Int) where N
    n = length(w)
    n==0 && return [()]
    g==0 && return []
    
    wl = letters(w)
    sols = Any[]
    for i=1:n, k=i+1:n
        wl[i]==-wl[k] || continue
        a = FreeWord{N}([wl[k]])
        for j=i+1:k-1, l=k+1:n
            wl[j]==-wl[l] || continue
            b = FreeWord{N}([wl[l]])
            (w₁,w₂,w₃,w₄,w₅) = ntuple(_->FreeWord{N}([]),5)
            for s=1:i-1 rmul!(w₁,wl[s]) end
            for s=i+1:j-1 rmul!(w₂,wl[s]) end
            for s=j+1:k-1 rmul!(w₃,wl[s]) end
            for s=k+1:l-1 rmul!(w₄,wl[s]) end
            for s=l+1:n rmul!(w₅,wl[s]) end
            for p=clsols(w₁*w₄*w₃*w₂*w₅,g-1)
                push!(sols,(((w₄*w₃*a)^inv(w₁),(b*inv(w₃*w₂))^inv(w₁*w₄)),p...))
            end
        end
    end
    sols
end

FW = FreeWord{4}
FE = FreeGroupEndomorphism{4}
FA = FreeGroupAutomorphism{4}

#w = FW([ 1, -2, 1, -2, 1, 1, -2, 1, 2, -1, -1, 2, -1, 2, -1, -1, -1, 2, 1, -2 ])

A1 = FA(FE([1],[2,1],[3],[4]),FE([1],[2,-1],[3],[4]))
B1 = FA(FE([1,2],[2],[3],[4]),FE([1,-2],[2],[3],[4]))
B2 = FA(FE([1],[2],[3,4],[4]),FE([1],[2],[3,-4],[4]))
G1 = FA(FE([2,-4,2,1],[-1,-2],[-1,-4,2,1,-3,2,1,-2],[-1,-4,2,1,-2]),FE([-1,-2,4,-2],[-4,2,1],[-2,-1,-2,4,-3,2,1],[-2,-1,-4,2,1]))

C1 = FE([1,3,-4,-3,2],[1,-2,-1,-4,2,3,-4,-3,2],[-2,3,4],[4])
C1i = FE([1,1,-2,-1,-4],[3,-4,-3,2,3,4,-3],[3,-4,-3,2,3],[4])
Y3 = FE([3,3,1,2],[-2,-1,-3,-3,2,3,3,1,2],[-2,-1,-3,-3,2,3,1],[-2,-1,-4,-3,2,3,1])
Y3i = FE([1,-2,3,-4,3,-4],[4,-3,4,-3,2,3,-4,3,-4],[4,-3,4],[-3,2,3,-4,1,-2,-1])

w0 = FreeWord{4}([4])
# then apply some sequence of A1...G1
# then apply Q1, Q2 or Q3:
Q1 = FreeGroupEndomorphism{4}([1],[-1],[2],Int[])
Q2 = FreeGroupEndomorphism{4}([1],Int[],[2],Int[])
Q3 = FreeGroupEndomorphism{4}([1],[1],[2],Int[])

N4toN4a = FreeGroupEndomorphism{4}([-1,-2,4,-3,2,1],[-1,-2,3],[-3,2,1,-2],[-1,-4,3,-4,2,1])
N4atoN4 = FreeGroupEndomorphism{4}([2,3,3,4],[-3,-2],[3,4,2],[3,4,1,2])

gens = [((A1,B1,B2,G1).|>positive)...,((A1,B1,B2,G1).|>inv.|>positive)...,G1^2|>positive,C1,C1i,Y3,Y3i]

false && begin
    wcandidates = sort(unique(x->x[1],[(minimalconjugate(q(g(w0)))[1],q,g) for g=ball(gens,5) for q=[Q1,Q2,Q3]]),lt=(x,y)->x[1]<y[1])

    results = Channel(Inf)

    @info "Ready to work on $(length(wcandidates)) elements"

    using ThreadPools

    @time @qthreads for w=wcandidates
        bd = clbound(w[1],Val(2))
        @info "$(w[1]): $bd"
        bd || put!(results,w)
    end
    close(results)
    cldata = collect(results)
end

w1 = FreeWord{2}([-1,-2,1,1,2,-1])
w2 = FreeWord{2}([-1,-1,-2,-1,2,1,-2,1,1,2])

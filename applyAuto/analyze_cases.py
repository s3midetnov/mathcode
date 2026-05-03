import sympy as sp
from sympy.matrices.normalforms import smith_normal_form


def abelian_group_type(a, b, c, d):
    M = sp.Matrix([[a, b],
                   [c, d]])

    res = smith_normal_form(M)

    # handle both return styles
    S = res[0] if isinstance(res, tuple) else res

    diag = [S[0, 0], S[1, 1]]
    invariants = [x for x in diag if x != 0]
    rank = len(invariants)

    if rank == 2:
        s1, s2 = invariants
        return  (s1, s2) #f"Z/{s1} ⊕ Z/{s2}"

    if rank == 1:
        return  (0, invariants[0]) #f"Z ⊕ Z/{invariants[0]}"

    return (0, 0) #"Z ⊕ Z"

def make_smaller(aa : str, cc : str):
    # print(aa, cc)
    cc = cc.replace(aa, '')
    # print(aa, cc)
    return aa, cc

def abelianize(word : str):
    e_x = word.count('x') - word.count('X')
    e_y = word.count('y') - word.count('Y')
    return e_x, e_y

def full_abelianization(aa : str, cc : str):
    a_x, a_y = abelianize(aa)
    c_x, c_y = abelianize(cc)

    return abs(a_x) + abs(a_y) + abs(c_x) + abs(c_y) == 0


def compute_ab_rank(aa : str, cc : str):
    a_x, a_y = abelianize(aa)
    c_x, c_y = abelianize(cc)
    return abelian_group_type(a_x, a_y, c_x, c_y)


from freegrouplib import reduce_word, inverse_word

def find_best_chunk(b, a):
    best_saving = 0
    best = None

    for candidate in [a, inverse_word(a)]:
        n = len(candidate)
        for i in range(len(b)):
            e_len = 0
            while e_len < n and i + e_len < len(b) and b[i + e_len] == candidate[e_len]:
                e_len += 1

            if e_len == 0:
                continue

            w_inv = inverse_word(candidate[e_len:])
            saving = e_len - len(w_inv)

            if saving > best_saving:
                best_saving = saving
                best = (i, e_len, w_inv, saving)

    return best  # None if no improving match found


def reduce_by(a, c, b):
    while True:
        match_a = find_best_chunk(b, a)
        match_c = find_best_chunk(b, c)

        if match_a is None and match_c is None:
            break

        if match_a is None:
            best = match_c
        elif match_c is None:
            best = match_a
        else:
            best = match_a if match_a[3] >= match_c[3] else match_c  # compare savings

        i, e_len, w_inv, saving = best
        b = reduce_word(b[:i] + w_inv + b[i + e_len:])

    return b

def analyze_cases():
    interesting_count = 0
    with open("testCases/test_cases.txt", "r") as f:
        for ind, line in enumerate(f):
            aa, bb, cc, dd = [s.strip() for s in line.strip().split(",")]
            if len(aa) <= 2 or len(cc) <= 2 or len(bb) <= 2:
                continue


            # b_ = reduce_by(aa, cc, bb)
            # if len(b_) <= 2:
            #     continue

            interesting_count += 1
            with open("testCases/reducedb.txt", "a") as f:
                f.write(f"{aa}, {cc}, {b_}\n")
                print(f"{aa}, {cc}, {b_}")
            if interesting_count > 50:
                break
    return 0





if __name__ == "__main__":
    print(analyze_cases())
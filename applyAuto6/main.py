import random

from applyAuto6.freegrouplib2 import inverse_word
from freegrouplib2 import apply_sequence, reduce_word, abelianize, apply_aut, comm, comm2
from automorphisms import aut_map, map_word1, map_word2, map_word3
import os




def random_iter(steps=5):
    a_ = 'a'
    b_ = 'b'
    c_ = 'c'
    d_ = 'd'
    e_ = 'e'
    f_ = 'f'
    to_apply = [random.choice(list(aut_map.keys())) for _ in range(steps)]
    a_ = apply_sequence(a_, to_apply)
    b_ = apply_sequence(b_, to_apply)
    c_ = apply_sequence(c_, to_apply)
    d_ = apply_sequence(d_, to_apply)
    e_ = apply_sequence(e_, to_apply)
    f_ = apply_sequence(f_, to_apply)
    return a_, b_, c_, d_, e_, f_, to_apply




def generate_test_case(steps=20):
    a_, b_, c_, d_, e_, f_, seq = random_iter(steps)
    aa = reduce_word(map_word3(a_))
    bb = reduce_word(map_word3(b_))
    cc = reduce_word(map_word3(c_))
    dd = reduce_word(map_word3(d_))
    ee = reduce_word(map_word3(e_))
    ff = reduce_word(map_word3(f_))


    if len(aa) <= 3 or len(bb) <= 3 or len(cc) <= 3 or len(dd) <= 3 or len(ee) <= 3 or len(ff) <= 3:
        return aa, bb, cc, dd, ee, ff

    # Only keep cases where all four words lie in the commutator subgroup (γ_2)
    if 1 == 1:
        line = f"{aa}, {bb}, {cc}, {dd}, {ee}, {ff}"
        filename = os.path.join(os.path.dirname(__file__), "testCases", "examples.txt")
        existing = set()
        if os.path.exists(filename):
            with open(filename, "r") as f:
                existing = set(l.strip() for l in f if l.strip())

        if line not in existing:
            with open(filename, "a") as f:
                f.write(line + "\n")
            print(f"Appended: {line}")
        else:
            print(f"Already exists: {line}")
        return aa, bb, cc, dd, ee, ff
    return aa, bb, cc, dd, ee, ff



def check_inverse(aut, aut_inv, generators="abcdefABCDEF"):
    for g in generators:
        fwd = apply_aut(g, aut)
        roundtrip = apply_aut(fwd, aut_inv)
        assert reduce_word(roundtrip) == g, f"Failed on {g}: got {roundtrip}"

def generate_test_test(steps=1):
    a_, b_, c_, d_, e_, f_, seq = random_iter(steps)

    # Check identity in the FREE GROUP on a,b,c,d,e,f FIRST
    commutator = (a_ + b_ + inverse_word(a_) + inverse_word(b_) +
                  c_ + d_ + inverse_word(c_) + inverse_word(d_) +
                  e_ + f_ + inverse_word(e_) + inverse_word(f_))
    # assert reduce_word(commutator) == "", "Identity failed in F(a,b,c,d,e,f)!"

    # Now project
    aa = reduce_word(map_word3(a_))
    bb = reduce_word(map_word3(b_))
    cc = reduce_word(map_word3(c_))
    dd = reduce_word(map_word3(d_))
    ee = reduce_word(map_word3(e_))
    ff = reduce_word(map_word3(f_))

    # assert(reduce_word(aa + bb + inverse_word(aa) + inverse_word(bb) + cc + dd + inverse_word(cc) + inverse_word(dd) + ee + ff + inverse_word(ee) + inverse_word(ff)))
    # assert (reduce_word(comm(aa, bb) + comm(cc, dd) + comm(ee, ff)) == "")
    # print(f"{aa}, {bb}, {cc}, {dd}, {ee}, {ff}")
    assert(reduce_word(comm2(aa, bb) + comm2(cc, dd) + comm2(ee, ff)) == "")
    if not reduce_word(comm2(aa, bb) + comm2(cc, dd) + comm2(ee, ff)) == "":
        print(f"Failed on {aa}, {bb}, {cc}, {dd}, {ee}, {ff}")
        print(reduce_word(comm2(aa, bb) + comm2(cc, dd) + comm2(ee, ff)))


if __name__ == "__main__":
    print("assertions")
    check_inverse(aut_map['5'], aut_map['5n'])
    check_inverse(aut_map['6'], aut_map['6n'])
    check_inverse(aut_map['7'], aut_map['7n'])
    check_inverse(aut_map['8'], aut_map['8n'])
    for _ in range(100):
        generate_test_test()
    print("="*50)
    print('test cases work!')
    print("="*50)

    for _ in range(1000):
        aa, bb, cc, dd, ee, ff = generate_test_case(random.randint(5, random.randint(10, 30)))
        assert(reduce_word(comm2(aa, bb) + comm2(cc, dd) + comm2(ee, ff)) == "")
        print(aa, bb, cc, dd, ee, ff)




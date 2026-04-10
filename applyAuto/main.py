import random
import os
from pi1S2auto import *
from freegrouplib import *


auts = [aut1, aut2, aut3, aut4, aut5, aut1n, aut2n, aut3n, aut4n, aut5n]
aut_map = {
    "1": aut1, "2": aut2, "3": aut3, "4": aut4, "5": aut5,
    "1n": aut1n, "2n": aut2n, "3n": aut3n, "4n": aut4n, "5n": aut5n
}

def apply_sequence(word, sequence):
    for aut_key in sequence:
        aut = aut_map[aut_key]
        word = apply_aut(word, aut)
    return word

# Example: apply random sequence
def random_iter(steps=5):
    a_ = 'a'
    b_ = 'b'
    c_ = 'c'
    d_ = 'd'
    to_apply = [random.choice(list(aut_map.keys())) for _ in range(steps)]
    a_ = apply_sequence(a_, to_apply)
    b_ = apply_sequence(b_, to_apply)
    c_ = apply_sequence(c_, to_apply)
    d_ = apply_sequence(d_, to_apply)
    return a_, b_, c_, d_, to_apply

def delete_subwords(a, c, target, steps = 20):
    it = steps
    changed = True
    while changed and it:
        it -=1
        changed = False
        for sub in [a, c, inverse_word(a), inverse_word(c)]:
            if sub in target:
                target = target.replace(sub, "")
                changed = True
    return target

def abelianize(word : str):
    e_x = word.count('x') - word.count('X')
    e_y = word.count('y') - word.count('Y')
    return e_x, e_y

def trivial_abeliznization (aa : str, cc : str) -> bool:
    ea_x, ea_y = abelianize(aa)
    ec_x, ec_y = abelianize(cc)
    return (ea_x * ec_y - ec_x * ea_y == 1) or (ea_x * ec_y - ec_x * ea_y == -1)

def generate_test_case(steps=None):
    if steps is None:
        steps = random.randint(10, random.randint(20, 70))
    a_, b_, c_, d_, seq = random_iter(steps)
    aa = reduce_word(map_word1(a_))
    bb = reduce_word(map_word1(b_))
    cc = reduce_word(map_word1(c_))
    dd = reduce_word(map_word1(d_))
    if not trivial_abeliznization(aa, cc):
        return

    if len(aa) == 1 or len(cc) == 1 or len(aa) == 2 or len(cc) == 2:
        return

    line = f"{aa}, {bb}, {cc}, {dd}"
    filename = os.path.join(os.path.dirname(__file__), "testCases", "test_cases.txt")

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

    seq_line = ",".join(seq)
    seq_filename = os.path.join(os.path.dirname(__file__), "testCases", "test_sequences.txt")
    with open(seq_filename, "a") as f:
        f.write(f"{line} | {seq_line}\n")

    return aa, bb, cc, dd

def generate_test_case2(steps=None):
    if steps is None:
        steps = random.randint(5, random.randint(20, 70))
    a_, b_, c_, d_, seq = random_iter(steps)
    aa = reduce_word(map_word2(a_))
    bb = reduce_word(map_word2(b_))
    cc = reduce_word(map_word2(c_))
    dd = reduce_word(map_word2(d_))
    if not trivial_abeliznization(aa, cc):
        return

    if len(aa) == 1 or len(cc) == 1 or len(aa) == 2 or len(cc) == 2:
        return

    line = f"{aa}, {bb}, {cc}, {dd}"
    filename = os.path.join(os.path.dirname(__file__), "testCases", "test_cases.txt")

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

    seq_line = ",".join(seq)
    seq_filename = os.path.join(os.path.dirname(__file__), "testCases", "test_sequences.txt")
    with open(seq_filename, "a") as f:
        f.write(f"{line} | {seq_line}\n")

    return aa, bb, cc, dd
generate_test_case()

sampling = True
if sampling:

    bucket_success = 0 # if it is /= 0
    bucket_fail = 0
    strict_bucket_fail = 0
    no_3_bucket_fail = 0

    for size in range(5, 30, 20):
    #     print("Size:", size)
        for _ in range(20):
            x = random_iter(size)
            aa = reduce_word(map_word1(x[0]))
            # print('a : ', aa)
            bb = reduce_word(map_word1(x[1]))
            # print('b : ', bb)
            cc = reduce_word(map_word1(x[2]))
            # print('c : ', cc)
            dd = reduce_word(map_word1(x[3]))

            bb_ = delete_subwords(aa, cc, bb)
            dd_ = delete_subwords(aa, cc, dd)
            if bb_ or dd_:
                bucket_success += 1
                print(' a= ', aa, '\n b= ', bb_, '\n c= ', cc, '\n d= ', dd_, x[4])
                print("-----------------------")
            elif not ('3' in x[4] or '3n' in x[4]):
                no_3_bucket_fail += 1
            elif len(aa) + len(cc) > 2:
                strict_bucket_fail += 1
                print(x[4])
                print(' a= ', aa, '\n b= ', bb_, '\n c= ', cc, '\n d= ', dd_)
            else:
                bucket_fail += 1

    print(f"nontrivial element in {bucket_success} cases, \n trivial because no mixing in {no_3_bucket_fail} cases, \n trivial because basis in {bucket_fail} cases,\n  strict trivial in {strict_bucket_fail} cases")


def write_as_product(a : str) -> str:
    parts = []
    for c in a:
        if c.isupper():
            parts.append(c.lower() + "^-1")
        else:
            parts.append(c)
    return " * ".join(parts)


if __name__ == "__main__":
    # print(write_as_product("xYXYXYxYXyxyXY"))
    # print(write_as_product("xYXYYXYxyyy"))
    for _ in range(50_000):
        generate_test_case()
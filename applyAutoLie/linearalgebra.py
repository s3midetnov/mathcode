import copy
import random

import numpy as np

A1 = np.array([
    [1, 0, 0, 0],  # a coefficient
    [1, 1, 0, 0],  # b coefficient
    [0, 0, 1, 0],  # c
    [0, 0, 0, 1],  # d
])

A2 = np.array([
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
])

A3 = np.array([
    [1, -1, -1, 0],
    [0,  1,  0, 0],
    [0,  0,  1, 0],
    [0,  1,  1, 1],
])

A4 = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
])

A5 = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
])

A1_inv = np.linalg.inv(A1).astype(int)
A2_inv = np.linalg.inv(A2).astype(int)
A3_inv = np.linalg.inv(A3).astype(int)
A4_inv = np.linalg.inv(A4).astype(int)
A5_inv = np.linalg.inv(A5).astype(int)

aut_map = {
    "1": A1, "2": A2, "3": A3, "4": A4, "5": A5,
    "1n": A1_inv, "2n": A2_inv, "3n": A3_inv, "4n": A4_inv, "5n": A5_inv
}

def apply_sequence(vec, sequence):
    for key in sequence:
        vec = aut_map[key] @ vec
    return vec


def format_vector(vec) -> str:
    labels = ["a", "b", "c", "d"]
    terms = []

    for coeff, label in zip(vec, labels):
        if coeff == 0:
            continue
        if coeff == 1:
            terms.append(f"{label}")
        elif coeff == -1:
            terms.append(f"-{label}")
        else:
            terms.append(f"{coeff}{label}")

    if not terms:
        return "0"

    # clean up signs
    result = terms[0]
    for term in terms[1:]:
        if term.startswith("-"):
            result += " - " + term[1:]
        else:
            result += " + " + term

    return result

def format_xy(vec) -> str:
    x, y = vec
    terms = []

    if x != 0:
        if x == 1:
            terms.append("x")
        elif x == -1:
            terms.append("-x")
        else:
            terms.append(f"{x}x")

    if y != 0:
        if y == 1:
            terms.append("y")
        elif y == -1:
            terms.append("-y")
        else:
            terms.append(f"{y}y")

    if not terms:
        return "0"

    result = terms[0]
    for term in terms[1:]:
        if term.startswith("-"):
            result += " - " + term[1:]
        else:
            result += " + " + term

    return result

# projection matrix
P = np.array([
    [1, 0, 0, 1],  # x = a + d
    [0, 1, 1, 0],  # y = b + c
])

def project(vec):
    return P @ vec


a = np.array([1, 0, 0, 0])
b = np.array([0, 1, 0, 0])
c = np.array([0, 0, 1, 0])
d = np.array([0, 0, 0, 1])


def random_iter(steps=5):
    a_ = copy.copy(a)
    b_ = copy.copy(b)
    c_ = copy.copy(c)
    d_ = copy.copy(d)
    to_apply = [random.choice(list(aut_map.keys())) for _ in range(steps)]
    a_ = apply_sequence(a_, to_apply)
    b_ = apply_sequence(b_, to_apply)
    c_ = apply_sequence(c_, to_apply)
    d_ = apply_sequence(d_, to_apply)

    return a_, b_, c_, d_, to_apply

if __name__ == '__main__':
    for _ in range(50):
        a__, b__, c__, d__, ap = random_iter(random.randint(10, 50))
        a_ = project(a__)
        b_ = project(b__)
        c_ = project(c__)
        d_ = project(d__)
        print(format_xy(a_))
        print(format_xy(b_))
        print(format_xy(c_))
        print(format_xy(d_))
        print("-"*50)

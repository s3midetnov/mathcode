from automorphisms import aut_map

# Free group reduction (canceling xx^{-1} and x^{-1}x)
def reduce_word(word):
    stack = []
    inverse = {"a":"A","b":"B","c":"C","d":"D","x":"X","y":"Y",
               "X":"x","Y":"y",
               "A":"a","B":"b","C":"c","D":"d", 'z' : 'Z', 'Z' : 'z', 'X' : 'x', 'Y' : 'y',
                'e' : 'E','f' : 'F','F' : 'f', 'E' : 'e'}
    for x in word:
        if stack and inverse[x] == stack[-1]:
            stack.pop()
        else:
            stack.append(x)
    return "".join(stack)


def inverse_word(word):
    inverse = {"a": "A", "b": "B", "c": "C", "d": "D",
               "A": "a", "B": "b", "C": "c", "D": "d", 'x' : 'X', 'y' : 'Y', 'X' : 'x', 'Y' : 'y',
               'e' : 'E','f' : 'F','F' : 'f', 'E' : 'e', 'z' : 'Z', 'Z' : 'z'}
    # Reverse the word and replace each letter by its inverse
    return "".join(inverse[ch] for ch in reversed(word))

# Apply a substitution (automorphism) to a word
def apply_aut(word, aut):
    return reduce_word("".join(aut[ch] for ch in word))



# Compute inverses of automorphisms
# Naively: try to find substitution map by brute force search on generators
def inverse_aut(aut):
    inv = {}
    for g in "abcdABCD":
        image = aut[g]
        inv[reduce_word(image)] = g
    # Rebuild inverse map by substitution
    # (Works because each generator is mapped to reduced word of length>=1)
    aut_inv = {}
    for g in "abcdABCD":
        for k,v in inv.items():
            if g == v:
                aut_inv[g] = k
    return aut_inv


def comm(a, b):
    return inverse_word(a) + inverse_word(b) + a + b

def comm2(a, b):
    return a + b + inverse_word(a) + inverse_word(b)

def cyclic_reduce(word: str) -> str:
    """
    Cyclically reduce a word in free group generators x, y, X, Y,
    where X = x⁻¹ and Y = y⁻¹.
    Repeatedly removes cancelling pairs from the ends until stable.
    """
    inverses = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y'}

    word = list(word)

    changed = True
    while changed:
        changed = False
        while len(word) >= 2 and inverses[word[0]] == word[-1]:
            word = word[1:-1]
            changed = True

    return ''.join(word)


def is_one_among_rest(word: str) -> bool:
    """
    Returns True if the word contains exactly one letter from one generator
    (x or X) and all others from the other generator (y or Y), or vice versa.
    """
    if not word:
        return False

    x_count = sum(1 for c in word if c in ('x', 'X'))
    y_count = sum(1 for c in word if c in ('y', 'Y'))

    return x_count == 1 or y_count == 1


# Apply a substitution (automorphism) to a word
def apply_aut(word, aut):
    return reduce_word("".join(aut[ch] for ch in word))


def apply_sequence(word, sequence):
    for aut_key in sequence:
        aut = aut_map[aut_key]
        word = apply_aut(word, aut)
    return word


def abelianize(word : str):
    e_x = word.count('x') - word.count('X')
    e_y = word.count('y') - word.count('Y')
    return e_x, e_y


if __name__ == "__main__":
    print("checking that all works with example xyXXyxYY, yyXYX, yXyXYxxxYX, xyXXXyxY")

    a = "xyXXyxYY"
    b = "yyXYX"
    c = "yXyXYxxxYX"
    d = "xyXXXyxY"

    print(f" abABcdCD = {a + b + inverse_word(a) + inverse_word(b) + c + d + inverse_word(c) + inverse_word(d)}")
    print(f" reduced [a, b][c,d] = {reduce_word(a + b + inverse_word(a) + inverse_word(b) + c + d + inverse_word(c) + inverse_word(d))}")
    # print(reduce_word(a + b + inverse_word(a) + inverse_word(b) + c + d + inverse_word(c) + inverse_word(d)))
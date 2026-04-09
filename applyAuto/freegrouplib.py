
# Free group reduction (canceling xx^{-1} and x^{-1}x)

def reduce_word(word):
    stack = []
    inverse = {"a":"A","b":"B","c":"C","d":"D","x":"X","y":"Y",
               "X":"x","Y":"y",
               "A":"a","B":"b","C":"c","D":"d", 'x' : 'X', 'y' : 'Y', 'X' : 'x', 'Y' : 'y'}
    for x in word:
        if stack and inverse[x] == stack[-1]:
            stack.pop()
        else:
            stack.append(x)
    return "".join(stack)


def inverse_word(word):
    inverse = {"a": "A", "b": "B", "c": "C", "d": "D",
               "A": "a", "B": "b", "C": "c", "D": "d", 'x' : 'X', 'y' : 'Y', 'X' : 'x', 'Y' : 'y'}
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

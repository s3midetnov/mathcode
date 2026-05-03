# Automorphisms definitions:
# Each automorphism is a dict: generator -> word

id_aut = {g:g for g in "abcdefABCDEF"}

aut1 = id_aut.copy(); aut1.update({"a":"ab","A":"BA"})

aut1n = id_aut.copy(); aut1n.update({"a":"aB","A":"bA"})

aut2 = id_aut.copy(); aut2.update({"b":"ba","B":"AB"})

aut2n = id_aut.copy(); aut2n.update({"b":"bA","B":"aB"})

aut3 = id_aut.copy(); aut3.update({"c":"cd","C":"DC"})

aut3n = id_aut.copy(); aut3n.update({"c":"cD","C":"dC"})

aut4 = id_aut.copy(); aut4.update({"d":"dc","D":"CD"})

aut4n = id_aut.copy(); aut4n.update({"d":"dC","D":"cD"})

# fifth: b -> (Ad)b, c -> (Ad)c
# aut5 = id_aut.copy()
# aut5.update({"b":"Adb", "B":"BDa",
#               "c":"Adc", "C":"CDa"})
#
# aut5n = id_aut.copy()
# aut5n.update({"b":"Dab", "B":"BAd",
#               "c":"Dac", "C":"CAd"})
#
# aut6 = id_aut.copy(); aut6.update({"c":"Dec","f":"Def",
#                                    "C": "CEd", "F" : "FEd"})
#
#
# aut6n = id_aut.copy(); aut6n.update({"c":"Edc","f":"Edf",
#                                    "C": "CDe", "F" : "FDe"})
#
#
# aut5: b, c mapped. e, f conjugated by (dA)
aut5 = id_aut.copy()
aut5.update({
    "b": "Adb", "B": "BDa",
    "c": "Adc", "C": "CDa",
    "e": "dAeaD", "E": "dAEaD",
    "f": "dAfaD", "F": "dAFaD"
})

# aut5n: inverse of aut5. Conjugates e, f by (aD)
aut5n = id_aut.copy()
aut5n.update({
    "b": "Dab", "B": "BAd",
    "c": "Dac", "C": "CAd",
    "e": "aDedA", "E": "aDEdA",  # Fixed suffix: dA instead of Ad
    "f": "aDfdA", "F": "aDFdA"   # Fixed suffix: dA instead of Ad
})

# aut6: c, f mapped. a, b conjugated by (De)
aut6 = id_aut.copy()
aut6.update({
    "c": "Dec", "C": "CEd",
    "f": "Def", "F": "FEd",
    "a": "DeaEd", "A": "DeAEd",
    "b": "DebEd", "B": "DeBEd"
})

# aut6n: inverse of aut6. Conjugates a, b by (Ed)
aut6n = id_aut.copy()
aut6n.update({
    "c": "Edc", "C": "CDe",
    "f": "Edf", "F": "FDe",
    "a": "EdaDe", "A": "EdADe",
    "b": "EdbDe", "B": "EdBDe"
})

aut7 = id_aut.copy(); aut7.update({"e":"ef","E":"FE"})
aut8 = id_aut.copy(); aut8.update({"f":"fe","F":"EF"})

aut7n = id_aut.copy(); aut7n.update({"e":"eF","E":"fE"})
aut8n = id_aut.copy(); aut8n.update({"f":"fE","F":"eF"})



# THE PROJECTIONS:
def map_word1(word):
    mapping = { #MAYBE MISTAKE IN INVERSES?
        'a': 'x', 'A': 'X',
        'b': 'x', 'B': 'X',
        'c': 'y', 'C': 'Y',
        'd': 'z', 'D': 'Z',
        'e': 'z', 'E': 'Z',
        'f': 'y', 'F': 'Y',
    }
    return ''.join(mapping[ch] for ch in word)

def map_word2(word):
    mapping = { #MISTAKE IN INVERSES
        'a': 'x', 'A': 'X',
        'b': 'y', 'B': 'y',
        'c': 'y', 'C': 'x',
        'd': 'x', 'D': 'x',
        'e': 'z', 'E': 'Z',
        'f': 'z', 'F': 'Z',
    }
    return ''.join(mapping[ch] for ch in word)

def map_word3(word):
    mapping = {
        'a': 'x', 'A': 'X',
        'b': 'y', 'B': 'Y',
        'c': 'z', 'C': 'Z',
        'd': 'z', 'D': 'Z',
        'e': 'y', 'E': 'Y',
        'f': 'x', 'F': 'X',
    }
    return ''.join(mapping[ch] for ch in word)


auts = [aut1, aut2, aut3, aut4, aut5, aut1n, aut2n, aut3n, aut4n, aut5n, aut6, aut7, aut6n, aut7n, aut8, aut8n]
aut_map = {
    "1": aut1, "2": aut2, "3": aut3, "4": aut4, "5": aut5,
    "1n": aut1n, "2n": aut2n, "3n": aut3n, "4n": aut4n, "5n": aut5n,
    "6": aut6, "7": aut7, "8": aut8,
    "6n" : aut6n, "7n": aut7n, "8n": aut8n
}

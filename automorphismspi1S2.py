
# Automorphisms definitions:
# Each automorphism is a dict: generator -> word

id_aut = {g:g for g in "abcdABCD"}

aut1 = id_aut.copy(); aut1.update({"a":"ab","A":"BA"})

aut1n = id_aut.copy(); aut1n.update({"a":"aB","A":"bA"})

aut2 = id_aut.copy(); aut2.update({"b":"ba","B":"AB"})

aut2n = id_aut.copy(); aut2n.update({"b":"bA","B":"aB"})

aut3 = id_aut.copy(); aut3.update({"c":"cd","C":"DC"})

aut3n = id_aut.copy(); aut3n.update({"c":"cD","C":"dC"})

aut4 = id_aut.copy(); aut4.update({"d":"dc","D":"CD"})

aut4n = id_aut.copy(); aut4n.update({"d":"dC","D":"cD"})

# fifth: b -> (Ad)b, c -> (Ad)c
aut5 = id_aut.copy()
aut5.update({"b":"Adb", "B":"BDa",
              "c":"Adc", "C":"CDa"})

aut5n = id_aut.copy()
aut5n.update({"b":"Dab", "B":"BAd",
              "c":"Dac", "C":"CAd"})



# THE PROJECTIONS:

def map_word1(word):
    mapping = {
        'a': 'x', 'A': 'X',
        'b': 'y', 'B': 'Y',
        'c': 'y', 'C': 'Y',
        'd': 'x', 'D': 'X'
    }
    return ''.join(mapping[ch] for ch in word)

def map_word2(word):
    mapping = {
        'a': 'x', 'A': 'X',
        'b': 'X', 'B': 'x',
        'c': 'y', 'C': 'Y',
        'd': 'Y', 'D': 'y'
    }
    return ''.join(mapping[ch] for ch in word)
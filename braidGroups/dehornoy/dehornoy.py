from braid import Braid

def get_first_handle(braid):
    """
    Finds and returns the first handle of the given braid.

    return:
        (p, q) : Where p, q are the start and end points of the handle.
    """
    def is_handle(braid, p, q):
        """
        Checks if (p, q) is a valid handle in the given braid.

        return:
            True/False
        """
        if braid.generators[p] + braid.generators[q] == 0:
            v = braid.generators[(p+1):q]
            j = abs(braid.generators[p])
            for k in v:
                if not (abs(k) < (j - 1) or abs(k) > j):
                    return False
            else:
                return True
            # if (j-1) in v or -1*(j-1) in v:
            #     return False
            # elif (j in v) or (-1*j in v):
            #     return False
            # else:
            #     return True
        else:
            return False
    p, q = 0, 0
    for q in range(len(braid.generators)):
        for k in range(q, (p-1), -1):
            if is_handle(braid, k, q):
                return (k, q)
    else:
        return None

def reduce(braid, p, q):
    """
    Applies one step of the alphabetical homomorphism on the given handle.

    Returns a new reduced braid.
    """
    new_handle = []
    j = abs(braid.generators[p])
    e = j/braid.generators[p]
    for letter in braid.generators[p:q+1]:
        exp = abs(letter)/letter
        idx = abs(letter)
        if (idx != j) and (idx != (j + 1)):
            new_handle.append(exp*idx)
        elif idx == (j + 1):
            new_handle.append(-1*e*idx)
            new_handle.append(exp*j)
            new_handle.append(e*idx)
    new_generators = braid.generators[:p] + new_handle + \
                        braid.generators[q + 1:]
    return Braid(new_generators, braid.pref_notation)

def fully_reduce(braid, print_output=True):
    """
    Fully reduces the given braid.
    """
    chain = []
    reduced_brd = braid
    while True:
        handle = get_first_handle(reduced_brd)
        chain.append((reduced_brd, handle))
        if handle == None:
            if print_output:
                print (str(reduced_brd))
            break
        p, q = handle
        if print_output:
            if reduced_brd.pref_notation == 'alpha':
                print (str(reduced_brd)[:p] + '[' + \
                      str(reduced_brd)[p:q+1] + ']' \
                    + str(reduced_brd)[q+1:])
            else:
                print (str(reduced_brd))
        reduced_brd = reduce(reduced_brd, handle[0], handle[1])
    print('\n\n\nTHE REDUCED BRAID IS \n', reduced_brd, '\n')
    return (reduced_brd, chain)

def compare(b1, b2, print_output=True):
    """
    Compares two braids b1 and b2. Returns true if equal.
    """
    if print_output:
        print ('b1: ', str(b1))
        print ('b2: ', str(b2))
        print ('b1*inv(b2): ', str(b1*b2.inverse()))
        print ('Reducing b1 * inv(b2)...')
        print 
    reduced, chain = fully_reduce(b1*b2.inverse(), print_output)
    if reduced.generators == []:
        if print_output:
            print ('b1 == b2 :)')
            return True
    else:
        if print_output:
            print ('b1 != b2')
        return False

# a = Braid([2, 2, -1, -2, 3,  2, -1, -2, -3, 2, 3, 2, 2, -1, -2, -3], 'artin')
# b = Braid([-1, -2, 1, 3, -2, -3, -2, 1, -3, 2, 1, 1], 'artin')
# a = Braid([1, 1, -1], 'artin')
# b = Braid([1], 'artin')
# b3 = Braid([-2, -1, -1, -2, -2, -2], 'artin')
# b2 = Braid([-1, -1], 'artin')


def mul(x, y : Braid) -> Braid :
    return Braid(x.generators + y.generators, 'artin')

def idBraid() -> Braid:
    return Braid([], 'artin')

def mulAr(xs) -> Braid :
    if len(xs) == 0:
        return idBraid()
    return mul(xs[0], mulAr(xs[1:]))

def commutator(a, b : Braid) -> Braid :
    return mulAr([a, b, a.inverse(), b.inverse()])

# spherical:
A_02 = Braid([2,3,3,2,1,1], 'artin')
A_03 = Braid([3,3,2,1,1,2], 'artin')
basecom = commutator(A_02, A_03)

# CohenWu
B_01 = Braid([1,2,3,3,2,1], 'artin')
B_02 = Braid([2,3,3,2,-1,-1], 'artin')
B_03 = Braid([3,3,-2,-1,-1,-2], 'artin')

B_01_ = B_01.inverse()
B_02_ = B_02.inverse()
B_03_ = B_03.inverse()


# compare(commutator(A_02, A_03), commutator(B_02, B_03))
# compare(commutator(A_02, A_03), commutator(B_03, B_02))
l = [B_01, B_02, B_03, B_01_, B_02_, B_03_]

def fun ():
    for b1 in l:
        for b2 in l:
            for b3 in l:
                for b4 in l:
                    for b5 in l:
                        for b6 in l:
                            if compare(basecom, mul(mul(commutator(b1, b2), commutator(b3, b4)), commutator(b5, b6)), False):
                                print("URA POBEDA")
                                return
    print("huy")
fun()




# def look_for_solutions1():
#     l = []
#     for x1 in array_iter2:
#         for x2 in array_iter2:
#             for x3 in array_iter2:
#                 for x4 in array_iter2:
#                     s = mulAr([x1, x2, x3, x4])
#                     # if compare(bc, s, False):
#                     #     return s.generators
#                     l.append(s.generators)
#     return l
#
# # l = look_for_solutions1()
# # print(look_for_solutions1())
#
# def look_for_solutions2() :
#     for x1 in l:
#         for x2 in l:
#             s = mul(Braid(x1, 'artin'), Braid(x2, 'artin'))
#             if compare(bc, s, False):
#                 return s.generators
#     return "no luck"

# print(look_for_solutions2())

# print('ANSWER IS', look_for_solutions1())


# compare(mulAr([a02, a03, a_02, a_03]), bc, 'True')

# for i1, i2, i3, i4 in array_iter:
#     s = mulAr([i1, i2, i3, i4])
#     if compare(s, bc, False):
#         print(s)
    # l.append(mulAr([i1, i2,i3,i4]))


# compare(b2, b3, True)
# fully_reduce(b3)


def main():

    print("insert values for k1, k2, k3, a11, a12, a13, a21, a22, a23, a31, a32, a33")
    a = list(map(int, input().split(",")))
    assert len(a) == 12

    for a_ in a:
        print(a_)




if __name__ == '__main__':
    main()

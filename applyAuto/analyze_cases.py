def make_smaller(aa : str, cc : str):
    # print(aa, cc)
    cc = cc.replace(aa, '')
    # print(aa, cc)
    return aa, cc


def analyze_cases():
    count_non_obviously_trivial_presentations = 0
    with open("testCases/test_cases.txt", "r") as f:
        for ind, line in enumerate(f):
            aa, bb, cc, dd = [s.strip() for s in line.strip().split(",")]
            # print(f"a= {aa}, b= {bb}, c= {cc}, d= {dd}")
            if len(make_smaller(aa, cc)[1]) <= 1 or len(make_smaller(cc, aa)[1]) <= 1:
                continue
            count_non_obviously_trivial_presentations += 1
            print(f"case {aa}, {cc} is non-obviously trivial")
    return count_non_obviously_trivial_presentations


if __name__ == "__main__":
    print(analyze_cases())
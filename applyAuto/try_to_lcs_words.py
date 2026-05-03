import apply_hom, lcs_depths, graded

def main():
    with open("testCases/test_cases.txt", "r") as f:
        for ind, line in enumerate(f):
            if ind <= 5:
                continue
            aa, bb, cc, dd = [s.strip() for s in line.strip().split(",")]
            for image1 in apply_hom.LCS_CANDIDATES:
                for image2 in apply_hom.LCS_CANDIDATES:
                    a_ = apply_hom.apply_hom(aa, image1[1], image2[1])
                    b_ = apply_hom.apply_hom(bb, image1[1], image2[1])
                    c_ = apply_hom.apply_hom(cc, image1[1], image2[1])
                    d_ = apply_hom.apply_hom(dd, image1[1], image2[1])
                    dep1 = lcs_depths.lcs_depth(a_)
                    if lcs_depths.lcs_depth(a_) ==lcs_depths.lcs_depth(b_) == lcs_depths.lcs_depth(c_) == lcs_depths.lcs_depth(d_):
                        checker = graded.check_free_abelian_rank(words={a_, b_, c_, d_}, n=dep1)
                        if checker['rank'] == checker['expected_rank']:
                            print(f"win!!, {a_}, {b_}, {c_}, {d_}, {image1}, {image2}")
                            break
                        if checker['rank'] >= 3:
                            print(f"almost win!!, {a_}, {b_}, {c_}, {d_}, {image1}, {image2}, {ind}")
                            break
            if ind >= 15:
                break
if __name__ == "__main__":
    main()


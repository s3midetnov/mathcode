import z3


def solve_system_z3():
    k1, k2, k3, t = z3.Ints('k1 k2 k3 t')
    b12, a21, a31, a22, a32, a23, a33, b23, a11, a12, a13 = z3.Ints('b12 a21 a31 a22 a32 a23 a33 b23 a11 a12 a13')

    vars_list = [k1, k2, k3, t, b12, a21, a31, a22, a32, a23, a33, b23, a11, a12, a13]
    var_names = ['k1', 'k2', 'k3', 't', 'b12', 'a21', 'a31', 'a22', 'a32', 'a23', 'a33', 'b23', 'a11', 'a12', 'a13']

    # The exact example you want to check for (b13=4 means t=1)
    target_solution = {
        'k1': 2, 'k2': 4, 'k3': 6, 't': 1,
        'b12': 2, 'a21': 1, 'a31': 2,
        'a22': 0, 'a32': 4, 'a23': -4,
        'a33': 0, 'b23': 2, 'a11': 0,
        'a12': -1, 'a13': -2
    }

    def z3_abs(x):
        return z3.If(x >= 0, x, -x)

    def z3_custom_pow(base, exp):
        abs_exp = z3.If(exp < 0, -exp, exp)
        int_power = z3.ToInt(base ** z3.ToReal(abs_exp))
        return z3.If(exp < 0, -int_power, int_power)

    S = 0
    while True:
        print(f"\n--- Searching for solutions with Sum of Absolute Values (S) = {S} ---")
        solver = z3.Solver()

        # 1. Base constraints
        solver.add(k1 >= 0)
        solver.add(k2 >= k1)
        solver.add(k3 >= k2)

        sum_abs = sum(z3_abs(v) for v in vars_list)
        solver.add(sum_abs == S)

        # 2. Pre-compute powers and derived variables
        b13 = z3_custom_pow(2, k3 - k2) * t
        p_k1 = z3_custom_pow(2, k1)
        p_k2 = z3_custom_pow(2, k2)
        p_k3 = z3_custom_pow(2, k3)
        p_k2_k1 = z3_custom_pow(2, k2 - k1)
        p_k3_k2 = z3_custom_pow(2, k3 - k2)
        p_k1_plus_k3 = z3_custom_pow(2, k1 + k3)

        # 3. The 9 original modulo conditions
        solver.add((b12 * a21 + t * a31) % p_k1 == 0)
        solver.add((b12 * a22 + t * a32) % p_k1 == 0)
        solver.add((b12 * a23 + t * a33) % p_k1 == 0)

        solver.add((p_k2_k1 * b12 * a11 - b23 * a31) % p_k1 == 0)
        solver.add((p_k2_k1 * b13 * a11 + p_k3_k2 * b23 * a21) % p_k1 == 0)

        solver.add((p_k2_k1 * b12 * a12 - b23 * a32) % p_k2 == 0)
        solver.add((p_k2_k1 * b13 * a12 + p_k3_k2 * b23 * a22) % p_k2 == 0)

        solver.add((p_k2_k1 * b12 * a13 - b23 * a33) % p_k2 == 0)
        solver.add((p_k2_k1 * b13 * a13 + p_k3_k2 * b23 * a23) % p_k3 == 0)

        # 4. Exclude condition 1: Divisibility rules
        skip_divisibility = z3.And(
            b12 % p_k1 == 0,
            (b13 * p_k2) % p_k1_plus_k3 == 0,
            b23 % p_k2 == 0
        )
        solver.add(z3.Not(skip_divisibility))

        # 5. NEW Exclude condition 2: No zero-rows in the matrix
        zero_row_1 = z3.And(a11 == 0, a12 == 0, a13 == 0)
        zero_row_2 = z3.And(a21 == 0, a22 == 0, a23 == 0)
        zero_row_3 = z3.And(a31 == 0, a32 == 0, a33 == 0)

        skip_zero_rows = z3.Or(zero_row_1, zero_row_2, zero_row_3)
        solver.add(z3.Not(skip_zero_rows))

        found_any = False

        # 6. Search loop
        while solver.check() == z3.sat:
            found_any = True
            model = solver.model()

            solution = {name: model.eval(var, model_completion=True).as_long()
                        for name, var in zip(var_names, vars_list)}

            print(solution)

            # Target check
            if all(solution[k] == v for k, v in target_solution.items()):
                print("\n" + "=" * 40)
                print("       ORIGINAL RIPS EXAMPLE!!!")
                print("=" * 40 + "\n")

            # Block the current solution to find the next one
            block_condition = [var != solution[name] for name, var in zip(var_names, vars_list)]
            solver.add(z3.Or(block_condition))

        if not found_any:
            print("No solutions found for this sum.")

        S += 1


if __name__ == "__main__":
    solve_system_z3()
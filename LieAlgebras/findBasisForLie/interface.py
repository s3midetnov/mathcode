import ast
import subprocess

def main():
    with open("input.txt", "w") as f:
        f.write("")
    print("insert values for k1, k2, k3, a11, a12, a13, a21, a22, a23, a31, a32, a33 (comma-separated)\n original Rips example (for tests) is : 2,4,6,0,-1,-2,1,0,-4,2,4,0 \n ")
    input_str = input()
    try:
        a_vals = [int(x.strip()) for x in input_str.split(",")]
    except ValueError:
        print("Invalid input: Please enter 12 integers separated by commas.")
        return

    if len(a_vals) != 12:
        print(f"Expected 12 values, got {len(a_vals)}.")
        return

    k1, k2, k3 = a_vals[0:3]
    a11, a12, a13 = a_vals[3:6]
    a21, a22, a23 = a_vals[6:9]
    a31, a32, a33 = a_vals[9:12]

    # Construct the matrix 'a' for GAP
    gap_a = f"[[{a11},{a12},{a13}],[{a21},{a22},{a23}],[{a31},{a32},{a33}]]"
    gap_vars = f"k1:={k1}; k2:={k2}; k3:={k3}; a:={gap_a};"

    # Command to run GAP
    cmd = ["gap", "-q", "-b", "-c", gap_vars, "findBasisCongruences.g"]

    try:
        # Run GAP and capture the output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Output from GAP for basis:")
        gap_output_bases = result.stdout.strip()
        gap_output_bases_parsed = ast.literal_eval(gap_output_bases)
        print(gap_output_bases_parsed)
        for basic_element in gap_output_bases_parsed:
            b12 = basic_element[0]
            b13 = basic_element[1] * (2 ** (k3 - k2))
            b23 = basic_element[2]
            with open("input.txt", "a") as f:
                f.write(f"k1 = {k1}, k2 = {k2}, k3 = {k3}, a11 = {a11}, a12 = {a12}, a13 = {a13}, a21 = {a21}, a22 = {a22}, a23 = {a23}, a31 = {a31}, a32 = {a32}, a33 = {a33}, b12 = {b12}, b13 = {b13}, b23 = {b23}\n")
        print("calling another GAP program to check triviality mod LCS")
        cmd_is_zero = ["gap", "-q", "-b", "-c", gap_vars, "isZeroModLCS.g"]
        result = subprocess.run(cmd_is_zero, capture_output=True, text=True, check=True)
        print("Output from GAP for triviality:")
        output_triviality = result.stdout.strip()
        print(output_triviality)
    except subprocess.CalledProcessError as e:
        print(f"Error running GAP: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
    except FileNotFoundError:
        print("The command 'gap' was not found in your PATH. Please ensure GAP is installed and accessible as 'gap'.")

if __name__ == '__main__':
    main()

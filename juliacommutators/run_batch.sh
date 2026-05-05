#!/usr/bin/env bash
# run_batch.sh — generate a random batch and append it to the database.
#
# Usage: ./run_batch.sh [TWO_N] [THREE_N]
#   TWO_N    random two-relator automorphisms to attempt  (default: 50000)
#   THREE_N  random three-relator automorphisms to attempt (default: 500)
#
# Steps:
#   1. Generate random two-relator lines   (gen_two_batch.jl)
#   2. Generate random three-relator lines (gen_three_batch.jl)
#   3. Lift two-relators to F3             (apply23_batch.jl)
#   4. Lift three-relators to F3           (apply33_batch.jl)
#   5. Append two-relator data to DB       (db_append_two.py)
#   6. Append three-relator data to DB     (db_append_three.py)

set -euo pipefail
cd "$(dirname "$0")"

TWO_N="${1:-50000}"
THREE_N="${2:-500}"
WD="$(pwd)/working_with_data"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "=== [1/6] Generating $TWO_N random two-relator lines ==="
julia gen_two_batch.jl "$TMP/two.txt" "$TWO_N"

echo "=== [2/6] Generating $THREE_N random three-relator lines ==="
julia gen_three_batch.jl "$TMP/three.txt" "$THREE_N"

echo "=== [3/6] Lifting two-relators to F3 ==="
julia apply23_batch.jl "$TMP/two.txt" "$TMP/twoF3.txt"

echo "=== [4/6] Lifting three-relators to F3 ==="
julia apply33_batch.jl "$TMP/three.txt" "$TMP/threeF3.txt"

echo "=== [5/6] Appending two-relator data to database ==="
cd "$WD"
python3 db_append_two.py "$TMP/twoF3.txt"

echo "=== [6/6] Appending three-relator data to database ==="
python3 db_append_three.py "$TMP/threeF3.txt"

echo "=== Done ==="

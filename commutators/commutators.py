import random

# Set a seed so the "arbitrary" shuffle is reproducible
random.seed(42)


class Commutator:
    def __init__(self, rep, left=None, right=None, weight=1, letters=None):
        self.rep = rep  # String representation
        self.left = left  # u
        self.right = right  # v
        self.weight = weight
        self.letters = letters  # Set of letters used

    def __repr__(self):
        return self.rep


def count_specific_commutators(n_letters, target_weight):
    # Store all commutators by weight in a dictionary
    # layers[k] will hold a LIST of commutators
    layers = {}

    # --- LAYER 1: Letters ---
    # "With the default order x1 < ... < xn"
    # We DO NOT shuffle layer 1. The index determines the order.
    layer_1 = []
    for i in range(1, n_letters + 1):
        c = Commutator(f"x{i}", weight=1, letters={i})
        layer_1.append(c)

    layers[1] = layer_1

    # --- HELPER: COMPARISON FUNCTION ---
    def compare(c1, c2):
        """
        Returns:
         1 if c1 > c2
         0 if c1 == c2 (shouldn't happen for distinct objects)
        -1 if c1 < c2
        """
        # Rule A: Higher weight is bigger
        if c1.weight > c2.weight:
            return 1
        if c1.weight < c2.weight:
            return -1

        # Rule B: Same weight -> Use Arbitrary Order (Index in the layer list)
        # We need to find where they sit in their respective layer list
        w = c1.weight
        layer = layers[w]

        # Optimization: indices can be cached, but .index() is fine for small n
        idx_1 = layer.index(c1)
        idx_2 = layer.index(c2)

        if idx_1 > idx_2:
            return 1
        elif idx_1 < idx_2:
            return -1
        return 0

    # --- BUILD ITERATIVELY ---
    for k in range(2, target_weight + 1):
        new_commutators = []

        # Try all splits a + b = k
        for weight_u in range(1, k):
            weight_v = k - weight_u

            list_u = layers[weight_u]
            list_v = layers[weight_v]

            for u in list_u:
                for v in list_v:
                    # 1. Disjoint letters
                    if not u.letters.isdisjoint(v.letters):
                        continue

                    # 2. u > v
                    if compare(u, v) <= 0:
                        continue

                    # 3. Hall Condition: If u = [x, y], then v >= y
                    # Only applies if u is composite (weight > 1)
                    if u.weight > 1:
                        y = u.right
                        # We need v >= y (means compare(v,y) is 1 or 0)
                        if compare(v, y) < 0:
                            continue

                    # If passed, create commutator
                    new_rep = f"[{u.rep}, {v.rep}]"
                    new_letters = u.letters | v.letters
                    new_comm = Commutator(new_rep, left=u, right=v, weight=k, letters=new_letters)
                    new_commutators.append(new_comm)

        # --- ARBITRARY ORDERING STEP ---
        # Shuffle specifically for the next iteration's comparisons
        random.shuffle(new_commutators)

        layers[k] = new_commutators
        print(f"Weight {k}: Found {len(new_commutators)} specific commutators.")

    return layers[target_weight]
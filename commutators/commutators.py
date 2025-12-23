import itertools
import random

# Set a seed so the "arbitrary" shuffle is reproducible for this demo
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
    # --- LAYER 1: Letters ---
    # We order letters x1 < x2 < ... < xn strictly
    layer_1 = []
    for i in range(1, n_letters + 1):
        c = Commutator(f"x{i}", weight=1, letters={i})
        layer_1.append(c)

    # Store all commutators by weight in a dictionary
    # layers[k] will hold a LIST of commutators of weight k
    # The INDEX in this list represents the "Arbitrary Order"
    layers = {1: layer_1}

    # --- BUILD ITERATIVELY UP TO TARGET WEIGHT ---
    for k in range(2, target_weight + 1):
        new_commutators = []

        # Try all splits a + b = k
        for weight_u in range(1, k):
            weight_v = k - weight_u

            # Get the lists from previous layers
            # These lists are already "ordered" arbitrarily by their indices
            list_u = layers[weight_u]
            list_v = layers[weight_v]

            # Iterate through all u in Layer a and v in Layer b
            for u in list_u:
                for v in list_v:

                    # --- CHECK CONDITIONS ---

                    # 1. Disjoint letters
                    if not u.letters.isdisjoint(v.letters):
                        continue

                    # 2. u > v
                    # We compare using the global rules:
                    # A. Higher weight is bigger
                    if u.weight > v.weight:
                        pass  # Condition met
                    elif v.weight > u.weight:
                        continue  # Fail
                    else:
                        # B. Same weight: Use the "Arbitrary Order" defined in the layers dict
                        # We simply check if u appears AFTER v in the list
                        # Note: We need to find their indices in the stored layer
                        idx_u = list_u.index(u)
                        idx_v = list_v.index(v)
                        if idx_u <= idx_v:
                            continue  # u must be > v (come after in the list)

                    # 3. Hall Condition: If u = [x, y], then v >= y
                    if u.weight > 1:
                        y = u.right
                        # We need to check if v >= y

                        # Compare weights of v and y
                        if v.weight > y.weight:
                            pass  # v is bigger (Condition met)
                        elif v.weight < y.weight:
                            continue  # v is smaller (Fail)
                        else:
                            # Same weight -> Compare indices in their layer
                            idx_v = layers[v.weight].index(v)
                            idx_y = layers[y.weight].index(y)
                            if idx_v < idx_y:
                                continue  # v is smaller (Fail)

                    # If we pass all checks, create the commutator
                    new_rep = f"[{u.rep}, {v.rep}]"
                    new_letters = u.letters | v.letters
                    new_comm = Commutator(new_rep, left=u, right=v, weight=k, letters=new_letters)
                    new_commutators.append(new_comm)

        # --- ARBITRARY ORDERING STEP ---
        # Once we built the commutators of weight k, we order them arbitrarily.
        # We simulate this by shuffling the list.
        random.shuffle(new_commutators)

        layers[k] = new_commutators
        print(f"Weight {k}: Found {len(new_commutators)} specific commutators.")

    return layers[target_weight]

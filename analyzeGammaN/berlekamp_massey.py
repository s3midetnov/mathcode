"""
Berlekamp-Massey over GF(p) applied to the flat coordinate sequence of y.
The sequence is: all coords of y concatenated weight-by-weight.
If a short LFSR exists mod p, the sequence is "algebraically structured."
"""

# Flat coord sequence extracted from solve_exact.g output (weights 1..11)
# Zeros are included for missing positions within each weight level.
# Format: extract from the printed output manually.

# From the GAP output, weight-by-weight (filling missing positions with 0):

w1 = [1, -1]                           # 2 gens
w2 = [-1]                              # 1 gen
w3 = [0, 1]                            # 2 gens
w4 = [0, 0, -1]                        # 3 gens
w5 = [0, 0, 0, 1, -1, 1]              # 6 gens
w6 = [0, 0, 0, -1, 1, 0, -2, 2, -1]  # 9 gens
w7 = [0]*18  # fill below
w8 = [0]*30
w9 = [0]*56
w10 = [0]*99
w11 = [0]*186

# Weight 7 (18 gens): pos6=1 pos7=-1 pos10=1 pos12=1 pos13=-3 pos15=1 pos16=3 pos17=-3 pos18=1
for pos, val in [(6,1),(7,-1),(10,1),(12,1),(13,-3),(15,1),(16,3),(17,-3),(18,1)]:
    w7[pos-1] = val

# Weight 8 (30 gens): pos7=-1 pos8=1 pos10=-1 pos14=1 pos17=-1 pos18=2 pos19=1 pos20=-1
#   pos21=-5 pos22=1 pos25=6 pos27=-3 pos28=-4 pos29=4 pos30=-1
for pos, val in [(7,-1),(8,1),(10,-1),(14,1),(17,-1),(18,2),(19,1),(20,-1),
                 (21,-5),(22,1),(25,6),(27,-3),(28,-4),(29,4),(30,-1)]:
    w8[pos-1] = val

# Weight 9 (56 gens): pos10=1 pos11=-1 pos14=1 pos17=-1 pos23=-1 pos25=3 pos28=1
#   pos29=-2 pos30=-1 pos31=1 pos32=3 pos37=-9 pos39=3 pos40=-1 pos42=1 pos44=-2
#   pos45=1 pos46=12 pos47=-2 pos48=1 pos50=-3 pos51=-10 pos52=-3 pos53=6 pos54=8 pos55=-6 pos56=1
for pos, val in [(10,1),(11,-1),(14,1),(17,-1),(23,-1),(25,3),(28,1),(29,-2),(30,-1),
                 (31,1),(32,3),(37,-9),(39,3),(40,-1),(42,1),(44,-2),(45,1),(46,12),
                 (47,-2),(48,1),(50,-3),(51,-10),(52,-3),(53,6),(54,8),(55,-6),(56,1)]:
    w9[pos-1] = val

# Weight 10 (99 gens)
for pos, val in [(13,-1),(14,1),(16,-1),(20,1),(24,1),(26,-3),(34,2),(36,-3),(37,-2),
                 (39,-1),(40,9),(41,-2),(42,2),(44,-1),(45,2),(46,1),(47,-1),(48,-3),
                 (51,1),(52,5),(53,1),(54,-2),(55,-2),(56,1),(58,-1),(60,3),(61,-5),
                 (62,-17),(63,-4),(64,-1),(65,2),(66,5),(67,12),(68,2),(70,-1),(71,2),
                 (73,1),(74,3),(75,3),(76,-2),(77,-1),(78,-3),(79,6),(80,6),(81,-21),
                 (82,-8),(83,6),(86,-2),(87,4),(88,21),(89,-17),(90,-6),(91,-4),(92,-8),
                 (93,5),(94,23),(95,12),(96,-12),(97,-18),(98,10),(99,-1)]:
    w10[pos-1] = val

# Weight 11 (186 gens)
for pos, val in [(20,1),(21,-1),(24,1),(27,-1),(32,-1),(34,3),(38,-2),(40,3),(41,2),
                 (43,1),(44,-9),(49,6),(50,-6),(55,-3),(57,4),(58,4),(60,1),(61,-8),
                 (62,-3),(64,5),(66,1),(67,-4),(68,-1),(69,4),(70,11),(71,-8),(72,4),
                 (73,-10),(74,1),(76,1),(77,-2),(78,-1),(79,1),(80,3),(84,-1),(85,-5),
                 (86,-1),(87,4),(88,-1),(91,2),(92,-1),(93,-2),(94,14),(95,2),(96,-5),
                 (97,2),(98,-10),(99,-2),(100,4),(101,2),(103,1),(104,-2),(105,-2),
                 (106,5),(107,-5),(108,-4),(109,2),(110,23),(111,-21),(112,11),(113,-5),
                 (114,24),(115,-15),(116,-4),(117,-6),(118,5),(119,-7),(120,-1),(121,-38),
                 (122,30),(123,13),(124,3),(126,1),(127,-2),(129,-2),(130,4),(131,-1),
                 (132,3),(133,-5),(134,2),(135,-6),(136,-5),(137,-5),(138,20),(139,-13),
                 (141,-6),(142,10),(143,5),(144,-11),(145,32),(146,8),(147,24),(148,5),
                 (149,37),(150,-37),(151,-101),(152,-37),(153,30),(154,31),(155,4),
                 (156,-4),(157,-3),(158,2),(159,-15),(160,-11),(161,-1),(162,2),(163,-50),
                 (164,52),(165,67),(166,19),(167,12),(168,-12),(169,-47),(171,22),
                 (172,-17),(173,-23),(174,-16),(175,-41),(176,31),(177,84),(178,10),
                 (179,21),(180,-6),(181,-89),(182,-30),(183,32),(184,37),(185,-17),(186,1)]:
    w11[pos-1] = val

flat = w1 + w2 + w3 + w4 + w5 + w6 + w7 + w8 + w9 + w10 + w11
print(f"Total sequence length: {len(flat)}")
print(f"Max |coord|: {max(abs(x) for x in flat)}")
print(f"Nonzero count: {sum(1 for x in flat if x != 0)}")


def berlekamp_massey(s, p):
    """Return the minimal LFSR length over GF(p) for sequence s."""
    n = len(s)
    s = [x % p for x in s]
    C = [1] + [0]*n
    B = [1] + [0]*n
    L, m, b = 0, 1, 1
    for i in range(n):
        d = s[i]
        for j in range(1, L+1):
            d = (d + C[j] * s[i-j]) % p
        if d == 0:
            m += 1
        elif 2*L <= i:
            T = C[:]
            coeff = d * pow(b, p-2, p) % p
            for j in range(m, n+1):
                C[j] = (C[j] - coeff * B[j-m]) % p
            L, B, b, m = i+1-L, T, d, 1
        else:
            coeff = d * pow(b, p-2, p) % p
            for j in range(m, n+1):
                C[j] = (C[j] - coeff * B[j-m]) % p
            m += 1
    return L


print("\nBerlekamp-Massey LFSR lengths over small primes:")
for p in [2, 3, 5, 7, 11, 13]:
    L = berlekamp_massey(flat, p)
    print(f"  GF({p}): minimal LFSR length = {L} (sequence length = {len(flat)})")
    if L < len(flat) // 2:
        print(f"    WARNING: short recurrence found! Ratio = {L}/{len(flat)//2}")
    else:
        print(f"    OK: LFSR length ≥ n/2 → no short recurrence mod {p}")

print("\nSign sequence of nonzero coords:")
signs = [1 if x > 0 else -1 for x in flat if x != 0]
print(signs[:60])

print("\nLast-generator coefficients by weight:")
weights = [w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11]
for i, wk in enumerate(weights, start=1):
    print(f"  w={i}: last coeff = {wk[-1]}, expected (-1)^{i-1} = {(-1)**(i-1)}, match={wk[-1]==(-1)**(i-1)}")

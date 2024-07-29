# print information
Decomp = True
KSKInnerProd = True

logN = 17
N = 2**logN         # number of coefficients in ciphertext ring
L = 35              # ciphertext level
dnum = 3            # number of limbs in switching key
beta = dnum
alpha = (L+1)/dnum
k = 13              # additional limbs for ksk


# Decomposition
Decomp_Mults = L * N * 2       # 2 multiplications for each limb, each limb has N elements
Decomp_Ops = Decomp_Mults
Decomp_limb_read = L * N * 8   # read each limb once, each element is 8 byte
Decomp_limb_write = L * N * 8  # write each limb once
Decomp_DRAM = Decomp_limb_read + Decomp_limb_write
Decomp_AI = float(Decomp_Ops) / Decomp_DRAM

if (Decomp):
    print("Decomposition")
    print("    Operations (GOP): ", Decomp_Ops * 1e-9) 
    print("    Multiplications (GOP): ", Decomp_Mults * 1e-9)
    print("    DRAM_transfer (GB): ", Decomp_DRAM * 1e-9)
    print("    Limb_read (GB): ", Decomp_limb_read * 1e-9)
    print("    Limb_write (GB): ", Decomp_limb_write * 1e-9)
    print("    Key_read (GB): ", 0)
    print("    AI: ", Decomp_AI)


# KSKInnerProd
KSK_Mults = 2 * dnum * (k+L) * N
KSK_Adds = 2 * (dnum-1) * (k+L) * N
KSK_Ops = KSK_Mults + KSK_Adds
KSK_limb_read = dnum * (k+L) * N * 8
KSK_limb_write = 0                      # no limbs write, because limbs are immediately used in the ModDown
KSK_key_read = 2 * dnum * (k+L) * N * 8
KSK_DRAM = KSK_limb_read + KSK_key_read
KSK_AI = float(KSK_Ops) / KSK_DRAM

if (KSKInnerProd):
    print("\nKSKInnerProd")
    print("    Multiplications (GOP): ", KSK_Mults * 1e-9)
    print("    Additions (GOP): ", KSK_Adds * 1e-9)
    print("    Operations (GOP): ", KSK_Ops * 1e-9)
    print("    Limb_read (GB): ", KSK_limb_read * 1e-9)
    print("    Limb_write (GB): ", KSK_limb_write * 1e-9)
    print("    Key_read (GB): ", KSK_key_read * 1e-9)
    print("    DRAM_transfer (GB): ", KSK_DRAM * 1e-9)
    print("    AI: ", KSK_AI)


# NTT/iNTT for each ciphertext
# NTT_L_Mults = L * N/2 * logN
# NTT_Lk_Mults = (L+k) * N/2 * logN
# NTT_L_Adds = NTT_L_Mults * 2
# NTT_Lk_Adds = NTT_Lk_Mults * 2
NTT_L_limb_size = L * N * 8                 # limb-wise read
NTT_Lk_limb_size = (L+k) * N * 8
iNTT_ModUp_Mults = L * N/2 * logN
iNTT_ModUp_Adds = iNTT_ModUp_Mults * 2
iNTT_ModDown_Mults = (L+k) * N/2 * logN
iNTT_ModDown_Adds = iNTT_ModDown_Mults * 2
NTT_ModUp_Mults = beta * (L+k-alpha) * N/2 * logN
NTT_ModUp_Adds = NTT_ModUp_Mults * 2
NTT_ModDown_Mults = L * N/2 * logN
NTT_ModDown_Adds = NTT_ModDown_Mults * 2



# RNS basis conversion for each ciphertext
RNS_Conv_ModUp_Mults = (k+L-alpha) * beta * N           # RNS_Conv_ModUp_Mults = (k+L-alpha) * 2 * (alpha-1) * N
RNS_Conv_ModUp_Adds = (k+L-alpha) * alpha * beta * N    # RNS_Conv_ModUp_Adds = (k+L-alpha) * (alpha-1) * N
RNS_Conv_ModDown_Mults = (alpha*beta) * N               # RNS_Conv_ModDown_Mults = L * 2 * (L+k-1) * N
RNS_Conv_ModDown_Adds = k * (alpha*beta) * N            # RNS_Conv_ModDown_Adds = L * (L+k-1) * N
RNS_Conv_ModUp_limb_read = alpha*beta * N * 8              # RNS_Conv_ModUp_limb_read = L * N * 8        # slot-wise read
RNS_Conv_ModUp_limb_wirte = beta * (alpha*beta+k) * N * 8  # RNS_Conv_ModUp_limb_wirte = k * N * 8   
RNS_Conv_ModDown_limb = (L+k) * N * 8


# ModUp
ModUp_Mults = iNTT_ModUp_Mults + RNS_Conv_ModUp_Mults + NTT_ModUp_Mults
ModUp_Adds = iNTT_ModUp_Adds + RNS_Conv_ModUp_Adds + NTT_ModUp_Adds
ModUp_Ops = ModUp_Mults + ModUp_Adds
ModUp_limb_read = NTT_L_limb_size + RNS_Conv_ModUp_limb_read
ModUp_limb_write = RNS_Conv_ModUp_limb_wirte + NTT_Lk_limb_size
ModUp_DRAM = ModUp_limb_read + ModUp_limb_write
ModUp_AI = float(ModUp_Ops) / ModUp_DRAM

print("\nModUp")
print("    Multiplications (GOP): ", ModUp_Mults * 1e-9)
print("    Additions (GOP): ", ModUp_Adds * 1e-9)
print("    Operations (GOP): ", ModUp_Ops * 1e-9)
print("    Limb_read (GB): ", ModUp_limb_read * 1e-9)
print("    Limb_write (GB): ", ModUp_limb_write * 1e-9)
print("    Key_read (GB): ", 0)
print("    DRAM_transfer (GB): ", ModUp_DRAM * 1e-9)
print("    AI: ", ModUp_AI)


# ModDown
ModDown_Mults = iNTT_ModDown_Mults + RNS_Conv_ModDown_Mults + NTT_ModDown_Mults
ModDown_Adds = iNTT_ModDown_Adds + RNS_Conv_ModDown_Adds + NTT_ModDown_Adds
ModDown_Ops = ModDown_Mults + ModDown_Adds
ModDown_limb_read = NTT_Lk_limb_size + RNS_Conv_ModDown_limb
ModDown_limb_write = RNS_Conv_ModDown_limb + NTT_L_limb_size
ModDown_DRAM = ModDown_limb_read + ModDown_limb_write
ModDown_AI = float(ModDown_Ops) / ModDown_DRAM

print("\nModDown")
print("    Multiplications (GOP): ", ModDown_Mults * 1e-9)
print("    Additions (GOP): ", ModDown_Adds * 1e-9)
print("    Operations (GOP): ", ModDown_Ops * 1e-9)
print("    Limb_read (GB): ", ModDown_limb_read * 1e-9)
print("    Limb_write (GB): ", ModDown_limb_write * 1e-9)
print("    Key_read (GB): ", 0)
print("    DRAM_transfer (GB): ", ModDown_DRAM * 1e-9)
print("    AI: ", ModDown_AI)

# Automorph
Automorph_limb_read = L * N * 8
Automorph_limb_write = L * N * 8
Automorph_DRAM = Automorph_limb_read + Automorph_limb_write
print("\nAutomorph")
print("    Limb_read (GB): ", 2 * Automorph_limb_read * 1e-9)
print("    Limb_write (GB): ", 2 * Automorph_limb_write * 1e-9)
print("    DRAM_transfer (GB): ", 2 * Automorph_DRAM * 1e-9)

# rotate
Rotate_Ops = Decomp_Ops + ModUp_Ops + KSK_Ops + ModDown_Ops*2     # Decomp + ModUp + KSKInnerProd + ModDown
Rotate_DRAM = Decomp_DRAM + ModUp_DRAM + KSK_DRAM + ModDown_DRAM*2
Rotate_key_read = KSK_key_read     # KSKInnerProd and Automorph, same key
Rotate_AI = float(Rotate_Ops) / Rotate_DRAM
print("\nRotate")
print("    Operations (GOP): ", Rotate_Ops * 1e-9)
print("    DRAM_transfer (GB): ", Rotate_DRAM * 1e-9)
print("    Key_read (GB): ", Rotate_key_read * 1e-9)
print("    AI: ", Rotate_AI)


# CoeffToSlot
radix = 2**4
num_matrices = 4
# before BSGS
num_diagonals = (2*radix-1) * num_matrices 
num_rotations = (2*radix-2) * num_matrices
# after BSGS
num_rotations_BSGS = (7+3) * num_matrices
num_mults = (8*4) * num_matrices
num_adds = (7*3) * num_matrices

CoeffToSlot_Ops = num_rotations_BSGS * Rotate_Ops + (num_mults + num_adds) * N/2 * (L+k)
CoeffToSlot_key_read = num_rotations_BSGS * Rotate_key_read
CoeffToSlots_DRAM = num_rotations_BSGS * Rotate_DRAM  + num_rotations_BSGS * N/2 * (L+k) * 8
CoeffToSlots_AI = float(CoeffToSlot_Ops) / CoeffToSlots_DRAM
print("\nCoeffToSlot")
print("    Operations (GOP): ", CoeffToSlot_Ops * 1e-9)
print("    Key_read (GB): ", CoeffToSlot_key_read * 1e-9)
print("    DRAM_transfer (GB): ", CoeffToSlots_DRAM * 1e-9)
print("    AI: ", CoeffToSlots_AI)
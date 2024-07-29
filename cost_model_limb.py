import math

# 100x poseidon ARK MAD
# FHE parameters
logN = 16  
N = 2**logN     # polynomial degree
L = 22          # maximum ciphertext level (maximum number of limbs minus 1)
k = 9          # additional limbs for key switch
dnum = 3        # number of digits in switching key
beta = dnum
alpha = int(math.ceil((L+1)/dnum))              # number of limbs comprising a digit after decomposition: fixed

# ciphertext/plaintext/limb/key property
coeff_size = 32*8/64;
one_limb_size = N * coeff_size                       # size of one limb
ct_Q_size = 2 * one_limb_size * (L+1)       # size of one ciphertext
ct_PQ_size = 2 * one_limb_size * (L+k+1)
key_size = 2 * beta * N * coeff_size                 # size of one rotation key
print("Data property: ")
print("     one_limb_size (MB): ", one_limb_size / 1e6)
print("     ct_beta_plus_1_size (MB): ", one_limb_size * (beta+1) / 1e6)
print("     ct_Q_size (MB): ", ct_Q_size / 1e6)
print("     ct_PQ_size (MB): ", ct_PQ_size / 1e6)   
print("     one_key_size (MB): ", key_size / 1e6)

# matrix factorization param
matrix_merged_per_stage =  4      
r = 2**4    # radix
fft_stage = int(math.ceil(logN / matrix_merged_per_stage))
diag_per_stage = 2*r-1
pt_size = diag_per_stage * one_limb_size
print("Matrix factorization: ")
print("     pt_size (MB): ", pt_size / 1e6)

# architecture specification
vector_line_size = 512  # parallelism 512
HBM_bw = 460e9    # 460 GB/s
freq = 3e8              # 300 MHz
modMult = 12             # 9 cycles for one modular multiplication
modAdd = 1              # 5 cycles for one modular addition
modSub = 1              # 5 cycles for one modular subtraction
modMAC = 13             # 12 cycles for one modular multiply accumulate

# NTT
def NTT(limb):
    permute = 2*N/vector_line_size
    lat1 =modMAC + (N/vector_line_size * logN + permute*(logN-1)) * limb    # pipeline latency
    return lat1


# Decomposition
def decomp(pre_limb):
    decomp_mult = pre_limb * 2
    return modMult + N * decomp_mult / vector_line_size

# basic conversion
def basis_conv(pre_limb, new_limb):
    bc_mult = 2 * pre_limb * new_limb
    # bc_add = 2 * (pre_limb-1) * new_limb
    # bc_cycles = N * (bc_mult + bc_add) / vector_line_size
    bc_cycles = modMult + N * bc_mult/vector_line_size
    return bc_cycles

def modup(pre_limb, new_limb):
    modup_intt_cycles = NTT(pre_limb)
    modup_ntt_cycles = NTT(k)
    modup_bc_cycles = basis_conv(pre_limb, k)
    return modup_intt_cycles + modup_ntt_cycles + modup_bc_cycles

def moddown(pre_limb, new_limb):
    moddown_mult = new_limb
    moddown_sub = new_limb
    # moddown_cycles = N * (moddown_mult + moddown_sub) / vector_line_size
    moddown_extra_compute_cycles = (moddown_mult + moddown_sub) + N/vector_line_size
    return NTT(k) + basis_conv(k, new_limb) + moddown_extra_compute_cycles + NTT(new_limb)
   
def automorph_read(limb):
    return limb * (one_limb_size / HBM_bw)
          
def automorph_permute(limb):
    return limb * (2*N/vector_line_size)/freq

def KeyMS(limb):
    time = modMAC + N/vector_line_size * limb * 2;  # pipeline latency
    return time

def DiagMS(limb):
    time = modMAC + N/vector_line_size * limb * 2;  # pipeline latency
    return time

def ma(limb):
    compute = modAdd + (N/vector_line_size)*limb
    return compute


# plaintext preparation: we ignore pre-compute time
pre_limbs = diag_per_stage
transfer_pre_time = pre_limbs * one_limb_size / HBM_bw 
transfer_one_stage_time = (L+k+1) * transfer_pre_time
transfer_total_time = fft_stage * transfer_one_stage_time
# print("NTT_one_limb_time (us): ", NTT(1) / freq * 1e6)
print("Plaintext preparation: ")
print("     pre_limb_size (MB): ", pre_limbs * one_limb_size / 1e6)
print("     transfer_pre_time (us): ", transfer_pre_time * 1e6)
print("     transfer_one_stage_time (us): ", transfer_one_stage_time * 1e6)
print("     transfer_total_time (us): ", transfer_total_time * 1e6)

HDFT_total_time = 0
print("\nHDFT operation: ")
for stage in range(fft_stage):
    ct_in_size = 2 * (L+1-stage) * one_limb_size
    decomp_read_time = ct_in_size / HBM_bw 
    decomp_compute_time = decomp(L+1-stage) / freq
    decomp_total_time = decomp_read_time + decomp_compute_time
    # modup_read_time = ((beta-1) * alpha + 1 * (alpha-stage) + 1 * (L+1-stage)) * one_limb_size / HBM_bw     # same as ct_in_size
    modup_intt_time = ((beta-1) * NTT(alpha) + NTT(alpha-stage) + NTT(L+1-stage)) / freq
    modup_bc_time = ((beta-1) * basis_conv(alpha, L+k-1) + basis_conv(alpha-stage, L+k-1) + basis_conv(L+1-stage, L+k+1)) / freq
    modup_ntt_time = (beta+1) * NTT(k) / freq
    modup_compute_time = modup_intt_time + modup_bc_time + modup_ntt_time
    ct_after_modup_size = (beta+1) * (L+k+1) * one_limb_size
    # modup_write_time = ct_after_modup_size / HBM_bw
    modup_total_time = modup_compute_time
    ct_prep_time = decomp_total_time + modup_total_time
    print("Stage ", stage+1)
    print("Ciphertext preparation: ")
    print("     ct_in_size (MB): ", ct_in_size / 1e6)
    print("     decomp_read_time (us): ", decomp_read_time * 1e6)
    print("     decomp_compute_time (us): ", decomp_compute_time * 1e6)
    # print("     decomp_write_time (us): ", decomp_write_time * 1e6)
    print("     decomp_total_time (us): ", decomp_total_time * 1e6)
    # print("     modup_read_time (us): ", modup_read_time * 1e6)
    print("     modup_intt_time (us): ", modup_intt_time * 1e6)
    print("     modup_bc_time (us): ", modup_bc_time * 1e6)
    print("     modup_ntt_time (us): ", modup_ntt_time * 1e6)
    print("     modup_compute_time (us): ", modup_compute_time * 1e6)
    print("     ct_after_modup_size (MB): ", ct_after_modup_size / 1e6)
    # print("     modup_write_time (us): ", modup_write_time * 1e6)
    print("     modup_total_time (us): ", modup_total_time * 1e6)
    print("     ct_prep_time (us): ", ct_prep_time * 1e6)
    
    print("PtMatVec operation: ")
    automorph_read_time = automorph_read(beta+1)
    automorph_permute_time = automorph_permute(beta+1) * diag_per_stage
    automorph_time = automorph_read_time+automorph_permute_time
    KeyMultSum_once_time = KeyMS(beta) / freq
    ma_once_time = ma(1) / freq
    DiagMultSum_once_time = DiagMS(1) / freq
    DiagMultSum_time = DiagMultSum_once_time * diag_per_stage
    limbflow_time = (automorph_time + KeyMultSum_once_time + ma_once_time + DiagMultSum_time)*(L+k+1-stage)
    Write_time = 2 * (L+k+1-stage) * one_limb_size / HBM_bw
    limbflow_total_time = limbflow_time + Write_time
    # DiagMultSum_total_time = DiagMultSum_once_time + DiagMultSum_compute_time + DiagMultWrite_time
    modDown_read_time = 2 * (L+k+1-stage) * one_limb_size / HBM_bw
    modDown_iNTT_time = 2 * NTT(k) / freq
    modDown_bc_time = 2 * basis_conv(k, L-stage) / freq
    modDown_NTT_time = 2 * NTT(L-stage) / freq
    modDown_extra_time = (modMult + N/vector_line_size * (L-stage) * 2) / freq
    modDown_compute_time = modDown_iNTT_time + modDown_bc_time + modDown_NTT_time + modDown_extra_time
    # modDown_compute_time_func = 2 * moddown(L+k+1, L+1-stage) / freq
    modDown_write_time = 2 * (L+1-stage) * one_limb_size / HBM_bw
    modDown_total_time = modDown_read_time + modDown_compute_time + modDown_write_time
    PtMatVec_one_stage_time = limbflow_total_time + modDown_total_time
    print("     automorph_read_time (us): ", automorph_read_time * 1e6)
    print("     automorph_permute_time (us): ", automorph_permute_time * 1e6)
    print("     automorph_time (us): ", automorph_time * 1e6)
    print("     KeyMultSum_once_time (us): ", KeyMultSum_once_time * 1e6)
    print("     ma_once_time (us): ", ma_once_time * 1e6)
    print("     DiagMultSum_once_time (us): ", DiagMultSum_once_time * 1e6)
    print("     DiagMultSum_time (us): ", DiagMultSum_time * 1e6)
    print("     limbflow_total_time (us): ", limbflow_total_time * 1e6)
    print("     Write_time (us): ", Write_time * 1e6)
    print("     limbflow_time (us): ", limbflow_time * 1e6)
    print("     modDown_read_time (us): ", modDown_read_time * 1e6)
    print("     modDown_iNTT_time (us): ", modDown_iNTT_time * 1e6)
    print("     modDown_bc_time (us): ", modDown_bc_time * 1e6)
    print("     modDown_NTT_time (us): ", modDown_NTT_time * 1e6)
    print("     modDown_extra_time (us): ", modDown_extra_time * 1e6)
    print("     modDown_compute_time (us): ", modDown_compute_time * 1e6)
    print("     modDown_write_time (us): ", modDown_write_time * 1e6)
    print("     modDown_total_time (us): ", modDown_total_time * 1e6)
    print("     PtMatVec_one_stage_time (us): ", PtMatVec_one_stage_time * 1e6)
    
    stage_time = ct_prep_time + PtMatVec_one_stage_time
    HDFT_total_time += stage_time
    print("Stage ", stage+1, "time: (us)", stage_time * 1e6)
    print("Total_time: (us)", HDFT_total_time * 1e6)
    print("\n")

# ciphertext preparation
# decomp_transfer_ct_time = 2 * ct_Q_size / HBM_bw 
# decomp_time = decomp(L+1) / freq
# modup_transferin_time = (beta+1) * (L+1) * N * 8 / HBM_bw
# modup_time = (beta * modup(alpha, L+k+1) + modup(L+1, L+k+1)) / freq
# transferOut_ct_time = (beta+1) * (L+k+1) * N * 8 / HBM_bw
# ct_prep_time = decomp_transfer_ct_time + decomp_time + modup_transferin_time + modup_time + transferOut_ct_time
# ct_prep_allstage_time = ct_prep_time * fft_stage
# print("\nCiphertext preparation: ")
# print("     transferIn_size (MB): ", ct_Q_size / 1e6)
# print("     decomp_transfer_ct_time (us): ", decomp_transfer_ct_time * 1e6)
# print("     decomp_time (us): ", decomp_time * 1e6)
# print("     modup_transferin_time (us): ", modup_transferin_time * 1e6)
# print("     modup_time (us): ", modup_time * 1e6)
# print("     transferOut_size (MB): ", (beta+1) * (L+k+1) * N * 8 / 1e6)
# print("     transferOut_ct_time (us): ", transferOut_ct_time * 1e6)
# print("     ct_prepation_time (us): ", ct_prep_time * 1e6)
# print("     ct_prepation_allstage_time (us): ", ct_prep_allstage_time * 1e6)

# PtMatVec operation
# automorph_once_time = automorph(beta+1)     # automorph time: read beta + 1 limbs
# InnerProd_once_time = InnerProd(beta+1) / freq
# automorph_time = (L+k+1) * automorph_once_time
# InnerProd_time = (L+k+1) * InnerProd_once_time
# write_back_time = 2 * (L+k+1) * one_limb_size / HBM_bw
# modDown_read_time = 2 * (L+k+1) * one_limb_size / HBM_bw
# modDown_write_time = 2 * (L+1) * one_limb_size / HBM_bw
# modDown_once_time = moddown(L+k+1, L+1) / freq
# modDown_NTT_time = (NTT(k) + NTT(L+1)) / freq
# modDown_bc_time = basis_conv(k, L+1) / freq
# one_stage_time = automorph_time + InnerProd_time + modDown_once_time
# all_stage_time = fft_stage * one_stage_time
# print("\nPtMatVec operation: ")
# print("     automorph_once_time (us): ", automorph_once_time * 1e6)
# print("     InnerProd_once_time (us): ", InnerProd_once_time * 1e6)
# print("     automorph_time (us): ", automorph_time * 1e6)
# print("     InnerProd_time (us): ", InnerProd_time * 1e6)
# print("     write_back_time (us): ", write_back_time * 1e6)
# print("     modDown_read_time (us): ", modDown_read_time * 1e6)
# print("     modDown_write_time (us): ", modDown_write_time * 1e6)
# print("     modDown_once_time (us): ", modDown_once_time * 1e6)
# print("     modDown_NTT_time (us): ", modDown_NTT_time * 1e6)
# print("     modDown_bc_time (us): ", modDown_bc_time * 1e6)
# print("     one_stage_time (us): ", one_stage_time * 1e6)
# print("     all_stage_time (us): ", all_stage_time * 1e6)





# plaintext preparation: we ignore pre-compute time
# on-the-fly plaintext limb generation
# total_limbs = L+k+1
# pre_limbs = 1
# gen_limbs = total_limbs - pre_limbs
# transfer_pre_time = pre_limbs * one_limb_size / HBM_bw  # should coefficient size of limb be smaller than 8 byte
# if gen_limbs>0:
#     generation_cycles = basis_conv(pre_limbs, gen_limbs)
# else:
#     generation_cycles = 0
# generation_time = generation_cycles / freq
# NTT_time = NTT(total_limbs) / freq
# NTT_diag_time = NTT(diag_per_stage) / freq
# otf_total_time = generation_time + transfer_pre_time + NTT_time
# transfer_all_time = total_limbs * one_limb_size / HBM_bw
# print("\nPlaintext preparation: ")
# print("     pre_limb_size (MB): ", pre_limbs * one_limb_size / 1e6)
# print("     gen_limb_size (MB): ", gen_limbs * one_limb_size / 1e6)
# print("     gen_one_limb_time (us): ", generation_time / gen_limbs * 1e6)
# print("     generation_time (us): ", generation_time * 1e6)
# print("     NTT_one_limb_time (us): ", NTT_time / total_limbs * 1e6)
# print("     NTT_total_time (us): ", NTT_time * 1e6)
# print("     NTT_diag_time (us): ", NTT_diag_time * 1e6)
# print("     transfer_in_time (us): ", transfer_pre_time * 1e6)
# print("     otf_total_time (us): ", otf_total_time * 1e6)
# print("     transfer_out_time (us): ", transfer_all_time * 1e6)

# # plaintext preparation: we ignore pre-compute time
# # on-the-fly plaintext limb generation
# pre_limbs = diag_per_stage
# # gen_limbs = diag_per_stage
# transfer_pre_time = pre_limbs * one_limb_size / HBM_bw  # should coefficient size of limb be smaller than 8 byte
# transfer_total_time = (L+k+1) * transfer_pre_time
# # generation_cycles = basis_conv(1, 1)
# # generation_time = generation_cycles / freq
# # NTT_time = NTT(diag_per_stage) / freq
# # otf_total_time = generation_time + transfer_pre_time + NTT_time
# # transfer_all_time = total_limbs * one_limb_size / HBM_bw
# print("\nPlaintext preparation: ")
# print("     pre_limb_size (MB): ", pre_limbs * one_limb_size / 1e6)
# # print("     gen_limb_size (MB): ", gen_limbs * one_limb_size / 1e6)
# # print("     gen_one_limb_time (us): ", generation_time / gen_limbs * 1e6)
# # print("     generation_time (us): ", generation_time * 1e6)
# print("     NTT_one_limb_time (us): ", NTT(1) / freq * 1e6)
# # print("     NTT_time (us): ", NTT_time * 1e6)
# print("     transfer_pre_time (us): ", transfer_pre_time * 1e6)
# print("     transfer_total_time (us): ", transfer_total_time * 1e6)
# # print("     otf_total_time (us): ", otf_total_time * 1e6)
# # print("     transfer_out_time (us): ", transfer_all_time * 1e6)
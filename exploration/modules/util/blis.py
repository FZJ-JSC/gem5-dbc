"""

   BLIS
   An object-based framework for developing high-performance BLAS-like
   libraries.

   Copyright (C) 2019, Forschungszentrjum Juelich, Germany

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are
   met:
    - Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    - Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    - Neither the name(s) of the copyright holder(s) nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
   HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

from math import *
from modules.util import toBinaryInteger


def get_blis_parameters(conf_dict: dict, vl = 256, N_vfma = 2, L_vfma = 5, set_blocksize = False, dtype = "double"):

    S_data = 8 if dtype == "double" else 4
    N_vec  = int(vl/S_data/8)

    cache_line_size = conf_dict['caches']['cache_line_size']
    SLC_size = conf_dict['system']['num_slcs_per_core']*conf_dict['system']['num_cpus']*toBinaryInteger(conf_dict['caches']['SLC']['size'])

    W_L1 = conf_dict['caches']['L1D']['assoc']
    W_L2 = conf_dict['caches']['L2']['assoc']
    W_L3 = conf_dict['caches']['SLC']['assoc']

    C_L1 = cache_line_size
    C_L2 = cache_line_size
    C_L3 = cache_line_size

    N_L1 = int(toBinaryInteger(conf_dict['caches']['L1D']['size'])/W_L1/C_L1)
    N_L2 = int(toBinaryInteger(conf_dict['caches']['L2']['size'])/W_L2/C_L2)
    N_L3 = int(SLC_size/W_L3/C_L3)
    
    m_r = int(ceil(sqrt(N_vec*L_vfma*N_vfma)/N_vec)*N_vec)
    n_r = int(ceil((N_vec*L_vfma*N_vfma)/m_r))

    # Reuse: B_r
    # Keep in L1: 1xB_r micropanel, 2xAr 2xCr
    # evict A_r:
    # A_r size: k_c*m_r
    # k_c*m_r*S_data = C_Ar * N_L1*C_L1
    # C_Ar = floor((W_L1-1.0)/(1.0+n_r/m_r)) (see paper)
    k_c = int(floor((floor((W_L1-1.0)/(1.0+n_r/m_r)) * N_L1*C_L1)/(n_r*S_data)))

    # Reuse: A_C
    # Keep in L2: 1x A_C, 2x m_c/m_r Cr microtiles, 2x B_r micropanel
    # Evict B_r microtiles
    # size: k_c*n_r
    # size of A_C: k_c*m_c
    # 
    # 1 CL for C_r, calc how many for B_r, rest for A_C
    C_Ac = W_L2 - 1 - int(ceil((2*k_c*n_r*S_data)/(C_L2*N_L2)))
    m_c = int(floor(C_Ac *(N_L2*C_L2)/(k_c*S_data)))
    m_c -= (m_c % m_r) 
    # Reuse: B_C
    # Keep in L3: 1x B_C, 2x m_c/m_r Cr microtiles, 2x A_C 
    # Evict A_C
    # size B_C: k_c*n_c
    #
    # 1 CL for C_r, calc how many for A_C, rest for B_C
    C_Bc = W_L3-1 - ceil((2*k_c*m_c*S_data)/(C_L3*N_L3))
    n_c = int(floor(C_Bc*(N_L3*C_L3)/(k_c*S_data)))
    n_c -= (n_c % n_r)
    
    blis_parameters = dict(
        BLIS_SVE_N_VFMA = N_vfma,
        BLIS_SVE_L_VFMA = L_vfma,
        BLIS_SVE_W_L1 = W_L1,
        BLIS_SVE_N_L1 = N_L1,
        BLIS_SVE_C_L1 = C_L1,
        BLIS_SVE_W_L2 = W_L2,
        BLIS_SVE_N_L2 = N_L2,
        BLIS_SVE_C_L2 = C_L2,
        BLIS_SVE_W_L3 = W_L3,
        BLIS_SVE_N_L3 = N_L3,
        BLIS_SVE_C_L3 = C_L3,
        _BLIS_SVE_MR = m_r,
        _BLIS_SVE_NR = n_r,
    )

    if set_blocksize:
        suffix = "_D"
        blis_parameters[f"BLIS_SVE_KC{suffix}"] = k_c
        blis_parameters[f"BLIS_SVE_MC{suffix}"] = m_c
        blis_parameters[f"BLIS_SVE_NC{suffix}"] = n_c

    return blis_parameters

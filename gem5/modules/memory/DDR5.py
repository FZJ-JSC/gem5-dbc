# Copyright (c) 2012-2019 ARM Limited
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Copyright (c) 2013 Amin Farmahini-Farahani
# Copyright (c) 2015 University of Kaiserslautern
# Copyright (c) 2015 The University of Bologna
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Andreas Hansson
#          Ani Udipi
#          Omar Naji
#          Matthias Jung
#          Erfan Azarkhish
#          Nam Ho
#          Francesco Sgherzi

import m5

# A single DDR5-4800 x64 channel, with timings based on the DDR5-4800 datasheet (MT60B1G16HC-48B) from MICRON
# DOC: https://media-www.micron.com/-/media/client/global/documents/products/data-sheet/dram/ddr5/ddr5_sdram_core.pdf?rev=3210029bd0f44952852e9f7134d83315
# 16 devices/rank * 2 ranks/channel * 512MB/device = 16GB/channel
class DDR5_4800_1x16(m5.objects.DRAMInterface):
    device_size = '1GiB'

    device_bus_width = 16 

    # page 27 
    # DDR5 is a BL16 device (page 34)
    burst_length = 16

    device_rowbuffer_size = '2KiB'

    # 16x4 configuration, so 16 devices
    devices_per_rank = 1

    # page 1, "4 groups in 4 banks each"
    bank_groups_per_rank = 4 

    # 64bit per rank (non ecc) / x4 banks/bit = 16 banks/rank  
    banks_per_rank = 16

    # Let's use dual rank
    ranks_per_channel = 2 

    # override the default buffer sizes and go for something larger to
    # accommodate the larger bank count
    # copied from DDR4
    write_buffer_size = 128
    read_buffer_size = 64

    # 4800 MT/s -> f0 = 2400 
    # page 343
    tCK = '0.416ns'

    # tCCD_S is 8CK
    # 8 beats per burst  -> 4tCK
    # 16 beats per burst -> 8tCK 
    # page 471
    tBURST = '1.664ns'

    # max(8CK, 5ns)
    # page 471
    tCCD_L = '5ns'

    # tRRD_S = 8 CK
    # page 471
    tRRD = '3.3ns'

    # tRRD_L = max(8CL, 5ns)
    tRRD_L = '5ns'

    # DDR5-4800 34-34-34
    # page 386
    tRCD = '14.166ns'
    
    tRP = '14.166ns'
    tRAS = '32ns'
    
    # 26CK @3200, no doc on @4800
    # page 34
    tCL = '10.833ns' 

    # page 34, write recovery
    # 48CK @3200, no doc on 4800
    tWR = '20ns'

    # Using tFAW = max(32CK, 20000ns)
    tXAW = '13.333ns'
    # FAW stands for Four Activation Window
    activation_limit = 4 

    # page 176 -> for 32GB device
    tRFC = '410ns'

    # WTR stands for Write To Read timings
    # page 164 and 481
    # WBL stands for Write Burst Length
    # FORMULA:   CWL   + WBL / 2 + max(16CK, 10ns) 
    #         (CL - 2) +    8    + 10ns
    tWTR = '28ns'

    # tRTP = 12ck
    # page 34, 12CK @3200, no doc at 4800
    tRTP = '5ns'
    
    #                2
    # formula is (CL - CWL) + RBL / 2 + 2tCL - Read DWS offset + tRPST - 0.5 tCL + tWPRE
    # for different ranks, for same rank is 2CLK
    # formula is (4.5CK) + 8 + 1.5CK + 2CK
    tRTW = '3.333ns'
    tCS = '3.333ns'

    # average full refresh time at T = [0, 85C]
    # page 176
    tREFI = '3.9us'

    # Page 485
    # max(7.5ns, 8CK)
    tXP = '7.5ns'

    # page 183: 'Minimum value of tXS is tRFC'
    tXS = '410ns'

    # Voltage value from datasheet
    # Current values might be gathered from the intel thing, 
    # but gem5 does not power model memories, afaik
    VDD = '1.1V'
    # From https://edc.intel.com/content/www/us/en/design/ipla/software-development-platforms/client/platforms/alder-lake-desktop/12th-generation-intel-core-processors-datasheet-volume-1-of-2/006/vdd2-dc-specifications/
    VDD2 = '1.116V' 


# Taken from `develop` branch
# DDR5-4800 channel
# timing parameters are extracted from MT60B2G8, and DDR5 SDRAM product core data sheet
# 4 devices/rank x 2 ranks/channel x 2GB/device = 16GB/channel

# NOTE: 
# Constraint setting: burst_length * (device_bus_width/8) * devices_per_rank = cache line size
class DDR5_4800_8x8(DDR5_4800_1x16):
    device_size           = '2GB'
        
    # 8x8 configuration, 8 devices each with an 8-bit interface
    device_bus_width = 8
    # DDR5 is a BL16/BL32 device
    burst_length = 16
    # Each device has a page (row buffer) size of 1 Kbyte (1K columns x8)
    device_rowbuffer_size = '1kB'
    # 8x8 configuration, so 8 devices
    devices_per_rank = 4

    ranks_per_channel = 2
    bank_groups_per_rank  = 8
    banks_per_rank        = 32

    
    # 2400 MHz
    tCK    = '0.416ns'
    # 16 beats need 8 x tCK of @2400MHz 
    # tBURST = '1.664ns'
    tBURST = '1.00242367ns' # Allows you to go up to 64GB/s
    tCCD_L = '3.75ns'    
    tRCD   = '16ns'
    tCL    = '16.64ns'
    tRP    = '16ns'
    tRAS   = '32ns'
    tRRD   = '3.328ns'
    tRRD_L = '5ns'
    tXAW   = '13.333ns'
    # TODO
    activation_limit = 4
    tRFC   = '195ns'
    tWR    = '30ns'
    
    # TODO: reuse DDR4
    tWTR = '5ns'
    
    # Greater of 4 CK or 7.5 ns
    tRTP = '7.5ns'
    
    tRTW   = '0.832ns'
    tCS    = '0.832ns'
    tREFI  = '3.9us'
    tXP    = '7.5ns'
    tXS    = '205ns'


class DDR5(DDR5_4800_8x8):
    def __init__(self, options, **kwargs):
        super(DDR5, self).__init__(**kwargs)


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
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
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

from modules import util

import m5

# A single HBM x128 interface (one command and address bus), with
# default timings based on data publically released
# ("HBM: Memory Solution for High Performance Processors", MemCon, 2014),
# IDD measurement values, and by extrapolating data from other classes.
# Architecture values based on published HBM spec
# A 4H stack is defined, 2Gb per die for a total of 1GB of memory.
class HBM_1000_4H_1x128(m5.objects.DRAMInterface):
    # HBM gen1 supports up to 8 128-bit physical channels
    # Configuration defines a single channel, with the capacity
    # set to (full_ stack_capacity / 8) based on 2Gb dies
    # To use all 8 channels, set 'channels' parameter to 8 in
    # system configuration

    # 128-bit interface legacy mode
    device_bus_width = 128

    # HBM supports BL4 and BL2 (legacy mode only)
    burst_length = 4

    # size of channel in bytes, 4H stack of 2Gb dies is 1GB per stack;
    # with 8 channels, 128MB per channel
    device_size = '128MB'

    device_rowbuffer_size = '2kB'

    # 1x128 configuration
    devices_per_rank = 1

    # HBM does not have a CS pin; set rank to 1
    ranks_per_channel = 1

    # HBM has 8 or 16 banks depending on capacity
    # 2Gb dies have 8 banks
    banks_per_rank = 8

    # depending on frequency, bank groups may be required
    # will always have 4 bank groups when enabled
    # current specifications do not define the minimum frequency for
    # bank group architecture
    # setting bank_groups_per_rank to 0 to disable until range is defined
    bank_groups_per_rank = 0

    # 500 MHz for 1Gbps DDR data rate
    tCK = '2ns'

    # use values from IDD measurement in JEDEC spec
    # use tRP value for tRCD and tCL similar to other classes
    tRP = '15ns'
    tRCD = '15ns'
    tCL = '15ns'
    tRAS = '33ns'

    # BL2 and BL4 supported, default to BL4
    # DDR @ 500 MHz means 4 * 2ns / 2 = 4ns
    tBURST = '4ns'

    # value for 2Gb device from JEDEC spec
    tRFC = '160ns'

    # value for 2Gb device from JEDEC spec
    tREFI = '3.9us'

    # extrapolate the following from LPDDR configs, using ns values
    # to minimize burst length, prefetch differences
    tWR = '18ns'
    tRTP = '7.5ns'
    tWTR = '10ns'

    # start with 2 cycles turnaround, similar to other memory classes
    # could be more with variations across the stack
    tRTW = '4ns'

    # single rank device, set to 0
    tCS = '0ns'

    # from MemCon example, tRRD is 4ns with 2ns tCK
    tRRD = '4ns'

    # from MemCon example, tFAW is 30ns with 2ns tCK
    tXAW = '30ns'
    activation_limit = 4

    # 4tCK
    tXP = '8ns'

    # start with tRFC + tXP -> 160ns + 8ns = 168ns
    tXS = '168ns'


class HBM(HBM_1000_4H_1x128):
    def __init__(self, options, **kwargs):
        super(HBM, self).__init__(**kwargs)
        

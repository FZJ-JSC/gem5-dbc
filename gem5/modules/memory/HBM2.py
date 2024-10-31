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


# Note: Following parameters taken from the
# gem5-X open source framework. See:
# https://github.com/esl-epfl/gem5-X/blob/2dbcef7ea088f0c4015928044e3346a62ccef5c9/src/mem/DRAMCtrl.py

# A single HBM2 x128 interface (one command and address bus), with
# default timings based on data publically released
# ("HBM: Memory Solution for High Performance Processors", MemCon, 2014),
# IDD measurement values, and by extrapolating data from other classes.
# Architecture values based on published HBM spec
# A 4H stack is defined, 2Gb per die for a total of 1GB of memory.
class HBM2_2000_4H_1x128(m5.objects.DRAMInterface):
    # HBM gen2 supports up to 8 128-bit physical channels
    # Configuration defines a single channel, with the capacity
    # set to (full_ stack_capacity / 8) based on 2Gb dies
    # To use all 8 channels, set 'channels' parameter to 8 in
    # system configuration

    # 128-bit interface legacy mode
    device_bus_width = 128

    write_buffer_size = 128
    read_buffer_size = 128

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
    banks_per_rank = 16

    # depending on frequency, bank groups may be required
    # will always have 4 bank groups when enabled
    # current specifications do not define the minimum frequency for
    # bank group architecture
    # setting bank_groups_per_rank to 0 to disable until range is defined
    bank_groups_per_rank = 4

    # 1.2GHz for 2.4Gbps DDR data rate
    tCK = '0.833ns'

    # use values from IDD measurement in JEDEC spec
    # use tRP value for tRCD and tCL similar to other classes
    tRP = '14ns'
    tRCD = '14ns'
    tCL = '14ns'
    tRAS = '33ns'

    # BL2 and BL4 supported, default to BL4
    # DDR @ 500 MHz means 4 * 2ns / 2 = 4ns
    tBURST = '1.666ns'
    tCCD_L = '3.332ns'
    tCCD_L_WR = '3.332ns'

    # value for 2Gb device from JEDEC spec
    tRFC = '160ns'

    # value for 2Gb device from JEDEC spec
    tREFI = '3.9us'

    # extrapolate the following from LPDDR configs, using ns values
    # to minimize burst length, prefetch differences
    tWR = '8ns'
    tRTP = '3.5ns'
    tWTR = '3ns'

    # start with 2 cycles turnaround, similar to other memory classes
    # could be more with variations across the stack
    tRTW = '1.666ns'

    # single rank device, set to 0
    tCS = '0ns'

    # from MemCon example, tRRD is 4ns with 2ns tCK
    tRRD = '1.666ns'
    tRRD_L = '1.666ns'

    # from MemCon example, tFAW is 30ns with 2ns tCK
    tXAW = '12.5ns'
    activation_limit = 4

    # 4tCK
    tXP = '3.332ns'

    # start with tRFC + tXP -> 160ns + 8ns = 168ns
    tXS = '160ns'

class HBM2(HBM2_2000_4H_1x128):
    def __init__(self, options, **kwargs):
        super(HBM2, self).__init__(**kwargs)

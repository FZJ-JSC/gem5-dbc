# Copyright (c) 2020 ARM Limited
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

# [lnghrdntcr]: Taken from gem5@epi juelich repo, commit 21dec619a88459b80df34c563b33216167d93a49
import m5

# NVM delays and device architecture defined to mimic PCM like memory.
# Can be configured with DDR4_2400 sharing the channel
class NVM_2400_1x64(m5.objects.NVMInterface):
    write_buffer_size = 128
    read_buffer_size = 64

    max_pending_writes = 128
    max_pending_reads = 64

    device_rowbuffer_size = '256B'

    # 8X capacity compared to DDR4 x4 DIMM with 8Gb devices
    device_size = '512GiB'
    # Mimic 64-bit media agnostic DIMM interface
    device_bus_width = 64
    devices_per_rank = 1
    ranks_per_channel = 1
    banks_per_rank = 16

    burst_length = 8

    two_cycle_rdwr = True

    # 1200 MHz
    tCK = '0.833ns'

    tREAD = '150ns'
    tWRITE = '500ns';
    tSEND = '14.16ns';
    tBURST = '3.332ns';

    # Default all bus turnaround and rank bus delay to 2 cycles
    # With DDR data bus, clock = 1200 MHz = 1.666 ns
    tWTR = '1.666ns';
    tRTW = '1.666ns';
    tCS = '1.666ns'

class NVM(NVM_2400_1x64): 
    def __init__(self, options, **kwargs):
        super(NVM, self).__init__(**kwargs)

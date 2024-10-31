# Copyright (c) 2013, 2017 ARM Limited
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
#
# Authors: Andreas Sandberg
#          Andreas Hansson

import sys
from math import log, ceil

import m5

from modules.memory import HBM, HBM2, DDR4, Simple

# [lnghrdntcr] Imported DDR5 and HBM3
from modules.memory import DDR5


def create_memory_interface(r, i, nbr_mem_ctrls, options):
    # This function shouldn't be called.
    assert False

    if(options.architecture.memory.model == 'HBM'):
        memory_cls = HBM
    if(options.architecture.memory.model == 'HBM2'):
        memory_cls = HBM2
    if(options.architecture.memory.model == 'DDR4'):
        memory_cls = DDR4
    if(options.architecture.memory.model == 'Simple'):
        memory_cls = Simple
    # [lnghrdntcr] Added DDR5
    if(options.architecture.memory.model == 'DDR5'):
        memory_cls = DDR5 


    if options.elastic_trace and not issubclass(memory_cls, m5.objects.SimpleMemory):
        print("When elastic trace is enabled, configure mem-type as simple-mem.")
        sys.exit(1)
    
    cache_line_size = options.architecture.caches.cache_line_size
    mem_channels_intlv = 0 #options.architecture.memory.channels_intlv
    
    if (options.architecture.NOC.active):
        #num_dirs = options.architecture.NOC.controllers
        intlv_bits = int(log(nbr_mem_ctrls, 2))
        if options.architecture.NOC.numa_high_bit:
            dir_bits = int(log(nbr_mem_ctrls, 2))
            intlv_size = 2 ** (options.architecture.NOC.numa_high_bit - dir_bits + 1)
        else:
            # if the numa_bit is not specified, set the directory bits as the
            # lowest bits above the block offset bits
            intlv_size = cache_line_size


        #mem_channels    = options.architecture.mem_channels
        #cache_line_size = options.architecture.cache_line_size
        #intlv_size = max(128, cache_line_size.value)
        #intlv_low_bit = int(log(intlv_size, 2))
        #intlv_bits = int(log(mem_channels, 2))
    else:
        #mem_channels    = 
        intlv_bits = int(log(nbr_mem_ctrls, 2))
        intlv_size = max(mem_channels_intlv, cache_line_size)
        if 2 ** intlv_bits != nbr_mem_ctrls:
            print("Number of memory channels must be a power of 2")
            sys.exit(1)
    
    intlv_low_bit = int(log(intlv_size, 2))

    # Use basic hashing for the channel selection, and preferably use the lower tag bits from the last level cache.
    # As we do not know the details of the caches here, make an educated guess. 
    # 4 MByte 4-way associative with 64 byte cache lines is 6 offset bits and 14 index bits.
    #xor_low_bit = 20
    xor_high_bit = 0
    if(options.architecture.NOC.active):
        xor_high_bit = options.architecture.NOC.xor_low_bit + intlv_bits - 1
                
    # Create an instance so we can figure out the address mapping and row-buffer size
    dram_iface = memory_cls(options)
                
    # Only do this for DRAMs
    if issubclass(memory_cls, m5.objects.DRAMInterface):
        # Inform each controller how many channels to account for
        #if(options.forth):
        #    mem_ctrl.channels = nbr_mem_ctrls
        # If the channel bits are appearing after the column bits, we need to add the appropriate number of bits for the row buffer size
        if dram_iface.addr_mapping.value == 'RoRaBaChCo':
            # This computation only really needs to happen once, but as we rely on having an instance we end up having to repeat it for each and every one
            rowbuffer_size = dram_iface.device_rowbuffer_size.value * dram_iface.devices_per_rank.value
            intlv_low_bit = int(log(rowbuffer_size, 2))
                
    # We got all we need to configure the appropriate address range
    dram_iface.range = m5.objects.AddrRange(r.start, size = r.size(),
                                      intlvHighBit = intlv_low_bit + intlv_bits - 1,
                                      xorHighBit = xor_high_bit,
                                      intlvBits = intlv_bits,
                                      intlvMatch = i)

    if(options.architecture.NOC.active):
        if options.architecture.NOC.access_backing_store:
            dram_iface.kvm_map=False
    else:
        # Set the number of ranks based on the command-line options if it was explicitly set
        #if issubclass(memory_cls, m5.objects.DRAMInterface) and options.architecture.memory.ranks:
        #    dram_iface.ranks_per_channel = options.architecture.memory.ranks
        if options.elastic_trace:
            dram_iface.latency = '1ns'
            print("For elastic trace, over-riding Simple Memory latency to 1ns.")
    
    # Enable low-power DRAM states if option is set
    if issubclass(memory_cls, m5.objects.DRAMInterface):
        dram_iface.enable_dram_powerdown = options.architecture.memory.enable_dram_powerdown
       

    return dram_iface

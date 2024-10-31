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

import m5
import math

from modules.memory import HBM, HBM2, DDR4, Simple
# [lnghrdntcr] Imported DDR5, HBM3 
from modules.memory import DDR5, HBM3
# [lnghrdntcr] Imported NVMInterface
from modules.memory import NVM

def create_memory_interface(options, model, range, index, intlv_size, intlv_bits, mem_options=None, hetero_mem_id=0, just_range=False):

    access_backing_store = options.architecture.NOC.access_backing_store
    xor_low_bit          = options.architecture.NOC.xor_low_bit

    memory_cls = dict(
        HBM  = HBM,
        HBM2 = HBM2,
        HBM3 = HBM3,
        DDR4 = DDR4,
        DDR5 = DDR5,
        NVM  = NVM,
        Simple = Simple
    ).get(model, DDR5)

    # Use basic hashing for the channel selection, and preferably use
    # the lower tag bits from the last level cache. As we do not know
    # the details of the caches here, make an educated guess. 4 MByte
    # 4-way associative with 64 byte cache lines is 6 offset bits and
    # 14 index bits.
    if (xor_low_bit):
        xor_high_bit = xor_low_bit + intlv_bits - 1
    else:
        xor_high_bit = 0

    # Create an instance so we can figure out the address
    # mapping and row-buffer size
    # interface = memory_cls(options)

    if mem_options is not None and mem_options.get("addr_mapping") is not None: 
        assert mem_options.get("page_policy") is not None
        page_policy  = mem_options["page_policy"]
        addr_mapping = mem_options["addr_mapping"] 

        if isinstance(page_policy, list): 
            # HeteroMemCtrl
            page_policy  = page_policy[hetero_mem_id]
            addr_mapping = addr_mapping[hetero_mem_id]


        interface = memory_cls(options, addr_mapping=addr_mapping, page_policy=page_policy)
    elif not just_range: 
        interface = memory_cls(options)

    # Set default intlv_low_bit value
    intlv_low_bit = int(math.log(intlv_size, 2))
    if just_range: 
        return m5.objects.AddrRange(
            range.start,
            size = range.size(),
            intlvHighBit = intlv_low_bit + intlv_bits - 1,
            xorHighBit   = xor_high_bit,
            intlvBits    = intlv_bits,
            intlvMatch   = index
        )

    # Only do this for DRAMs
    if issubclass(memory_cls, m5.objects.DRAMInterface):
        # If the channel bits are appearing after the column
        # bits, we need to add the appropriate number of bits
        # for the row buffer size
        if interface.addr_mapping.value == 'RoRaBaChCo':
            # This computation only really needs to happen
            # once, but as we rely on having an instance we
            # end up having to repeat it for each and every
            # one
            rowbuffer_size = interface.device_rowbuffer_size.value * interface.devices_per_rank.value

            intlv_low_bit = int(math.log(rowbuffer_size, 2))

        if interface.addr_mapping.value == 'RoCoRaBaCh': 
            intlv_low_bit = int(math.log(intlv_size, 2))

    # Also adjust interleaving bits for NVM attached as memory
    # Will have separate range defined with unique interleaving
    if issubclass(memory_cls, m5.objects.NVMInterface):
        # If the channel bits are appearing after the low order
        # address bits (buffer bits), we need to add the appropriate
        # number of bits for the buffer size
        if interface.addr_mapping.value == 'RoRaBaChCo':
            # This computation only really needs to happen
            # once, but as we rely on having an instance we
            # end up having to repeat it for each and every
            # one
            buffer_size = interface.per_bank_buffer_size.value

            intlv_low_bit = int(math.log(buffer_size, 2))

    # We got all we need to configure the appropriate address
    # range
    interface.range = m5.objects.AddrRange(
        range.start,
        size = range.size(),
        intlvHighBit = intlv_low_bit + intlv_bits - 1,
        xorHighBit   = xor_high_bit,
        intlvBits    = intlv_bits,
        intlvMatch   = index
        )
        
    print("AddrRange options: ")
    print("Start: ", range.start)
    print("Size: ", range.size())
    print("intlvHighBit: ", intlv_low_bit + intlv_bits - 1)
    print("xorHighBit: ", xor_high_bit)
    print("intlvBits: ", intlv_bits)
    print("intlvMatch: ", index)

    if access_backing_store:
        interface.kvm_map=False

    return interface


def configure_mem_region_controller(options, system, dir_cntrls: list): 

    """
    Configure Directory and Memory controllers for a single memory region
    """
    print("Name of dir_cntrls: ", type(dir_cntrls[0][1]).__name__)

    cache_line_size = options.architecture.caches.cache_line_size

    mem_ctrls = []
    # Loop over regions
    for region_id, mem_region in enumerate(options.architecture.memory.regions):
        # Collect all controllers corresponding to mem region
        region_ctrls   = [cntrl for (r_id, cntrl) in dir_cntrls if r_id == region_id]
        num_dir_cntrls = len(region_ctrls)
        mem_range      = system.mem_ranges[region_id]
        mem_options    = options.parameters["memory"][region_id]

        # if the numa_bit is not specified, set the directory bits as the
        # lowest bits above the block offset bits
        intlv_size = cache_line_size
        intlv_bits = int(math.log(num_dir_cntrls, 2))

        intlv_low_bit = int(math.log(intlv_size, 2))
        intlv_high_bit = intlv_low_bit + intlv_bits - 1
        xor_high_bit = options.architecture.NOC.xor_low_bit + intlv_bits - 1

        for index, dir_cntrl in enumerate(region_ctrls):

            # [lnghrdntcr] Heterogeneous memory controller
            if mem_region.model == "HMEM": 
                interfaces = []
                start = mem_range.start.value
                size = mem_range.size()
                for kind_id, m_model in enumerate(mem_region.kind): 
                    # FIXME: Do not assume that the two interfaces are of the same size!!!
                    m_addr_range = m5.objects.AddrRange(start, size=int(size / 2))
                    interfaces.append(
                        create_memory_interface(
                            options, 
                            m_model, 
                            m_addr_range, 
                            index, 
                            intlv_size, 
                            intlv_bits,
                            mem_options=mem_options,
                            hetero_mem_id=kind_id
                        )
                    )
                    start = m_addr_range.start + int(size/2)

                
                mem_ctrl = m5.objects.HeteroMemCtrl(dram = interfaces[0], second_interface=interfaces[1])

            else: 
                m_range = mem_range
                m_model = mem_region.model
                interface = create_memory_interface(
                    options,
                    m_model,
                    m_range,
                    index,
                    intlv_size,
                    intlv_bits,
                    mem_options=mem_options,
                    just_range = (mem_region.model == "BwLatCtrl") or (mem_region.model == "Ramulator2")
                )

                if mem_region.model == "BwLatCtrl": 
                    ctrl_config = mem_region.ctrl_config
                    mem_ctrl = m5.objects.BwLatCtrl(range=interface, curves_path = ctrl_config["curves_path"], sampling_window = ctrl_config["sampling_window"])
                elif mem_region.model == "Ramulator2":
                    mem_ctrl = m5.objects.Ramulator2(range=interface)
                    mem_ctrl.config_path = mem_region.config_file
                else: 
                    mem_ctrl = m5.objects.MemCtrl(dram = interface) if (mem_region.model != 'Simple') else interface

            # Enable low-power DRAM states if option is set
            if mem_region.model != 'Simple' and mem_region.model != "NVM" and mem_region.model != "BwLatCtrl" and mem_region.model != "Ramulator2":
                mem_ctrl.dram.enable_dram_powerdown = mem_region.enable_dram_powerdown

            mem_ctrl.port = dir_cntrl.memory_out_port

            if mem_region.model == "BwLatCtrl" or mem_region.model == "Ramulator2": 
                dir_cntrl.addr_ranges = [interface]
            elif mem_region.model == "HMEM": 
                dir_cntrl.addr_ranges = [i.range for i in interfaces]
            else: 
                dir_cntrl.addr_ranges = [interface.range]

            mem_ctrls.append(mem_ctrl)

    return mem_ctrls

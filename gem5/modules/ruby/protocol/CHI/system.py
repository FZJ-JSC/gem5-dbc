# Copyright (c) 2021 ARM Limited
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

import m5

from modules.options import Options

from modules.ruby.protocol.CHI import nodes


def create_RNF_nodes(options: Options, system, router_numa_ids: list = []):
    """
    Creates one RNF node per cpu with priv l2 caches
    """
    assert(len(system.cpu) == options.architecture.num_cpus)
    node_class = "RNF"

    ruby_system = system.ruby
    num_nodes_per_router = options.architecture.NOC.protocol.nodes[node_class].nodes_per_router
    router_idx_list      = options.architecture.NOC.protocol.nodes[node_class].router_list
    router_idx = lambda idx: idx // num_nodes_per_router
    num_ctrls  = len(system.cpu)

    sorted_numa_ids = sorted(set(router_numa_ids))

    sorted_router_list = []
    for numa_id in sorted_numa_ids:
        router_list = [router_id for router_id in router_idx_list if numa_id == router_numa_ids[router_id]]
        sorted_router_list.extend(sorted(router_list))

    ctrl_list = []
    ctrl_ids = [i for i in range(num_ctrls)]
    for numa_id in sorted_numa_ids:
        ctrl_router_list = [(ctrl_id,sorted_router_list[router_idx(ctrl_id)]) for ctrl_id in ctrl_ids if numa_id == router_numa_ids[sorted_router_list[router_idx(ctrl_id)]]]
        for ctrl_id, router_id in ctrl_router_list:
            numa_id   = router_numa_ids[router_id]
            ctrl = nodes.CHI_RNF(options, [system.cpu[ctrl_id]], ruby_system, router_id=router_id, numa_id=numa_id)
            print(f"  {node_class} ctrl_id={ctrl_id} router_id={router_id} numa_id={numa_id}")
            if options.architecture.caches.L2.active:
                ctrl.addPrivL2Cache(options)
            ctrl_list.append(ctrl)
    return ctrl_list


def create_HNF_nodes(options: Options, system, router_numa_ids: list = [], mem_numa_ids: list = [], other_memories: list = []):
    """
    Creates Address ranges for each defined memory range
    Creates corresponding HNF nodes
    """
    node_class = "HNF"

    if not options.architecture.caches.SLC.active:
        return []

    ruby_system = system.ruby
    num_nodes_per_router = options.architecture.NOC.protocol.nodes[node_class].nodes_per_router
    router_idx_list      = options.architecture.NOC.protocol.nodes[node_class].router_list
    router_idx = lambda idx: idx // num_nodes_per_router
    num_ctrls  = num_nodes_per_router * len(router_idx_list)

    sorted_numa_ids = sorted(set(router_numa_ids))

    ctrl_list = []
    ctrl_ids = [i for i in range(num_ctrls)]
    for numa_id in sorted_numa_ids:
        ctrl_router_list = [(ctrl_id,router_idx_list[router_idx(ctrl_id)]) for ctrl_id in ctrl_ids if numa_id == router_numa_ids[router_idx_list[router_idx(ctrl_id)]]]
        mem_region_list = [region_id for region_id in range(len(mem_numa_ids)) if numa_id == mem_numa_ids[region_id]]
        for region_id in mem_region_list:
            ctrl_router_list   = [(ctrl_id,router_idx_list[router_idx(ctrl_id)]) for ctrl_id in ctrl_ids if numa_id == router_numa_ids[router_idx_list[router_idx(ctrl_id)]]]
            # HNF range
            hnf_list   = [ctrl_id for ctrl_id,router_id in ctrl_router_list]
            hnf_ranges = [system.mem_ranges[region_id]]
            #+ other_memories if numa_id == 0 else mem_ranges
            if numa_id == 0:
                for m in other_memories:
                    hnf_ranges.append(m.range)
            # Create range for region
            nodes.CHI_HNF.createAddrRanges(options, hnf_ranges, hnf_list, numa_id=numa_id)
            # Create controllers for region
            for ctrl_id,router_id in ctrl_router_list:
                ctrl = nodes.CHI_HNF(options, ctrl_id, ruby_system, router_id = router_id, numa_id=numa_id) 
                ctrl_list.append(ctrl)
    return ctrl_list


def create_SNF_nodes(options: Options, system, router_numa_ids: list = []):
    """
    Create SNF Nodes
    """
    node_class = "SNF_Mem"

    ruby_system = system.ruby

    ctrl_list = []
    mem_range_numa_ids = []
    for region_id, mem_region in enumerate(options.architecture.memory.regions):

        router_idx_list = options.architecture.NOC.protocol.nodes[node_class].router_list[region_id]
        router_idx = lambda idx: idx  % len(router_idx_list)

        assert(len(router_idx_list) > 0)

        region_numa_id = router_numa_ids[router_idx_list[0]]
        mem_range_numa_ids.append(region_numa_id)

        num_channels = mem_region.channels
        for ctrl_id in range(num_channels):
            router_id = router_idx_list[router_idx(ctrl_id)]
            assert(region_numa_id == router_numa_ids[router_id])
            ctrl = nodes.CHI_SNF_MainMem(options, ruby_system, router_id = router_id, numa_id=region_numa_id, region_id=region_id)
            ctrl_list.append(ctrl)

    system.mem_range_numa_ids = mem_range_numa_ids

    return ctrl_list


def find_other_memories(system, bootmem = None):
    # Look for other memories
    other_memories = []
    if bootmem:
        other_memories.append(bootmem)
    if getattr(system, 'sram', None):
        other_memories.append(getattr(system, 'sram', None))
    on_chip_mem_ports = getattr(system, '_on_chip_mem_ports', None)
    if on_chip_mem_ports:
        other_memories.extend([p.simobj for p in on_chip_mem_ports])

    return other_memories


def create_system(options: Options, system, dma_ports = None, bootmem = None, router_numa_ids: list = [], mem_numa_ids: list = []):
    if m5.defines.buildEnv['PROTOCOL'] != 'CHI':
        m5.panic("This script requires the CHI build")

    ruby_system = system.ruby
    full_system = options.simulation.fs_mode

    # other functions use system.cache_line_size assuming it has been set
    assert(system.cache_line_size.value == options.architecture.caches.cache_line_size)

    cpu_sequencers = []
    mem_cntrls = []
    mem_dests = []
    network_nodes = []
    network_cntrls = []
    hnf_dests = []
    all_cntrls = []

    other_memories = find_other_memories(system, bootmem)

    # Create RNF nodes
    ruby_system.rnf = create_RNF_nodes(
        options,
        system,
        router_numa_ids = router_numa_ids
    )
    for rnf in ruby_system.rnf:
        cpu_sequencers.extend(rnf.getSequencers())
        network_nodes.append(rnf)
        network_cntrls.extend(rnf.getNetworkSideControllers())
        all_cntrls.extend(rnf.getAllControllers())

    # Create HNF nodes
    ruby_system.hnf = create_HNF_nodes(
        options,
        system,
        router_numa_ids=router_numa_ids,
        mem_numa_ids=mem_numa_ids,
        other_memories=other_memories
    )
    for hnf in ruby_system.hnf:
        assert(hnf.getAllControllers() == hnf.getNetworkSideControllers())
        hnf_dests.extend(hnf.getAllControllers())
        network_nodes.append(hnf)
        network_cntrls.extend(hnf.getNetworkSideControllers())
        all_cntrls.extend(hnf.getAllControllers())

    # Create the memory controllers
    # Notice we don't define a Directory_Controller type so we don't use
    # create_directories shared by other protocols.
    ruby_system.snf = create_SNF_nodes(
        options,
        system,
        router_numa_ids=router_numa_ids
    )
    for snf in ruby_system.snf:
        assert(snf.getAllControllers() == snf.getNetworkSideControllers())
        network_nodes.append(snf)
        network_cntrls.extend(snf.getNetworkSideControllers())
        mem_cntrls.extend(snf.getAllRegionIdControllers())
        all_cntrls.extend(snf.getAllControllers())
        mem_dests.extend(snf.getAllControllers())

    if len(other_memories) > 0:
        ruby_system.rom_snf = [ nodes.CHI_SNF_BootMem(options, ruby_system, None, m) for m in other_memories ]
        for snf in ruby_system.rom_snf:
            network_nodes.append(snf)
            network_cntrls.extend(snf.getNetworkSideControllers())
            all_cntrls.extend(snf.getAllControllers())
            mem_dests.extend(snf.getAllControllers())

    # Creates the controller for dma ports and io
    if len(dma_ports) > 0:
        ruby_system.dma_rni = [ nodes.CHI_RNI_DMA(options, ruby_system, dma_port, None) for dma_port in dma_ports ]
        for rni in ruby_system.dma_rni:
            network_nodes.append(rni)
            network_cntrls.extend(rni.getNetworkSideControllers())
            all_cntrls.extend(rni.getAllControllers())

    if full_system:
        ruby_system.io_rni = nodes.CHI_RNI_IO(options, ruby_system, None)
        network_nodes.append(ruby_system.io_rni)
        network_cntrls.extend(ruby_system.io_rni.getNetworkSideControllers())
        all_cntrls.extend(ruby_system.io_rni.getAllControllers())

    # Assign downstream destinations
    if options.architecture.caches.SLC.active:
        for rnf in ruby_system.rnf:
            rnf.setDownstream(hnf_dests)
        if len(dma_ports) > 0:
            for rni in ruby_system.dma_rni:
                rni.setDownstream(hnf_dests)
        if full_system:
            ruby_system.io_rni.setDownstream(hnf_dests)
        for hnf in ruby_system.hnf:
            hnf.setDownstream(mem_dests)
    else:
        for rnf in ruby_system.rnf:
            rnf.setDownstream(mem_dests)
        if len(dma_ports) > 0:
            for rni in ruby_system.dma_rni:
                rni.setDownstream(mem_dests)
        if full_system:
            ruby_system.io_rni.setDownstream(mem_dests)

    # Setup data message size for all controllers
    for cntrl in all_cntrls:
        cntrl.data_channel_size = options.architecture.NOC.network.data_width

    # Network configurations
    # virtual networks: 0=request, 1=snoop, 2=response, 3=data
    ruby_system.network.number_of_virtual_networks = options.architecture.NOC.n_vnets
    ruby_system.number_of_virtual_networks = options.architecture.NOC.n_vnets

    # Message sizes
    ruby_system.network.control_msg_size = options.architecture.NOC.network.cntrl_msg_size
    ruby_system.network.data_msg_size    = options.architecture.NOC.network.data_width

    if options.architecture.NOC.network.model == "simple":
        # Router port buffer (per vnet)
        ruby_system.network.buffer_size = options.architecture.NOC.network.simple.router_buffer_size

    return (cpu_sequencers, mem_cntrls, network_nodes)

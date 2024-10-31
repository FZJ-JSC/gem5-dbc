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
#

import math

import m5
from m5.util import fatal
from m5.params import *
from m5.objects import *

from m5.defines import buildEnv

from modules.options import Options

from modules.ruby.topology import SimpleTopology
from modules.ruby.protocol import CHI

from modules.ruby.network import create_int_link, create_ext_link
from modules.util import fatal_error

class Mesh_NOC(SimpleTopology):
    description = 'Mesh_NOC'

    def __init__(self, options: Options, nodes: list = []):

        self.nodes = nodes

        self.router_latency  = options.architecture.NOC.topology.router_latency
        self.num_rows = options.architecture.NOC.topology.parameters["dim"][0]
        self.num_cols = options.architecture.NOC.topology.parameters["dim"][1]
        self.num_mesh_routers = self.num_rows * self.num_cols

        self.numa_ids = options.architecture.NOC.topology.parameters.get("numa", dict())

        self.router_numa_ids = [0] * self.num_mesh_routers

        for router_id in range(self.num_mesh_routers):
            for id, router_ids in self.numa_ids.items():
                if router_id in router_ids:
                    self.router_numa_ids[router_id] = id
                    break
        
        self.num_mem_regions = len(options.architecture.memory.regions)
        self.mem_numa_ids = [0] * self.num_mem_regions
        
        for region_id in range(self.num_mem_regions):
            # NUMA ID is defined to be the ID of the first router
            # in the corresponding SNF_Mem router list
            self.mem_numa_ids[region_id] = self.router_numa_ids[options.architecture.NOC.protocol.nodes["SNF_Mem"].router_list[region_id][0]]

        # Set the router classes based on the command line options
        RouterClass = dict(
                garnet=m5.objects.GarnetRouter,
                simple=m5.objects.Switch
            ).get(options.architecture.NOC.network.model, None)
        if RouterClass is None:
            fatal_error(f"Unknown network {options.architecture.NOC.network.model}")

        self._routers = [RouterClass(router_id=i, latency = self.router_latency) for i in range(self.num_mesh_routers)]

        self._link_count = 0
        self._int_links = []
        self._ext_links = []

        # Create all the mesh internal links.
        self.create_links(options)

    def create_links(self, options: Options):
        mesh_lvs = options.architecture.NOC.network.mesh_vnet_support

        # East->West, West->East, North->South, South->North
        # XY routing weights
        link_weights = [1, 1, 2, 2]
        dst_inport = ["West", "East", "South", "North"]

        # East output to West input links
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if (col + 1 < self.num_cols):
                    src = col + (row * self.num_cols)
                    dst = (col + 1) + (row * self.num_cols)

                    for supported_vnets in mesh_lvs:
                        int_links_len = len(self._int_links)
                        #print(f"EW link: R{src}.L{int_links_len}.R{dst} {supported_vnets}")

                        self._int_links.append(
                                create_int_link(
                                    options,
                                    link_id  = self._link_count,
                                    src_node = self._routers[src],
                                    dst_node = self._routers[dst],
                                    dst_inport = dst_inport[0],
                                    weight     = link_weights[0],
                                    vnet_support = supported_vnets
                                    ))
                        self._link_count += 1

        # West output to East input links
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if (col + 1 < self.num_cols):
                    src = (col + 1) + (row * self.num_cols)
                    dst = col + (row * self.num_cols)

                    for supported_vnets in mesh_lvs:
                        int_links_len = len(self._int_links)
                    #print(f"WE link: R{src}.L{int_links_len}.R{dst} {supported_vnets}")

                        self._int_links.append(
                                create_int_link(
                                    options,
                                    link_id  = self._link_count,
                                    src_node = self._routers[src],
                                    dst_node = self._routers[dst],
                                    dst_inport = dst_inport[1],
                                    weight     = link_weights[1],
                                    vnet_support = supported_vnets
                                    ))
                        self._link_count += 1

        # North output to South input links
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                if (row + 1 < self.num_rows):
                    src = col + (row * self.num_cols)
                    dst = col + ((row + 1) * self.num_cols)

                    for supported_vnets in mesh_lvs:
                        int_links_len = len(self._int_links)
                        #print(f"NS link: R{src}.L{int_links_len}.R{dst} {supported_vnets}")

                        self._int_links.append(
                                create_int_link(
                                    options,
                                    link_id  = self._link_count,
                                    src_node = self._routers[src],
                                    dst_node = self._routers[dst],
                                    dst_inport = dst_inport[2],
                                    weight     = link_weights[2],
                                    vnet_support = supported_vnets
                                    ))
                        self._link_count += 1

        # South output to North input links
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                if (row + 1 < self.num_rows):
                    src = col + ((row + 1) * self.num_cols)
                    dst = col + (row * self.num_cols)

                    for supported_vnets in mesh_lvs:
                        int_links_len = len(self._int_links)
                        #print(f"SN link: R{src}.L{int_links_len}.R{dst} {supported_vnets}")

                        self._int_links.append(
                                create_int_link(
                                    options,
                                    link_id  = self._link_count,
                                    src_node = self._routers[src],
                                    dst_node = self._routers[dst],
                                    dst_inport = dst_inport[3],
                                    weight     = link_weights[3],
                                    vnet_support = supported_vnets
                                ))
                        self._link_count += 1

        # dirs = [0,1,2,3]
        # for d in dirs:
        #     for row in range(num_rows):
        #         for col in range(num_cols):
        #             if (d < 2 and col + 1 < num_cols) or ((d >= 2 and row + 1 < num_rows)):
        #                 node = [col + (row * num_cols), col + (row * num_cols) + (1 if d < 2 else num_cols)]
        #                 src = node[(d)%2]
        #                 dst = node[(d+1)%2]
        #                 for vnet_support in mesh_lvs:
        #                     int_links_len = len(self._int_links)
        #                     print(f"EW link: R{src}.L{int_links_len}.R{dst} {vnet_support}")
        #                     self._int_links.append(
        #                         create_int_link(
        #                             options,
        #                             link_id  = self._link_count,
        #                             src_node = self._routers[src],
        #                             dst_node = self._routers[dst],
        #                             dst_inport = dst_inport[d],
        #                             weight     = link_weights[d],
        #                             vnet_support = vnet_support
        #                             )
        #                         )
        #                     self._link_count += 1


    def _createRNFRouter(self, options: Options, mesh_router):
        # Create a zero-latency router bridging node controllers and the mesh router

        cbar_lvs       = options.architecture.NOC.network.cbar_vnet_support
        link_latency   = options.architecture.NOC.topology.cbar_link_latency
        router_latency = options.architecture.NOC.topology.cbar_router_latency

        router_id = len(self._routers)

        # Set the network classes based on the command line options
        if options.architecture.NOC.network.model == "garnet":
            RouterClass  = m5.objects.GarnetRouter
        elif options.architecture.NOC.network.model == "simple":
            RouterClass  = m5.objects.Switch
        else:
            fatal_error(f"Unknown network {options.architecture.NOC.network.model}")

        # Set bus latency to zero
        node_router = RouterClass(
            router_id = router_id,
            latency = router_latency,
            router_class = 1
            )

        self._routers.append(node_router)

        for supported_vnets in cbar_lvs:
            int_links_len = len(self._int_links)
            #print(f"RN link: R{node_router.router_id}.L{int_links_len}.R{mesh_router.router_id}")

            # connect node_router <-> mesh router
            self._int_links.append(
                create_int_link(
                    options,
                    link_id = self._link_count,
                    src_node = node_router,
                    dst_node = mesh_router,
                    latency = link_latency,
                    vnet_support=supported_vnets
                    ))
            self._link_count += 1

            int_links_len = len(self._int_links)
            #print(f"RN link: R{mesh_router.router_id}.L{int_links_len}.R{node_router.router_id}")

            self._int_links.append(
                create_int_link(
                    options,
                    link_id = self._link_count,
                    src_node = mesh_router,
                    dst_node = node_router,
                    latency = link_latency,
                    vnet_support=supported_vnets
                    ))
            self._link_count += 1

        return node_router

    def distributeNodes(self, options: Options, node_list, node_name: str):

        num_nodes_per_router = options.architecture.NOC.protocol.nodes[node_name].nodes_per_router
        router_idx_list      = options.architecture.NOC.protocol.nodes[node_name].router_list
        mesh_lvs             = options.architecture.NOC.network.mesh_vnet_support
        mesh_link_latency    = options.architecture.NOC.topology.node_link_latency
        rnf_single_router    = options.architecture.NOC.protocol.rnf_single_router

        if num_nodes_per_router:
            # evenly distribute nodes to all listed routers
            router_idx = lambda idx: idx // num_nodes_per_router
        else:
            # try to circulate all nodes to all routers, some routers may be
            # connected to zero or more than one node.
            router_idx = lambda idx: idx  % len(router_idx_list)

        for idx, node in enumerate(node_list):
            mesh_router_idx = node._router_id if node._router_id is not None else router_idx_list[router_idx(idx)]
            router = self._routers[mesh_router_idx]

            # Create another router bridging RNF node controllers and the mesh router
            # for non-RNF nodes, node router is mesh router
            if isinstance(node, CHI.CHI_RNF) and rnf_single_router:
                router = self._createRNFRouter(options, router)
            # connect all ctrls in the node to node_router
            ctrls = node.getNetworkSideControllers()
            for i, c in enumerate(ctrls):
                for supported_vnets in mesh_lvs:
                    #print("EXT link: EXT.{}.{}.{}.L{}.R{} {}".format(node.__class__.__name__, i, c.__class__.__name__, self._link_count, router.router_id, supported_vnets))
                    self._ext_links.append(
                        create_ext_link(
                            options,
                            link_id = self._link_count,
                            ext_node = c,
                            int_node = router,
                            latency = mesh_link_latency,
                            vnet_support=supported_vnets
                        ))
                    self._link_count += 1

    def makeTopology(self, options: Options, network):
        assert(buildEnv['PROTOCOL'] == 'CHI')

        # classify nodes into different types
        mesh_nodes = dict(
            RNF = [],
            HNF = [],
            SNF_Mem = [],
            SNF_IO = [],
            RNI_IO = [],
        )

        for n in self.nodes:
            if isinstance(n, CHI.CHI_RNF):
                mesh_nodes["RNF"].append(n)
            elif isinstance(n, CHI.CHI_HNF):
                mesh_nodes["HNF"].append(n)
            elif isinstance(n, CHI.CHI_SNF_MainMem):
                mesh_nodes["SNF_Mem"].append(n)
            elif isinstance(n, CHI.CHI_SNF_BootMem):
                mesh_nodes["SNF_IO"].append(n)
            elif isinstance(n, CHI.CHI_RNI_DMA):
                mesh_nodes["RNI_IO"].append(n)
            elif isinstance(n, CHI.CHI_RNI_IO):
                mesh_nodes["RNI_IO"].append(n)
            else:
                fatal('topologies.Mesh_NOC: {} not supported'.format(n.__class__.__name__))

        # Place nodes on the mesh
        for label, nodes in mesh_nodes.items():
            self.distributeNodes(options, nodes, label)

        # Set up
        network.int_links = self._int_links
        network.ext_links = self._ext_links
        network.routers = self._routers

        pairing = options.architecture.NOC.protocol.pairing
        if pairing != None:
            self._autoPairHNFandSNF(mesh_nodes["HNF"], mesh_nodes["SNF_Mem"], pairing)

    def _autoPairHNFandSNF(self, cache_ctrls, mem_ctrls, pairing):
        # Use the pairing defined by the configuration to reassign the
        # memory ranges
        pair_debug = False 
        all_cache = []
        for c in cache_ctrls: all_cache.extend(c.getNetworkSideControllers())
        all_mem = []
        for c in mem_ctrls: all_mem.extend(c.getNetworkSideControllers())

        # checks and maps index from pairing map to component
        assert(len(pairing) == len(all_cache))

        def _tolist(val): return val if isinstance(val, list) else [val]

        for m in all_mem: m._pairing = []

        pairing_check = max(1, len(all_mem) / len(all_cache))
        for cidx,c in enumerate(all_cache):
            c._pairing = []
            for midx in _tolist(pairing[cidx]):
                c._pairing.append(all_mem[midx])
                if c not in all_mem[midx]._pairing:
                    all_mem[midx]._pairing.append(c)
            assert(len(c._pairing) == pairing_check)
            if pair_debug:
                print(c.path())
                for r in c.addr_ranges:
                    print("%s" % r)
                for p in c._pairing:
                    print("\t"+p.path())
                    for r in p.addr_ranges:
                        print("\t%s" % r)

        # all must be paired
        for c in all_cache: assert(len(c._pairing) > 0)
        for m in all_mem: assert(len(m._pairing) > 0)

        # only support a single range for the main memory controllers
        tgt_range_start = all_mem[0].addr_ranges[0].start.value
        for mem in all_mem:
            for r in mem.addr_ranges:
                if r.start.value != tgt_range_start:
                    fatal('topologies.CustomMesh: not supporting pairing of '\
                          'main memory with multiple ranges')

        # reassign ranges for a 1 -> N paring
        def _rerange(src_cntrls, tgt_cntrls, fix_tgt_peer):
            assert(len(tgt_cntrls) >= len(src_cntrls))

            def _rangeToBit(addr_ranges):
                bit = None
                for r in addr_ranges:
                    if bit == None:
                        bit = r.intlvMatch
                    else:
                        assert(bit == r.intlvMatch)
                return bit

            def _getPeer(cntrl):
                return cntrl.memory_out_port.peer.simobj

            sorted_src = list(src_cntrls)
            sorted_src.sort(key = lambda x: _rangeToBit(x.addr_ranges))

            # paired controllers need to have seq. interleaving match values
            intlvMatch = 0
            for src in sorted_src:
                for tgt in src._pairing:
                    for r in tgt.addr_ranges:
                        r.intlvMatch = intlvMatch
                    if fix_tgt_peer:
                        _getPeer(tgt).range.intlvMatch = intlvMatch
                    intlvMatch = intlvMatch + 1

            # recreate masks
            for src in sorted_src:
                for src_range in src.addr_ranges:
                    if src_range.start.value != tgt_range_start:
                        continue
                    new_src_mask = []
                    for m in src_range.masks:
                        # TODO should mask all the way to the max range size
                        new_src_mask.append(m | (m*2) | (m*4) |
                                                  (m*8) | (m*16))
                    for tgt in src._pairing:
                        paired = False
                        for tgt_range in tgt.addr_ranges:
                            if tgt_range.start.value == \
                               src_range.start.value:
                                src_range.masks = new_src_mask
                                new_tgt_mask = []
                                lsbs = len(tgt_range.masks) - \
                                       len(new_src_mask)
                                for i in range(lsbs):
                                    new_tgt_mask.append(tgt_range.masks[i])
                                for m in new_src_mask:
                                    new_tgt_mask.append(m)
                                tgt_range.masks = new_tgt_mask
                                if fix_tgt_peer:
                                    _getPeer(tgt).range.masks = new_tgt_mask
                                paired = True
                        if not paired:
                            fatal('topologies.CustomMesh: could not ' \
                                    'reassign ranges {} {}'.format(
                                    src.path(), tgt.path()))
        if len(all_mem) >= len(all_cache):
            _rerange(all_cache, all_mem, True)
        else:
            _rerange(all_mem, all_cache, False)

        if pair_debug:
            print("")
            for cidx,c in enumerate(all_cache):
                assert(len(c._pairing) == pairing_check)
                print(c.path())
                for r in c.addr_ranges:
                    print("%s" % r)
                for p in c._pairing:
                    print("\t"+p.path())
                    for r in p.addr_ranges:
                        print("\t%s" % r)



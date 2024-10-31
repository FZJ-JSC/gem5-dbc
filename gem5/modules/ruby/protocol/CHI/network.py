# Copyright (c) 2016 Georgia Institute of Technology
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

import m5

from modules.options import Options
from modules.util import fatal_error

def init_bridges(network):
    # Create Bridges and connect them to the corresponding links

    for intLink in network.int_links:
        intLink.src_net_bridge = m5.objects.NetworkBridge(
            link = intLink.network_link,
            vtype = 'OBJECT_LINK',
            width = intLink.src_node.width)
        intLink.src_cred_bridge = m5.objects.NetworkBridge(
            link = intLink.credit_link,
            vtype = 'LINK_OBJECT',
            width = intLink.src_node.width)
        intLink.dst_net_bridge = m5.objects.NetworkBridge(
            link = intLink.network_link,
            vtype = 'LINK_OBJECT',
            width = intLink.dst_node.width)
        intLink.dst_cred_bridge = m5.objects.NetworkBridge(
            link = intLink.credit_link,
            vtype = 'OBJECT_LINK',
            width = intLink.dst_node.width)

    for extLink in network.ext_links:
        ext_net_bridges = []
        ext_net_bridges.append(m5.objects.NetworkBridge(
            link = extLink.network_links[0],
            vtype = 'OBJECT_LINK',
            width = extLink.width))
        ext_net_bridges.append(m5.objects.NetworkBridge(
            link = extLink.network_links[1],
            vtype = 'LINK_OBJECT',
            width = extLink.width))
        extLink.ext_net_bridge = ext_net_bridges

        ext_credit_bridges = []
        ext_credit_bridges.append(m5.objects.NetworkBridge(
            link = extLink.credit_links[0],
            vtype = 'LINK_OBJECT',
            width = extLink.width))
        ext_credit_bridges.append(m5.objects.NetworkBridge(
            link = extLink.credit_links[1],
            vtype = 'OBJECT_LINK',
            width = extLink.width))
        extLink.ext_cred_bridge = ext_credit_bridges

        int_net_bridges = []
        int_net_bridges.append(m5.objects.NetworkBridge(
            link = extLink.network_links[0],
            vtype = 'LINK_OBJECT',
            width = extLink.int_node.width))
        int_net_bridges.append(m5.objects.NetworkBridge(
            link = extLink.network_links[1],
            vtype = 'OBJECT_LINK',
            width = extLink.int_node.width))
        extLink.int_net_bridge = int_net_bridges

        int_cred_bridges = []
        int_cred_bridges.append(m5.objects.NetworkBridge(
            link = extLink.credit_links[0],
            vtype = 'OBJECT_LINK',
            width = extLink.int_node.width))
        int_cred_bridges.append(m5.objects.NetworkBridge(
            link = extLink.credit_links[1],
            vtype = 'LINK_OBJECT',
            width = extLink.int_node.width))
        extLink.int_cred_bridge = int_cred_bridges

def init_network(options: Options, network, num_rows = None, num_cols = None):

    # Initialize network based on topology
    if options.architecture.NOC.network.model == "garnet":
        network.num_rows =  num_rows
        network.num_cols =  num_cols 
        network.vcs_per_vnet = options.architecture.NOC.network.garnet.vcs_per_vnet

        network.ni_flit_size              = options.architecture.NOC.network.ni_flit_size
        network.routing_algorithm         = options.architecture.NOC.network.garnet.routing_algorithm
        network.garnet_deadlock_threshold = options.architecture.NOC.network.garnet.deadlock_threshold

        if (options.architecture.NOC.network.garnet.use_link_bridges):
            init_bridges(network)

    elif options.architecture.NOC.network.model == "simple":
        network.setup_buffers()
    else:
        fatal_error(f"Unknown network {options.architecture.NOC.network.model}")

    # Set the network classes based on the command line options
    if options.architecture.NOC.network.model == "garnet":
        InterfaceClass = m5.objects.GarnetNetworkInterface
    elif options.architecture.NOC.network.model == "simple":
        InterfaceClass = None
    else:
        fatal_error(f"Unknown network {options.architecture.NOC.network.model}")

    if InterfaceClass != None:
        netifs = [InterfaceClass(id=i) for (i,n) in enumerate(network.ext_links)]
        network.netifs = netifs

    if options.architecture.NOC.network_fault_model:
        assert(options.architecture.NOC.network.model == "garnet")
        network.enable_fault_model = True
        network.fault_model = m5.objects.FaultModel()

# Copyright (c) 2012, 2017-2018, 2021 ARM Limited
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
# Copyright (c) 2006-2007 The Regents of The University of Michigan
# Copyright (c) 2009 Advanced Micro Devices, Inc.
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

from modules.ruby.memory import configure_mem_region_controller
from modules.ruby.protocol import CHI
from modules.ruby.topology.Mesh_NOC.Mesh_NOC import Mesh_NOC

from modules.util import fatal_error
import modules.filesystem


def configure_ruby(system, options: Options, piobus = None, dma_ports = [], bootmem=None):

    system.ruby = m5.objects.RubySystem(
        # Set block sizes for Ruby
        block_size_bytes = options.architecture.caches.cache_line_size,
        memory_size_bits = 48
    )

    # Generate pseudo filesystem
    modules.filesystem.create(system, options)

    # Create the network object
    NetworkClass = dict(
            garnet=m5.objects.GarnetNetwork,
            simple=m5.objects.SimpleNetwork
        ).get(options.architecture.NOC.network.model, None)
    if NetworkClass is None:
        fatal_error(f"Unknown network {options.architecture.NOC.network.model}")

    # Instantiate the network object
    # so that the controllers can connect to it.
    network = NetworkClass(
        ruby_system = system.ruby,
        topology  = options.architecture.NOC.topology.model,
        routers   = [],
        ext_links = [],
        int_links = [],
        netifs    = []
    )

    system.ruby.network = network

    # Instantiate network topology
    topology = Mesh_NOC(options)    

    # Create memory controllers
    (cpu_sequencers, dir_cntrls, network_nodes) = CHI.create_system(
        options,
        system,
        dma_ports = dma_ports,
        bootmem = bootmem,
        router_numa_ids = topology.router_numa_ids,
        mem_numa_ids    = topology.mem_numa_ids
    )

    # Add nodes
    topology.set_nodes(network_nodes)

    # Create the network topology
    topology.makeTopology(options, network)

    # Register the topology elements with faux filesystem (SE mode only)
    if not options.simulation.fs_mode:
        topology.registerTopology(options)

    # Initialize network based on topology
    CHI.init_network(
        options,
        system.ruby.network,
        num_rows = topology.num_rows,
        num_cols = topology.num_cols
    )

    # Create a port proxy for connecting the system port. This is
    # independent of the protocol and kept in the protocol-agnostic part (i.e. here).
    sys_port_proxy = m5.objects.RubyPortProxy(ruby_system = system.ruby)
    if piobus is not None:
        sys_port_proxy.pio_request_port = piobus.cpu_side_ports

    # Give the system port proxy a SimObject parent without creating a full-fledged controller
    system.sys_port_proxy = sys_port_proxy
    # Connect the system port for loading of binaries etc
    system.system_port = system.sys_port_proxy.in_ports
    # Memory
    # Creates memory controllers attached to a directory controller.
    # A separate controller is created for each address range
    # as the abstract memory can handle only one contiguous address range as of now.
    system.mem_ctrls = configure_mem_region_controller(options, system, dir_cntrls)

    # Connect the cpu sequencers and the piobus
    if piobus is not None:
        for cpu_seq in cpu_sequencers:
            cpu_seq.connectIOPorts(piobus)

    system.ruby.number_of_virtual_networks = system.ruby.network.number_of_virtual_networks
    system.ruby._cpu_ports = cpu_sequencers
    system.ruby.num_of_sequencers = len(cpu_sequencers)

    # Create a backing copy of physical memory in case required
    if options.architecture.NOC.access_backing_store:
        system.ruby.access_backing_store = True
        system.ruby.phys_mem = m5.objects.SimpleMemory(
            range=system.mem_ranges[0],
            in_addr_map=False
        )

    # Create a seperate clock domain for Ruby
    system.ruby.clk_domain = m5.objects.SrcClockDomain(
        clock = options.architecture.NOC.clock,
        voltage_domain = system.voltage_domain
    )

    if options.simulation.fs_mode:
        # Connect the ruby io port to the PIO bus, assuming that there is just one such port.
        system.iobus.mem_side_ports = system.ruby._io_port.in_ports

        # Tie the cpu ports to the correct ruby system ports
        for (i, cpu) in enumerate(system.cpu):
            cpu.clk_domain = system.cpu_clk_domain
            cpu.createThreads()
            cpu.createInterruptController()

            system.ruby._cpu_ports[i].connectCpuPorts(cpu)
    else:
        # Tie the cpu ports to the correct ruby system ports
        for (i, cpu) in enumerate(system.cpu):
            #cpu.clk_domain = system.cpu_clk_domain
            #cpu.createThreads()
            cpu.createInterruptController()
            system.ruby._cpu_ports[i].connectCpuPorts(cpu)

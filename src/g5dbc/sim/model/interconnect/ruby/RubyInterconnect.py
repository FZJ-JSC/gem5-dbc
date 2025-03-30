from g5dbc.config import Config
from g5dbc.sim.factory.network import NetworkFactory
from g5dbc.sim.factory.topology.ruby import RubyTopologyFactory
from g5dbc.sim.m5_objects import m5_AddrRange
from g5dbc.sim.m5_objects.io import m5_IOXBar, m5_SystemXBar
from g5dbc.sim.m5_objects.mem import m5_SimpleMemory
from g5dbc.sim.m5_objects.ruby import m5_RubyPortProxy, m5_RubySystem
from g5dbc.sim.model.cpu import AbstractProcessor
from g5dbc.sim.model.interconnect import CoherentInterconnect
from g5dbc.sim.model.memory import AbstractMemSystem
from g5dbc.sim.model.topology import NodeSpec

from .controller import AbstractController
from .node.chi import HNF, RNF, RNI, SNF, SNF_ROM


class RubyInterconnect(CoherentInterconnect):

    def __init__(self, config: Config) -> None:
        super().__init__()

        self._config = config
        self._cache_line_size = config.system.cache_line_size

        self.configure_system_clocks(config.network.clock)

        self.ruby_system = m5_RubySystem(
            # Set block sizes for Ruby
            block_size_bytes=config.system.cache_line_size,
            memory_size_bits=48,
            number_of_virtual_networks=config.network.n_vnets,
            clk_domain=self.clk_domain,
        )

        self._topology = RubyTopologyFactory.create(config)

        self.init_interconnect()

    def init_interconnect(self):
        config = self._config
        topology = self._topology

        # Create RNF nodes
        self.rnf = [RNF(node_id) for node_id in topology.get_cpu_nodes()]

        # Create HNF nodes
        self.hnf = [HNF(node_id) for node_id in topology.get_slc_nodes()]

        # Create SNF Nodes
        self.snf = [SNF(node_id) for node_id in topology.get_mem_nodes()]

        # Create PIO controller
        self.pio = [RNI(node_id) for node_id in topology.get_dma_nodes()[:1]]

        for node in [*self.rnf, *self.hnf, *self.snf, *self.pio]:
            node.create_controller(config, self.ruby_system)

    def connect_IO_bus(self, iobus: m5_IOXBar) -> None:
        for node in self.rnf:
            dcache_seq, _ = node.get_sequencers()
            dcache_seq.connect_IO_bus(iobus)

        # Setup IO port
        for seq in self.pio[0].get_sequencers():
            iobus.mem_side_ports = seq.in_ports

    def connect_MEM_bus(self, membus: m5_SystemXBar) -> None:
        pass

    def connect_board_port(self, system_port):
        self.ruby_system.sys_port_proxy = m5_RubyPortProxy(ruby_system=self.ruby_system)
        self.ruby_system.sys_port_proxy.in_ports = system_port

    def connect_cpu_nodes(self, processor: AbstractProcessor) -> None:
        assert processor.get_num_cpus() == len(self.rnf)

        # Connect CPUs
        for node in self.rnf:
            node.set_clock_domain(processor.get_clock_domain())

            core_id = node.get_core_id()
            numa_id = node.get_numa_id()

            core = processor.get_active_core(core_id)

            assert (
                core.get_core_id() == core_id
            ), f"ctrl_id={core.get_core_id()} core_id={core_id}"

            # Get dcache and icache sequencers
            dcache_seq, icache_seq = node.get_sequencers()

            core.set_numa_id(numa_id)
            core.connect_dcache(dcache_seq.in_ports)
            core.connect_icache(icache_seq.in_ports)

            core.connect_walker_ports(dcache_seq.in_ports, icache_seq.in_ports)
            core.connect_interrupt()

    def connect_slc_nodes(self, slc_ranges: list[list[m5_AddrRange]]) -> None:
        from g5dbc.sim.factory.interconnect.slc import MaskFactory

        config = self._config

        generate_mask = MaskFactory.create(config)

        assert len(config.memory.regions) == len(slc_ranges)

        for numa_id, hnf_ranges in enumerate(slc_ranges):
            # Collect HNFs serving numa_id
            hnfs = [hnf for hnf in self.hnf if hnf.get_numa_id() == numa_id]

            # Sort by Controller id
            hnfs.sort(key=lambda x: x.get_ctrl_id())

            # Calculate HNF mask
            mask = generate_mask(len(hnfs))

            # Set ranges for current numa domain
            for ctrl_id, hnf in enumerate(hnfs):
                assert ctrl_id == hnf.get_ctrl_id()
                addr_ranges = [
                    m5_AddrRange(
                        mem_range.start,
                        size=mem_range.size(),
                        masks=mask,
                        intlvMatch=ctrl_id,
                    )
                    for mem_range in hnf_ranges
                ]
                for ctrl in hnf.get_controllers():
                    ctrl.set_addr_ranges(addr_ranges)

    def connect_mem_nodes(self, mem_sys: AbstractMemSystem) -> None:
        for node in self.snf:
            ctrl_id = node.get_ctrl_id()
            numa_id = node.get_numa_id()
            mem_ctrl = mem_sys.get_mem_ctrl(numa_id, ctrl_id)

            for ctrl in node.get_controllers():
                mem_ctrl.connect_memory_port(ctrl.memory_out_port)
                ctrl.set_addr_ranges(mem_ctrl.get_addr_ranges())

    def connect_rom_nodes(self, mems: list[m5_SimpleMemory]):
        config = self._config

        node_ids = self._topology.get_rom_nodes()
        node_idx = lambda idx: node_ids[idx % len(node_ids)]

        # Create ROM Nodes
        self.rom = [
            SNF_ROM(NodeSpec(router_id=node_idx(i).router_id, ctrl_id=i))
            for i in range(len(mems))
        ]

        for node in self.rom:
            node.create_controller(config, self.ruby_system)

            for ctrl in node.get_controllers():
                mems[node.get_ctrl_id()].port = ctrl.memory_out_port
                ctrl.set_addr_ranges([mems[node.get_ctrl_id()].range])

    def connect_dma_nodes(self, ports: list):
        config = self._config

        node_ids = self._topology.get_dma_nodes()
        node_idx = lambda idx: node_ids[idx % len(node_ids)]

        # Create DMA Nodes
        self.dma = [
            RNI(NodeSpec(router_id=node_idx(i).router_id, ctrl_id=i))
            for i in range(len(ports))
        ]

        for node in self.dma:
            node.create_controller(config, self.ruby_system)

            for seq in node.get_sequencers():
                seq.in_ports = ports[node.get_ctrl_id()]

    def connect_network(self):
        config = self._config
        topology = self._topology

        nodes = [
            *self.rnf,
            *self.hnf,
            *self.snf,
            *self.pio,
            *self.dma,
            *self.rom,
        ]

        network = NetworkFactory.create(config, self.ruby_system)

        network.initialize(topology)

        network.connect_nodes(nodes)
        network.connect_interfaces()

        self.ruby_system.set_network(network)

        # Set number of sequencers
        seqs = []
        for node in nodes:
            seqs.extend(node.get_sequencers())

        self.ruby_system.set_num_of_sequencers(len(seqs))

    def set_downstream(self):
        mem_dests: list[AbstractController] = []
        hnf_dests: list[AbstractController] = []

        for hnf in self.hnf:
            hnf_dests.extend(hnf.get_controllers())

        for mem in [*self.snf, *self.rom]:
            mem_dests.extend(mem.get_controllers())

        for node in [*self.rnf, *self.pio, *self.dma]:
            node.set_downstream(hnf_dests)
        for hnf in self.hnf:
            hnf.set_downstream(mem_dests)

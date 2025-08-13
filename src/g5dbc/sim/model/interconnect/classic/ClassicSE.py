from g5dbc.config import Config
from g5dbc.sim.factory.interconnect.slc import MaskFactory
from g5dbc.sim.m5_objects import m5_AddrRange
from g5dbc.sim.m5_objects.io import m5_IOXBar, m5_SystemXBar
from g5dbc.sim.m5_objects.mem import m5_SimpleMemory
from g5dbc.sim.model.cpu import AbstractProcessor
from g5dbc.sim.model.interconnect import CoherentInterconnect
from g5dbc.sim.model.memory import AbstractMemSystem

from .cache import ClassicCache, ClassicXBar


class ClassicSE(CoherentInterconnect):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config

        # config.caches #options.architecture.caches.cache_levels
        self._ncpus = config.system.num_cpus
        self._num_slcs = (
            0
            if "SLC" not in config.caches
            else config.system.num_cpus * config.interconnect.classic.slcs_per_core
        )

        # L1I Caches
        self.l1i = [ClassicCache(config.caches["L1I"]) for _ in range(self._ncpus)]
        for _cache in self.l1i:
            _cache.set_prefetcher(config.caches["L1I"].prefetcher)

        # L1D Caches
        self.l1d = [ClassicCache(config.caches["L1D"]) for _ in range(self._ncpus)]
        for _cache in self.l1d:
            _cache.set_prefetcher(config.caches["L1D"].prefetcher)

        # L2 Caches
        self.l2cache = [ClassicCache(config.caches["L2"]) for _ in range(self._ncpus)]
        for _cache in self.l2cache:
            _cache.set_prefetcher(config.caches["L2"].prefetcher)

        # L3 Caches
        if self._num_slcs > 0:
            self.l3cache = [
                ClassicCache(config.caches["SLC"]) for _ in range(self._num_slcs)
            ]
            for _cache in self.l3cache:
                _cache.set_prefetcher(config.caches["SLC"].prefetcher)

        # ITLB Page walk caches
        self.iwc = [ClassicCache(config.caches["IWC"]) for _ in range(self._ncpus)]
        # DTLB Page walk caches
        self.dwc = [ClassicCache(config.caches["DWC"]) for _ in range(self._ncpus)]

        # L2 XBar
        self.l2bus = [ClassicXBar(config.caches["L2"]) for _ in range(self._ncpus)]
        # L3 XBar
        if self._num_slcs > 0:
            self.l3bus = ClassicXBar(config.caches["SLC"])

    def connect_IO_bus(self, iobus: m5_IOXBar) -> None:
        pass
        # self._iobus = iobus

    def connect_MEM_bus(self, membus: m5_SystemXBar) -> None:
        self._membus = membus

    def connect_board_port(self, system_port):
        # Set up the system port for functional access from the simulator.
        self._membus.cpu_side_ports = system_port

    def connect_cpu_nodes(self, processor: AbstractProcessor) -> None:
        for cpu_id in range(processor.get_num_cpus()):
            core = processor.get_active_core(cpu_id)

            core.connect_dcache(self.l1d[cpu_id].cpu_side)
            core.connect_icache(self.l1i[cpu_id].cpu_side)
            core.connect_walker_ports(
                self.iwc[cpu_id].cpu_side, self.dwc[cpu_id].cpu_side
            )
            for _cache in [self.l1i, self.l1d, self.iwc, self.dwc]:
                _cache[cpu_id].mem_side = self.l2bus[cpu_id].cpu_side_ports

            self.l2bus[cpu_id].mem_side_ports = self.l2cache[cpu_id].cpu_side

            core.connect_interrupt()

    def connect_slc_nodes(self, slc_ranges: list[list[m5_AddrRange]]) -> None:
        generate_mask = MaskFactory.create(self._config)

        # @TODO: Handle NUMA regions
        mem_ranges = [slc_ranges[0][0]]

        # Create a cache for coherent I/O connections
        # self.iocache = ClassicCache(
        #    self._config.caches["CoherentIO"], addr_ranges=mem_ranges
        # )
        # self.iocache.mem_side = self._membus.cpu_side_ports
        # self.iocache.cpu_side = self._iobus.mem_side_ports

        if self._num_slcs > 0:
            mask = generate_mask(self._num_slcs)

            for id, l3 in enumerate(self.l3cache):
                l3.addr_ranges = [
                    m5_AddrRange(
                        0,
                        size=mem_range.end,
                        masks=mask,
                        intlvMatch=id,
                    )
                    for mem_range in mem_ranges
                ]

    def connect_mem_nodes(self, mem_sys: AbstractMemSystem) -> None:
        """
        Connect Memory controllers to corresponding interconnect controller
        """
        for ctrl in mem_sys.get_mem_ctrls():
            ctrl.connect_memory_port(self._membus.mem_side_ports)

    def connect_rom_nodes(self, mems: list[m5_SimpleMemory]):
        pass

    def connect_dma_nodes(self, ports: list):
        pass

    def connect_network(self):
        pass

    def set_downstream(self):
        if self._num_slcs == 0:
            for l2 in self.l2cache:
                l2.mem_side = self._membus.cpu_side_ports
        else:
            for l2 in self.l2cache:
                l2.mem_side = self.l3bus.cpu_side_ports
            # For each l3 connect to the XBar
            for l3 in self.l3cache:
                self.l3bus.mem_side_ports = l3.cpu_side
                l3.mem_side = self._membus.cpu_side_ports

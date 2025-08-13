from g5dbc.config import Config
from g5dbc.config.artifacts import BinaryArtifact
from g5dbc.config.memory import MemoryRegionConfig
from g5dbc.sim.m5_objects import (
    m5_Addr,
    m5_AddrRange,
    m5_SrcClockDomain,
    m5_VoltageDomain,
)
from g5dbc.sim.m5_objects.io import m5_BadAddr, m5_IOXBar, m5_SystemXBar
from g5dbc.sim.m5_objects.mem import m5_SimpleMemory
from g5dbc.sim.m5_objects.sim import m5_Process, m5_System
from g5dbc.sim.model.cpu import AbstractProcessor
from g5dbc.sim.model.interconnect import CoherentInterconnect
from g5dbc.sim.model.memory import AbstractMemSystem
from g5dbc.sim.model.work import AbstractWork

from .AbstractBoardSystem import AbstractBoardSystem


class BoardSystemSE(m5_System, AbstractBoardSystem):

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)

        self._config = config

        self.create_system_clocks(config)

        self.init_board()

        self.create_IO_bus()

    def init_board(self) -> None:
        config = self._config
        self.mem_ranges = self.create_memory_ranges(config.memory.regions)

    def create_IO_bus(self):
        config = self._config

        self._dma_ports = None if config.interconnect.is_classic() else []
        self._mem_ports = []

        if config.interconnect.is_classic():
            # Configure MemBus
            self.membus = m5_SystemXBar(width=64)

            self.membus.badaddr_responder = m5_BadAddr()
            self.membus.badaddr_responder.warn_access = "warn"
            self.membus.default = self.membus.badaddr_responder.pio

    def get_IO_bus(self) -> m5_IOXBar:
        return self.iobus

    def get_MEM_bus(self) -> m5_SystemXBar:
        return self.membus

    def get_DMA_ports(self) -> list:
        """
        Return a list of m5.objects.Port
        """
        return [] if self._dma_ports is None else self._dma_ports

    def attach_disk_images(self, disk_images: list[BinaryArtifact]):
        pass

    def assign_workload(self, work: AbstractWork) -> AbstractBoardSystem:

        self.workload = work

        return self

    def create_memory_ranges(
        self, regions: list[MemoryRegionConfig]
    ) -> list[m5_AddrRange]:
        mem_ranges: list[m5_AddrRange] = []
        start = 0
        for region in regions:
            size = int(m5_Addr(region.size))
            mem_ranges.append(m5_AddrRange(start, size=size))
            start = start + size

        return mem_ranges

    def connect_processor(self, processor: AbstractProcessor) -> AbstractBoardSystem:
        config = self._config

        self.cpus = processor

        se_paths = dict(
            [
                (o.name, o.path)
                for o in config.search_artifacts("EXEC")
                + config.search_artifacts("OBJECT")
            ]
        )

        se_cmd = [se_paths.get(p, p) for p in config.simulation.se_cmd]

        self.cpus.set_workload(
            m5_Process(
                executable=se_cmd[0],
                cmd=se_cmd,
                input=config.simulation.se_stdin,
                output=config.simulation.se_stdout,
                errout=config.simulation.se_stderr,
            )
        )

        # Set Memory access mode
        mem_mode = processor.get_active_mem_mode()
        # Ruby only supports atomic accesses in noncaching mode
        if f"{mem_mode}" == "atomic" and not config.interconnect.is_classic():
            mem_mode = "atomic_noncaching"

        self.mem_mode = mem_mode

        return self

    def connect_memory(self, memory: AbstractMemSystem) -> AbstractBoardSystem:
        self.mem_ctrls = memory

        # Set memory ranges
        self.mem_ctrls.set_memory_ranges(self.mem_ranges)

        return self

    def connect_interconnect(self, ic: CoherentInterconnect) -> AbstractBoardSystem:
        self.interconnect = ic

        ic.connect_MEM_bus(self.get_MEM_bus())

        ic.connect_board_port(self.system_port)

        # Connect CPUs
        ic.connect_cpu_nodes(self.get_board_procesor())

        # Define HNF ranges
        hnf_ranges = [[r] for r in self.get_mem_ranges()]

        # Connect HNFs
        ic.connect_slc_nodes(hnf_ranges)

        # Connect Mem
        ic.connect_mem_nodes(self.mem_ctrls)

        ic.set_downstream()

        return self

    def get_board_procesor(self) -> AbstractProcessor:
        return self.cpus

    def get_board_memories(self) -> list[m5_SimpleMemory]:
        return []

    def get_mem_ranges(self) -> list[m5_AddrRange]:
        return self.mem_ranges

    def create_system_clocks(self, config: Config):
        self.voltage_domain = m5_VoltageDomain(voltage=config.system.voltage)
        self.clk_domain = m5_SrcClockDomain(
            clock=config.system.clock, voltage_domain=self.voltage_domain
        )

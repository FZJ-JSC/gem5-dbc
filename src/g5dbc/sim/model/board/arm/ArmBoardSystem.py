from g5dbc.config import Config
from g5dbc.config.artifacts import BinaryArtifact
from g5dbc.config.memory import MemoryRegionConfig
from g5dbc.sim.m5_objects import (
    m5_Addr,
    m5_AddrRange,
    m5_SrcClockDomain,
    m5_VoltageDomain,
)
from g5dbc.sim.m5_objects.arch import m5_ArmSystem
from g5dbc.sim.m5_objects.dev import m5_PciVirtIO, m5_VirtIOBlock
from g5dbc.sim.m5_objects.io import m5_BadAddr, m5_Bridge, m5_IOXBar, m5_SystemXBar
from g5dbc.sim.m5_objects.mem import m5_SimpleMemory
from g5dbc.sim.model.cpu import AbstractProcessor
from g5dbc.sim.model.interconnect import CoherentInterconnect
from g5dbc.sim.model.memory import AbstractMemSystem
from g5dbc.sim.model.storage import FileDiskImage
from g5dbc.sim.model.work import AbstractWork

from ..AbstractBoardSystem import AbstractBoardSystem


class ArmBoardSystem(m5_ArmSystem, AbstractBoardSystem):

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)

        self._config = config

        self.create_system_clocks(config)

        self.init_board()

        self.create_IO_bus()

        # @TODO: Set mem_mode

        self.attach_chip_IO()

        self.attach_disk_images(config.search_artifacts("DISK"))

    def init_board(self) -> None:
        config = self._config
        # Set Platform
        self.realview.connect_global_interrupt(self)
        # @TODO: Assumes VExpress_GEM5_Base platform
        self.mem_ranges = self.create_memory_ranges(config.memory.regions)
        # Set NUMA ids of memory ranges for DTB
        self.set_mem_range_numa_ids([r.numa_id for r in config.memory.regions])

    def create_IO_bus(self):
        config = self._config

        # self._pci_devices = []
        self._dma_ports = None if config.interconnect.is_classic() else []
        self._mem_ports = []

        # Configure IO Bus
        self.iobus = m5_IOXBar()
        self.iobus.badaddr_responder = m5_BadAddr()
        self.iobus.default = self.iobus.badaddr_responder.pio

        if config.interconnect.is_classic():
            # Configure MemBus and IO Bridge
            self.membus = m5_SystemXBar(width=64)

            self.iobridge = m5_Bridge(delay="50ns")

            self.membus.badaddr_responder = m5_BadAddr()
            self.membus.badaddr_responder.warn_access = "warn"
            self.membus.default = self.membus.badaddr_responder.pio

            self.iobridge.mem_side_port = self.iobus.cpu_side_ports
            self.iobridge.cpu_side_port = self.membus.mem_side_ports

    def get_IO_bus(self) -> m5_IOXBar:
        return self.iobus

    def get_MEM_bus(self) -> m5_SystemXBar | None:
        if self._config.interconnect.is_classic():
            return self.membus
        else:
            return None

    def get_DMA_ports(self) -> list:
        """
        Return a list of m5.objects.Port
        """
        return [] if self._dma_ports is None else self._dma_ports

    def attach_chip_IO(self):
        if self._config.interconnect.is_classic():
            self.realview.attachOnChipIO(bus=self.membus, bridge=self.iobridge)
        else:
            # self.realview.attachOnChipIO does the following:
            # - For self._mem_ports != None, fills self._mem_ports with on-chip memory ports,
            #    otherwise automatically connects  on-chip memory ports to given bus.
            # - For self._dma_ports != None,
            self.realview.attachOnChipIO(
                bus=self.iobus, dma_ports=self._dma_ports, mem_ports=self._mem_ports
            )

        self.realview.attachIO(bus=self.iobus, dma_ports=self._dma_ports)

    def attach_disk_images(self, disk_images: list[BinaryArtifact]):

        # Setup VirtIO disk images
        paths = [str(v.path) for v in disk_images]
        disks = [FileDiskImage(f) for f in paths]

        self.pci_vio_block = [
            m5_PciVirtIO(vio=m5_VirtIOBlock(image=img)) for img in disks
        ]

        for dev in self.pci_vio_block:
            self.realview.attachPciDevice(
                dev, self.get_IO_bus(), dma_ports=self._dma_ports
            )

    def assign_workload(self, work: AbstractWork) -> AbstractBoardSystem:

        self.workload = work

        self.realview.setupBootLoader(
            self, lambda name: work.get_bootloader(self.realview.get_version())
        )

        self.readfile = work.get_work_script()

        if (f := self.workload.get_dtb_file()) is not None:
            self.generateDtb(f)

        return self

    def set_mem_range_numa_ids(self, ids: list[int]) -> None:
        """ """
        if hasattr(self, "mem_range_numa_ids"):
            self.mem_range_numa_ids = ids

    def create_memory_ranges(
        self, regions: list[MemoryRegionConfig]
    ) -> list[m5_AddrRange]:
        # @TODO: Assumes VExpress_GEM5_Base platform
        sys_mem_region = self.realview._mem_regions[0]

        mem_ranges: list[m5_AddrRange] = []
        start = sys_mem_region.start
        for region in regions:
            size = int(m5_Addr(region.size))
            mem_ranges.append(m5_AddrRange(start, size=size))
            start = start + size

        return mem_ranges

    def connect_processor(self, processor: AbstractProcessor) -> AbstractBoardSystem:
        config = self._config

        self.cpus = processor

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

        ic.connect_IO_bus(self.get_IO_bus())

        ic.connect_MEM_bus(self.get_MEM_bus())

        ic.connect_board_port(self.system_port)

        # Connect CPUs
        ic.connect_cpu_nodes(self.get_board_procesor())

        # Define HNF ranges
        hnf_ranges = [[r] for r in self.get_mem_ranges()]

        # @TODO: Let connect_rom_nodes handle board memories entirely
        for m in self.get_board_memories():
            hnf_ranges[0].append(m.range)

        # Connect HNFs
        ic.connect_slc_nodes(hnf_ranges)

        # Connect Mem
        ic.connect_mem_nodes(self.mem_ctrls)

        ic.connect_rom_nodes(self.get_board_memories())

        ic.connect_dma_nodes(self.get_DMA_ports())

        ic.connect_network()

        ic.set_downstream()

        return self

    def get_board_procesor(self) -> AbstractProcessor:
        return self.cpus

    def get_board_memories(self) -> list[m5_SimpleMemory]:
        bootmem = self.realview.get_bootmem()
        on_chip_mem_ports = getattr(self, "_on_chip_mem_ports", None)
        sram = getattr(self, "sram", None)

        # other memories
        other_memories: list[m5_SimpleMemory] = []
        if bootmem:
            other_memories.append(bootmem)
        if sram:
            other_memories.append(sram)
        if on_chip_mem_ports:
            other_memories.extend([p.simobj for p in on_chip_mem_ports])

        return other_memories

    def get_mem_ranges(self) -> list[m5_AddrRange]:
        return self.mem_ranges

    def create_system_clocks(self, config: Config):
        self.voltage_domain = m5_VoltageDomain(voltage=config.system.voltage)
        self.clk_domain = m5_SrcClockDomain(
            clock=config.system.clock, voltage_domain=self.voltage_domain
        )

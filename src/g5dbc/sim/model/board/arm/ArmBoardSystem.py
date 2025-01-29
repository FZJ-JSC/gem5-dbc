from pathlib import Path

from g5dbc.config import Config
from g5dbc.config.memory import MemoryRegionConfig
from g5dbc.sim.m5_objects import m5_Addr, m5_AddrRange
from g5dbc.sim.m5_objects.arch import m5_ArmFsLinux, m5_ArmSystem
from g5dbc.sim.m5_objects.dev import m5_PciVirtIO, m5_VirtIOBlock
from g5dbc.sim.m5_objects.io import m5_BadAddr, m5_Bridge, m5_IOXBar, m5_SystemXBar
from g5dbc.sim.m5_objects.mem import m5_SimpleMemory
from g5dbc.sim.model.cpu import AbstractProcessor
from g5dbc.sim.model.interconnect import CoherentInterconnect
from g5dbc.sim.model.memory import AbstractMemSystem
from g5dbc.sim.model.storage import FileDiskImage

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

        self.attach_disk_images()

        self.attach_pci_devices()

        self.configure_system_boot()

    def init_board(self) -> None:
        config = self._config

        # Set Platform
        self.realview.connect_global_interrupt(self)

        self._bootmem: list[m5_SimpleMemory] = self.realview.get_bootmem()

        # @TODO: Assumes VExpress_GEM5_Base platform
        self.mem_ranges = self.create_memory_ranges(config.memory.regions)
        # Set NUMA ids of memory ranges for DTB
        self.set_mem_range_numa_ids([r.numa_id for r in config.memory.regions])

    def create_IO_bus(self):
        config = self._config

        self._pci_devices = []
        self._dma_ports = [] if not config.system.is_classic() else None
        self._mem_ports = []

        # Configure IO Bus
        self.iobus = m5_IOXBar()
        self.iobus.badaddr_responder = m5_BadAddr()
        self.iobus.default = self.iobus.badaddr_responder.pio

        if config.system.is_classic():
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
        if self._config.system.is_classic():
            return self.membus
        else:
            return None

    def get_DMA_ports(self) -> list:
        """
        Return a list of m5.objects.Port
        """
        return self._dma_ports

    def attach_chip_IO(self):
        if self._config.system.is_classic():
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

    def attach_disk_images(self):
        config = self._config

        # Setup VirtIO disk images
        disk_images = config.search_artifact("DISK")
        paths = [str(v.path) for k, v in disk_images.items()]
        disks = [FileDiskImage(f) for f in paths]

        self.pci_vio_block = [
            m5_PciVirtIO(vio=m5_VirtIOBlock(image=img)) for img in disks
        ]

        for dev in self.pci_vio_block:
            self._pci_devices.append(dev)

    def attach_pci_devices(self):
        for dev in self._pci_devices:
            self.realview.attachPciDevice(
                dev, self.get_IO_bus(), dma_ports=self.get_DMA_ports()
            )

    def configure_system_boot(self):
        config = self._config

        output_dir = Path(config.simulation.output_dir)
        kernels = config.search_artifact("KERNEL")
        bootloaders = config.search_artifact("BOOT")
        disk_images = config.search_artifact("DISK")
        bootloader_path = [
            v.path
            for k, v in bootloaders.items()
            if v.metadata == config.system.platform
        ]
        root_partition = [v.metadata for k, v in disk_images.items()]

        if not kernels:
            raise ValueError(f"Kernel list empty")
        if not bootloader_path:
            raise ValueError(f"Bootloader list empty")
        if not root_partition:
            raise ValueError(f"Disk image list empty")

        # Assume first disk in list to be root disk
        kernel_metadata = kernels["vmlinux"].metadata
        self.workload = m5_ArmFsLinux(
            output_dir=str(output_dir),
            command_line=f"{kernel_metadata} root={root_partition[0]}",
            kernel_path=str(kernels["vmlinux"].path),
        )

        # Use first bootloader in list
        self.realview.setupBootLoader(self, lambda name: str(bootloader_path[0]))

        self.readfile = str(output_dir.joinpath(config.simulation.work_script))

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
        if f"{mem_mode}" == "atomic" and not config.system.is_classic():
            mem_mode = "atomic_noncaching"

        self.mem_mode = mem_mode

        return self

    def connect_memory(self, mem_ctrls: AbstractMemSystem) -> AbstractBoardSystem:
        self.mem_ctrls = mem_ctrls

        # Set memory ranges
        self.mem_ctrls.set_memory_ranges(self.mem_ranges)

        return self

    def connect_interconnect(
        self, interconnect: CoherentInterconnect
    ) -> AbstractBoardSystem:
        config = self._config

        self.interconnect = interconnect

        interconnect.connect_IO_bus(self.get_IO_bus())

        interconnect.connect_MEM_bus(self.get_MEM_bus())

        interconnect.connect_board_port(self.system_port)

        # Connect CPUs
        interconnect.connect_cpu_nodes(self.get_board_procesor())

        # Define HNF ranges
        hnf_ranges = [[r] for r in self.get_mem_ranges()]

        # @TODO: Let connect_rom_nodes handle board memories entirely
        for m in self.get_board_memories():
            hnf_ranges[0].append(m.range)

        # Connect HNFs
        interconnect.connect_slc_nodes(hnf_ranges)

        # Connect Mem
        interconnect.connect_mem_nodes(self.mem_ctrls)

        interconnect.connect_rom_nodes(self.get_board_memories())

        interconnect.connect_dma_nodes(self.get_DMA_ports())

        interconnect.connect_network()

        interconnect.set_downstream()

        return self

    def get_board_procesor(self) -> AbstractProcessor:
        return self.cpus

    def get_board_memories(self) -> list[m5_SimpleMemory]:

        bootmem = self.realview.get_bootmem()

        # other memories
        other_memories: list[m5_SimpleMemory] = []
        if bootmem:
            other_memories.append(bootmem)
        if getattr(self, "sram", None):
            other_memories.append(getattr(self, "sram", None))
        on_chip_mem_ports = getattr(self, "_on_chip_mem_ports", None)
        if on_chip_mem_ports:
            other_memories.extend([p.simobj for p in on_chip_mem_ports])

        return other_memories

    def get_mem_ranges(self) -> list[m5_AddrRange]:
        return self.mem_ranges

    # @TODO: DTB only needed for Arm systems
    def generate_dtb(self) -> None:
        filename = self.workload.dtb_filename
        self.generateDtb(filename)

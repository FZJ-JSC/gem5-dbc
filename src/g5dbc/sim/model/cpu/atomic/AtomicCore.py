from g5dbc.sim.m5_objects.cpu import m5_AtomicSimpleCPU

from ..AbstractCore import AbstractCore


class AtomicCore(m5_AtomicSimpleCPU, AbstractCore):

    def __init__(self, core_id: int = 0):
        super().__init__(cpu_id=core_id)

        self._core_id = core_id

    def get_core_id(self) -> int:
        return self._core_id

    def get_mem_mode(self) -> str:
        return self.memory_mode()

    def create_threads(self) -> None:
        self.createThreads()

    def connect_interrupt(self) -> None:
        self.createInterruptController()

    def connect_icache(self, port) -> None:
        self.icache_port = port  # sequencer.in_ports

    def connect_dcache(self, port) -> None:
        self.dcache_port = port  # sequencer.in_ports

    def connect_walker_ports(self, port1, port2) -> None:
        self.mmu.dtb_walker.port = port1
        self.mmu.itb_walker.port = port2

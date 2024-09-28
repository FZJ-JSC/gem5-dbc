from g5dbc.sim.m5_objects.cpu import m5_AtomicSimpleCPU
from g5dbc.sim.m5_objects.ruby import Sequencer

from ..AbstractCore import AbstractCore

class AtomicCore(m5_AtomicSimpleCPU, AbstractCore):

    def __init__(self, cpu_id: int = 0):

        super().__init__(
            cpu_id=cpu_id
        )

    def create_threads(self) -> None:
        self.createThreads()

    def connect_interrupt(self) -> None:
        self.createInterruptController()
        
    def connect_icache(self, sequencer: Sequencer) -> None:
        self.icache_port = sequencer.in_ports

    def connect_dcache(self, sequencer: Sequencer) -> None:
        self.dcache_port = sequencer.in_ports

    def connect_walker_ports(self, port1, port2) -> None:
        self.mmu.dtb_walker.port = port1.in_ports
        self.mmu.itb_walker.port = port2.in_ports

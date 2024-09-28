from abc import ABC, ABCMeta, abstractmethod
from g5dbc.sim.m5_objects import m5_ClockDomain
from g5dbc.sim.m5_objects.ruby import Sequencer

class AbstractCore:
    """
    Abstract Core
    """
    __metaclass__ = ABCMeta

    def set_active(self, active: bool) -> bool:
        self.switched_out = not active
        return active
    
    def set_clock_domain(self, clock: m5_ClockDomain) -> None:
        self.clk_domain = clock

    def set_numa_id(self, numa_id: int) -> int:
        #self.numa_id = numa_id
        return numa_id #self.numa_id.value

    def get_core_id(self) -> int:
        return self.cpu_id.value
    
    def get_mem_mode(self) -> str:
        return self.memory_mode()

    @abstractmethod
    def create_threads(self) -> None:
        """
        """

    @abstractmethod
    def connect_interrupt(self) -> None:
        """
        """

    @abstractmethod
    def connect_icache(self, sequencer: Sequencer) -> None:
        """
        """

    @abstractmethod
    def connect_dcache(self, sequencer: Sequencer) -> None:
        """
        """

    @abstractmethod
    def connect_walker_ports(self, port1, port2) -> None:
        """
        """

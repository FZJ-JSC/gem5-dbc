from abc import ABCMeta, abstractmethod

from g5dbc.sim.m5_objects import m5_AddrRange, m5_SrcClockDomain, m5_VoltageDomain
from g5dbc.sim.m5_objects.io import m5_IOXBar, m5_SystemXBar
from g5dbc.sim.m5_objects.mem import m5_SimpleMemory
from g5dbc.sim.m5_objects.sim import m5_SubSystem
from g5dbc.sim.model.cpu import AbstractProcessor
from g5dbc.sim.model.memory import AbstractMemSystem


class CoherentInterconnect(m5_SubSystem):

    __metaclass__ = ABCMeta

    def __init__(self) -> None:
        super().__init__()

    def configure_system_clocks(self, clock: str):
        # Create a voltage domain
        self.voltage_domain = m5_VoltageDomain()
        # Create a source clock
        self.clk_domain = m5_SrcClockDomain(
            clock=clock, voltage_domain=self.voltage_domain
        )

    @abstractmethod
    def connect_IO_bus(self, iobus: m5_IOXBar) -> None:
        """
        Connect IO bus
        """

    @abstractmethod
    def connect_MEM_bus(self, membus: m5_SystemXBar) -> None:
        """
        Connect MEM bus
        """

    @abstractmethod
    def connect_board_port(self, system_port):
        """
        Connect system port
        """

    @abstractmethod
    def connect_cpu_nodes(self, processor: AbstractProcessor) -> None:
        """
        Connect CPU cores to corresponding interconnect controller
        """

    @abstractmethod
    def connect_slc_nodes(self, slc_ranges: list[list[m5_AddrRange]]) -> None:
        """
        Connect SLC nodes to corresponding interconnect controller
        """

    @abstractmethod
    def connect_mem_nodes(self, mem_sys: AbstractMemSystem) -> None:
        """
        Connect Memory controllers to corresponding interconnect controller
        """

    @abstractmethod
    def connect_rom_nodes(self, mems: list[m5_SimpleMemory]):
        """
        Connect ROM memory to corresponding interconnect controller
        """

    @abstractmethod
    def connect_dma_nodes(self, ports: list):
        """
        Connect DMA memory to corresponding interconnect controller
        """

    @abstractmethod
    def connect_network(self):
        """
        Connect Network
        """

    @abstractmethod
    def set_downstream(self):
        """
        Connect controllers downstream
        """

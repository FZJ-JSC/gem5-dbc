from __future__ import annotations
from abc import ABCMeta, abstractmethod

from g5dbc.sim.m5_objects import m5_AddrRange, m5_SrcClockDomain, m5_VoltageDomain
from g5dbc.sim.m5_objects.io import m5_Bridge, m5_BadAddr, m5_SystemXBar, m5_IOXBar
from g5dbc.sim.m5_objects.mem import m5_SimpleMemory
from g5dbc.sim.m5_objects.ruby import Sequencer

from g5dbc.config import Config

from g5dbc.sim.model.cpu import AbstractProcessor
from g5dbc.sim.model.cpu.AbstractCore import AbstractCore

from g5dbc.sim.model.memory import AbstractMemSystem
from g5dbc.sim.model.interconnect import CoherentInterconnect


class AbstractBoardSystem:
    """
    Abstract System Board
    """
    __metaclass__ = ABCMeta


    @abstractmethod
    def get_board_memories(self) -> list[m5_SimpleMemory]:
        """
        """

    @abstractmethod
    def connect_processor(self, processor: AbstractProcessor) -> AbstractBoardSystem:
        """
        """

    @abstractmethod
    def connect_memory(self, memory: AbstractMemSystem) -> AbstractBoardSystem:
        """
        """

    @abstractmethod
    def connect_interconnect(self, interconnect: CoherentInterconnect) -> AbstractBoardSystem:
        """
        """

    @abstractmethod
    def get_board_procesor(self) -> AbstractProcessor:
        """        
        """

    @abstractmethod
    def get_mem_ranges(self) -> list[m5_AddrRange]:
        """
        """

    @abstractmethod
    def get_dma_ports(self) -> list:
        """
        """

    def set_mem_mode(self, mem_mode) -> None:
        self.mem_mode = mem_mode

    def set_mem_range_numa_ids(self, ids: list[int]) -> None:
        """
        """
        #self.mem_range_numa_ids = ids

    @abstractmethod
    def connect_ruby_sequencer(self, sequencer: Sequencer) -> None:
        """
        """

    @abstractmethod
    def connect_mem_side_ports(self, port) -> None:
        """
        """

    def switch_cpus(self) -> list[tuple[AbstractCore,AbstractCore]]:
        processor = self.get_board_procesor()
        return processor.switch_next()

    #@TODO: DTB only needed for Arm systems
    @abstractmethod
    def generate_dtb(self) -> None:
        ...

    def create_system_clocks(self, config: Config):
        self.voltage_domain = m5_VoltageDomain(
            voltage=config.system.voltage
        )
        self.clk_domain = m5_SrcClockDomain(
            clock=config.system.clock,
            voltage_domain=self.voltage_domain
        )

    def create_IO_bus(self, config: Config):
        if config.system.activeNOC():
            # Configure IO Bus
            self.iobus = m5_IOXBar()
            self.iobus.badaddr_responder = m5_BadAddr()
            self.iobus.default = self.iobus.badaddr_responder.pio
        else:
            # Configure MemBus and IO Bridge
            self.iobridge = m5_Bridge(delay='50ns')

            self.membus = m5_SystemXBar(width=64)
            self.membus.badaddr_responder = m5_BadAddr()
            self.membus.badaddr_responder.warn_access = "warn"
            self.membus.default = self.membus.badaddr_responder.pio

            self.iobridge.mem_side_port = self.iobus.cpu_side_ports
            self.iobridge.cpu_side_port = self.membus.mem_side_ports

from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod

from g5dbc.sim.m5_objects import m5_AddrRange

from ..Sequencer import Sequencer


class AbstractController:
    """Abstract Ruby Controller"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def connect_network(self, network) -> None:
        """Connect Controller to Network

        Args:
            network: Network to connect
        """

    @abstractmethod
    def connect_sequencer(self, sequencer: Sequencer, dcache: bool) -> None:
        """Connect Sequencer

        Args:
            sequencer (Sequencer): Sequencer instance to connect
            dcache (bool): True if sequencer connected to data cache
        """

    @abstractmethod
    def set_addr_ranges(self, addr_ranges: list[m5_AddrRange]) -> None:
        """Set Address Ranges

        Args:
            addr_ranges (list[m5_AddrRange]): _description_
        """

    @abstractmethod
    def set_downstream(self, cntrls: list[AbstractController]) -> None:
        """Set Downstream Controllers

        Args:
            cntrls (list[AbstractController]): List of controllers
        """

    def attach_memory_ctrl(self, mem_ctrl) -> None:
        """Attach memory controller

        Args:
            mem_ctrl: Memory controller to attach
        """
        self.memory_out_port = mem_ctrl.port

    def set_clock_domain(self, clk_domain) -> None:
        """Set clock domain for controller

        Args:
            clk_domain: Clock domain
        """
        self.clk_domain = clk_domain

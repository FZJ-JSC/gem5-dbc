from __future__ import annotations

from abc import ABCMeta, abstractmethod

from g5dbc.sim.m5_objects import m5_AddrRange

from ..Sequencer import Sequencer


class AbstractController:
    """
    Abstract Ruby Controller
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def connect_network(self, network) -> None:
        """
        Connect Controller to Network
        """

    @abstractmethod
    def connect_sequencer(self, sequencer: Sequencer, dcache: bool) -> None:
        """
        Connect Sequencer
        """

    @abstractmethod
    def set_addr_ranges(self, addr_ranges: list[m5_AddrRange]) -> None:
        """
        Set Address Ranges
        """

    @abstractmethod
    def set_downstream(self, cntrls: list[AbstractController]) -> None:
        """
        Set Downstream Controllers
        """

    def set_clock_domain(self, clk_domain) -> None:
        self.clk_domain = clk_domain

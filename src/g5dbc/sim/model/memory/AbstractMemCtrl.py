from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod

from g5dbc.sim.m5_objects import m5_AddrRange


class AbstractMemCtrl:
    """
    Abstract Memory Controller
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_ctrl_id(self) -> int:
        """
        Return controller id
        """

    @abstractmethod
    def get_numa_id(self) -> int:
        """
        Return memory numa id
        """

    @abstractmethod
    def connect_memory_port(self, memory_out_port) -> None:
        """
        Connects to memory controller port
        """

    @abstractmethod
    def get_addr_ranges(self) -> list[m5_AddrRange]:
        """
        Gets addres range from memory controller
        """

    @abstractmethod
    def set_addr_range(self, addr_range: m5_AddrRange) -> None:
        """
        Sets addres range for memory controller
        """

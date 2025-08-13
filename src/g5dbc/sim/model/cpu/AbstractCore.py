from abc import ABC, ABCMeta, abstractmethod

from g5dbc.sim.m5_objects import m5_ClockDomain


class AbstractCore:
    """Abstract Core"""

    __metaclass__ = ABCMeta

    def set_active(self, active: bool) -> bool:
        """Set switched_out flag from active parameter

        Args:
            active (bool): True if active

        Returns:
            bool: True if active
        """
        self.switched_out = not active
        return active

    def set_clock_domain(self, clock: m5_ClockDomain) -> None:
        """Set clock domain

        Args:
            clock (m5_ClockDomain): Clock domain
        """
        self.clk_domain = clock

    def set_workload(self, workload) -> None:
        """Set workload for SE mode

        Args:
            workload: SE mode workload
        """
        self.workload = workload

    def set_numa_id(self, numa_id: int) -> int:
        """Set core NUMA id if supported

        Args:
            numa_id (int): NUMA id

        Returns:
            int: Returns configured NUMA id
        """
        _id = 0
        if hasattr(self, "numa_id"):
            self.numa_id = numa_id
            _id = numa_id
        return _id

    @abstractmethod
    def get_core_id(self) -> int:
        """Return core id

        Returns:
            int: Core id
        """

    @abstractmethod
    def get_mem_mode(self) -> str:
        """Return CPU model memory mode

        Returns:
            str: CPU model memory mode
        """

    @abstractmethod
    def create_threads(self) -> None:
        """Create CPU threads"""

    @abstractmethod
    def connect_interrupt(self) -> None:
        """Create interrupt controller"""

    @abstractmethod
    def connect_icache(self, port) -> None:
        """Connect icache port"""

    @abstractmethod
    def connect_dcache(self, port) -> None:
        """Connect dcache port"""

    @abstractmethod
    def connect_walker_ports(self, port1, port2) -> None:
        """Connect MMU walker ports"""

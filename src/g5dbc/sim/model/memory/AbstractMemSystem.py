from abc import ABCMeta, abstractmethod

from g5dbc.sim.m5_objects import m5_AddrRange
from g5dbc.sim.m5_objects.sim import m5_SubSystem

from .AbstractMemCtrl import AbstractMemCtrl
from .MultiChannelMem import MultiChannelMem


class AbstractMemSystem(m5_SubSystem):
    __metaclass__ = ABCMeta

    def __init__(self, mem_channels: list[MultiChannelMem]) -> None:
        super().__init__()

        self._num_regions = len(mem_channels)

        self._mem_channels = mem_channels

        for numa_id, mem in enumerate(mem_channels):
            setattr(self, f"mem_node{numa_id}_ctrl", mem.controllers())

    def get_mem_ctrls(self, numa_id: int = 0) -> list[AbstractMemCtrl]:
        """
        Return memory controllers
        """
        return self._mem_channels[numa_id].controllers()

    def get_mem_ctrl(self, numa_id: int, ctrl_id: int) -> AbstractMemCtrl:
        """
        Return memory controller
        """
        return self._mem_channels[numa_id].get_ctrl(ctrl_id)

    def set_memory_ranges(self, ranges: list[m5_AddrRange]) -> None:
        """
        Set memory ranges
        """
        assert len(ranges) == self._num_regions

        for idx, m in enumerate(self._mem_channels):
            m.set_memory_range(ranges[idx])

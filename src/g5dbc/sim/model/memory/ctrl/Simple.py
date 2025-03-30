from g5dbc.config.memory import MemoryRegionConfig
from g5dbc.sim.m5_objects import m5_AddrRange
from g5dbc.sim.m5_objects.mem import m5_SimpleMemory

from ..AbstractMemCtrl import AbstractMemCtrl


class SimpleMainMemory(m5_SimpleMemory, AbstractMemCtrl):

    def __init__(self, config: MemoryRegionConfig, ctrl_id: int = 0):
        _attr = dict()
        for k, v in config.extra_parameters.items():
            if hasattr(m5_SimpleMemory, k):
                _attr[k] = v
        super().__init__(
            bandwidth=config.bandwidth,
            latency=config.latency,
            latency_var=config.latency_var,
            **_attr,
        )
        self._ctrl_id = ctrl_id
        self._numa_id = config.numa_id

    def get_ctrl_id(self) -> int:
        return self._ctrl_id

    def get_numa_id(self) -> int:
        return self._numa_id

    def set_addr_range(self, addr_range: m5_AddrRange) -> None:
        self.range = addr_range

    def connect_memory_port(self, memory_out_port) -> None:
        self.port = memory_out_port

    def get_addr_ranges(self) -> list[m5_AddrRange]:
        return [self.range]

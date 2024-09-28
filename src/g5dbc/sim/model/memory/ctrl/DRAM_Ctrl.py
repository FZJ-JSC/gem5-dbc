from g5dbc.config.memory import MemoryRegionConfig
from g5dbc.sim.m5_objects import m5_AddrRange
from g5dbc.sim.m5_objects.mem import m5_MemCtrl, m5_DRAMInterface
from ..AbstractMemCtrl import AbstractMemCtrl

class DRAM_Ctrl(m5_MemCtrl, AbstractMemCtrl):
    
    def __init__(self, config: MemoryRegionConfig, ctrl_id: int = 0):
        super().__init__()

        self._ctrl_id = ctrl_id
        self._numa_id = config.numa_id

    def get_ctrl_id(self) -> int:
        return self._ctrl_id

    def get_numa_id(self) -> int:
        return self._numa_id

    def set_dram_interface(self, dram: m5_DRAMInterface) -> None:
        self.dram = dram

    def set_addr_range(self, addr_range: m5_AddrRange) -> None:
        self.dram.range = addr_range

    def connect_memory_port(self, ctrl) -> None:
        self.port = ctrl.memory_out_port

    def get_addr_ranges(self) -> list[m5_AddrRange]:
        return [self.dram.range]

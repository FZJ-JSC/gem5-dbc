from dataclasses import dataclass, field
from enum import Enum

from .controller import MemCtrlConfig

class MemoryModel(Enum):
    Simple = 1
    DRAM   = 2

@dataclass
class MemoryRegionConfig:
    model: str = "Simple"
    size: str = "1GB"
    channels: int = 2

    bandwidth: str = "30GiB/s"
    latency: str = "30ns"
    latency_var: str = "0ns"
    
    addr_mapping : str|None = None
    intlv_size:   int = 64
    xor_low_bit:  int = 20

    numa_id: int = 0

    dram_settings: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        model = MemoryModel[self.model]
        self.model = model.name

    def isDRAM(self) -> bool:
        return self.model == "DRAM"

@dataclass
class MemoryConf:
    controller: MemCtrlConfig
    regions: list[MemoryRegionConfig] = field(default_factory=list)

    def __post_init__(self):
        self.controller = MemCtrlConfig(**self.controller)

        for n,v in enumerate(self.regions):
            if isinstance(v, dict):
                self.regions[n] = MemoryRegionConfig(**v)
                self.regions[n].numa_id = n

    def numa_regions(self) -> list[int]:
        return [n for n in range(len(self.regions))]

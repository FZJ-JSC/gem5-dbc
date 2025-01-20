from dataclasses import dataclass, field
from enum import Enum


class MemoryModel(Enum):
    Simple = 1
    DRAM = 2


@dataclass
class MemoryRegionConfig:
    model: str = "Simple"
    size: str = "1GB"
    channels: int = 2

    bandwidth: str = "30GiB/s"
    latency: str = "30ns"
    latency_var: str = "0ns"

    addr_mapping: str | None = None
    intlv_size: int = 64
    xor_low_bit: int = 20

    numa_id: int = 0

    dram_settings: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        model = MemoryModel[self.model]
        self.model = model.name

    def isDRAM(self) -> bool:
        return self.model == "DRAM"

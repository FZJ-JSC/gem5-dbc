from dataclasses import dataclass, field

from .controller import MemCtrlConfig
from .region import MemoryRegionConfig


@dataclass
class MemoryConf:
    controller: MemCtrlConfig = field(default_factory=MemCtrlConfig)
    regions: list[MemoryRegionConfig] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.controller, dict):
            self.controller = MemCtrlConfig(**self.controller)

        for n, v in enumerate(self.regions):
            if isinstance(v, dict):
                self.regions[n] = MemoryRegionConfig(**v)
                self.regions[n].numa_id = n

    def numa_regions(self) -> list[int]:
        return [n for n in range(len(self.regions))]

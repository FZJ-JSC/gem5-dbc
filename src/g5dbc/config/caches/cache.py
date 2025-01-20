from dataclasses import asdict, dataclass

from .classic import ClassicCacheConf
from .controller import CacheCtrlConf
from .latency import Latency
from .sequencer import Sequencer


@dataclass
class CacheConf:
    name: str
    size: str
    assoc: int
    latency: Latency
    controller: CacheCtrlConf | None = None
    classic: ClassicCacheConf | None = None
    sequencer: Sequencer | None = None
    system_shared: bool = False
    block_size_bits: int = 6
    resource_stalls: bool = False

    def is_icache(self) -> bool:
        return self.name == "L1I"

    def __post_init__(self):
        if isinstance(self.latency, dict):
            self.latency = Latency(**self.latency)
        if isinstance(self.controller, dict):
            self.controller = CacheCtrlConf(**self.controller)
        if isinstance(self.classic, dict):
            self.classic = ClassicCacheConf(**self.classic)
        if isinstance(self.sequencer, dict):
            self.sequencer = Sequencer(**self.sequencer)

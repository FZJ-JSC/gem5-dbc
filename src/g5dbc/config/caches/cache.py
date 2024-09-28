from dataclasses import dataclass, field, asdict

from .classic import Classic
from .sequencer import Sequencer
from .controller import CacheCtrlConfig
from .latency import Latency

@dataclass
class CacheConf:
    name: str
    size: str
    assoc: int
    latency: Latency
    controller: CacheCtrlConfig
    classic:    Classic|None = None
    sequencer:  Sequencer|None = None
    system_shared: bool = False
    block_size_bits : int = 6
    resource_stalls : bool = False

    def is_icache(self) -> bool:
        return self.name == "L1I"

    def __post_init__(self):
        if isinstance(self.latency, dict):
            self.latency    = Latency(**self.latency)
        if isinstance(self.controller, dict):
            self.controller    = CacheCtrlConfig(**self.controller)
        if isinstance(self.latency, dict):
            self.classic    = Classic(**self.classic)
        if isinstance(self.sequencer, dict):
            self.sequencer    = Sequencer(**self.sequencer)

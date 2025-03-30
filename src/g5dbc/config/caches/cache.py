from dataclasses import dataclass, field

from .classic import ClassicCacheConf
from .controller import CacheCtrlConf
from .latency import Latency
from .prefetcher import PrefetcherConf
from .sequencer import SequencerConf


@dataclass
class CacheConf:
    name: str
    size: str
    assoc: int
    latency: Latency
    controller: CacheCtrlConf = field(default_factory=CacheCtrlConf)
    classic: ClassicCacheConf = field(default_factory=ClassicCacheConf)
    sequencer: SequencerConf = field(default_factory=SequencerConf)
    prefetcher: PrefetcherConf | None = None
    system_shared: bool = False
    block_size_bits: int = 6
    resource_stalls: bool = False
    extra_parameters: dict = field(default_factory=dict)

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
            self.sequencer = SequencerConf(**self.sequencer)
        if isinstance(self.prefetcher, dict):
            self.prefetcher = PrefetcherConf(**self.prefetcher)

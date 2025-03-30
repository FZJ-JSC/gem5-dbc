from dataclasses import dataclass, field

from .bpred import BPredConf
from .core import CoreConfig, CoreFUDesc


@dataclass
class CPUConf:
    name: str
    model: str
    clock: str
    bpred: BPredConf | None = None
    core: CoreConfig | None = None
    FU: dict[str, CoreFUDesc] = field(default_factory=dict)
    extra_parameters: dict = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.bpred, dict):
            self.bpred = BPredConf(**self.bpred)

        if isinstance(self.core, dict):
            self.core = CoreConfig(**self.core)

        for k, v in self.FU.items():
            if isinstance(v, dict):
                self.FU[k] = CoreFUDesc(**v)

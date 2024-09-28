from dataclasses import dataclass, field, asdict

from .core import CoreConfig, CoreFUDesc

@dataclass
class CPUConf:
    name: str
    model: str
    clock: str
    bp: str|None = None
    core: CoreConfig|None = None
    FU: dict[str, CoreFUDesc] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.core, dict):
            self.core = CoreConfig(**self.core)
        
        for k,v in self.FU.items():
            if isinstance(v, dict):
                self.FU[k] = CoreFUDesc(**v)

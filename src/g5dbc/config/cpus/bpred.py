from dataclasses import asdict, dataclass, field


@dataclass
class BTBConf:
    numEntries: int = 4096
    tagBits: int = 16
    instShiftAmt: int = 2

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BPredConf:
    model: str
    BTB: BTBConf
    settings: dict = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.BTB, dict):
            self.BTB = BTBConf(**self.BTB)

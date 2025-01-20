from dataclasses import dataclass, field


@dataclass
class PrefetcherConf:
    name: str
    model: str
    settings: dict = field(default_factory=dict)

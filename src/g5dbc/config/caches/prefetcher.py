from dataclasses import dataclass, field


@dataclass
class PrefetcherConf:
    model: str = "None"
    settings: dict = field(default_factory=dict)

from dataclasses import dataclass

@dataclass
class PrefetcherConf:
    name: str
    model : str
    degree: int = 8


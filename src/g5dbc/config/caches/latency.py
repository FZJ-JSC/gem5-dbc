from dataclasses import dataclass

@dataclass
class Latency:
    tag: int
    data: int
    response: int = 1
from dataclasses import dataclass, field, asdict
from enum import Enum

class NodeType(Enum):
    CPU = 1
    SLC = 2
    MEM = 3
    ROM = 4
    DMA = 5

@dataclass
class NodeSpec:
    ctrl_id:   int = 0
    router_id: int = 0
    numa_id:   int = 0
    core_id:   int = 0
    needs_exclusive_router: bool = False
    def __lt__(self, next):
            return (self.numa_id,self.ctrl_id,self.core_id) < (next.numa_id,next.ctrl_id,next.core_id)

@dataclass
class RouterSpec:
    router_ids: list[int] = field(default_factory=list)
    numa_id: int = 0
    nodes_per_router: int = 0

    def num_ctrls(self) -> int:
         return self.nodes_per_router*len(self.router_ids)


@dataclass
class LinkSpec:
    src: int
    dst: int
    latency: int
    weight: int = 1
    def __str__(self):
         return f"link src={self.src} dst={self.dst} latency={self.latency} weight={self.weight}"

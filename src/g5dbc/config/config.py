from dataclasses import dataclass, field, asdict

from .artifacts import ArtifactList
from .caches import CacheConf
from .cpus import CPUConf
from .interconnect import InterconnectConf
from .memory import MemoryConf
from .network import NetworkConf
from .prefetcher import PrefetcherConf
from .simulation import SimulationConf
from .system import SystemConf

@dataclass
class Config:
    system:       SystemConf
    interconnect: InterconnectConf
    network:      NetworkConf
    memory:       MemoryConf
    simulation:   SimulationConf
    artifacts:    ArtifactList

    cpus:         dict[str, CPUConf]        = field(default_factory=dict)
    caches:       dict[str, CacheConf]      = field(default_factory=dict)
    prefetcher:   dict[str, PrefetcherConf] = field(default_factory=dict)

    parameters:   dict = field(default_factory=dict)

    def __post_init__(self):
        if self.network.clock == "":
            self.network.clock = self.system.clock

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, conf_dict: dict):
        config = cls(
            system=SystemConf(**conf_dict["system"]),
            memory=MemoryConf(**conf_dict["memory"]),
            network=NetworkConf(**conf_dict["network"]),
            interconnect=InterconnectConf(**conf_dict["interconnect"]),
            simulation=SimulationConf(**conf_dict["simulation"]),
            artifacts=ArtifactList(**conf_dict["artifacts"]),
            parameters=conf_dict.setdefault("parameters", dict())
        )

        for name, opts in conf_dict["cpus"].items():
            config.cpus[name] = CPUConf(**{**opts, 'name':name})

        for name, opts in conf_dict["caches"].items():
            config.caches[name] = CacheConf(**{**opts, 'name':name})

        for name, opts in conf_dict["prefetcher"].items():
            config.prefetcher[name] = PrefetcherConf(**{**opts, 'name':name})

        return config

from dataclasses import asdict, dataclass, field

from .artifacts import BinaryArtifact
from .bpred import BPredConf
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
    system: SystemConf
    interconnect: InterconnectConf
    network: NetworkConf
    memory: MemoryConf
    simulation: SimulationConf
    cpus: dict[str, CPUConf] = field(default_factory=dict)
    bpred: dict[str, BPredConf] = field(default_factory=dict)
    caches: dict[str, CacheConf] = field(default_factory=dict)
    prefetcher: dict[str, PrefetcherConf] = field(default_factory=dict)
    artifacts: dict[str, list[BinaryArtifact]] = field(default_factory=dict)
    parameters: dict = field(default_factory=dict)

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
        )

        for k, v in conf_dict["cpus"].items():
            config.cpus[k] = CPUConf(**{**v, "name": k})

        for k, v in conf_dict["bpred"].items():
            config.bpred[k] = BPredConf(**{**v, "name": k})

        for k, v in conf_dict["caches"].items():
            config.caches[k] = CacheConf(**{**v, "name": k})

        for k, v in conf_dict["prefetcher"].items():
            config.prefetcher[k] = PrefetcherConf(**{**v, "name": k})

        for k, v in conf_dict.get("artifacts", dict()).items():
            config.artifacts[k] = [BinaryArtifact(**a) for a in v]

        for k, v in conf_dict.get("parameters", dict()).items():
            config.parameters[k] = v

        return config

    def search_artifact(
        self, typename: str, version: str = ""
    ) -> dict[str, BinaryArtifact]:
        arch_name = self.system.architecture
        artifacts = self.artifacts[arch_name]

        _select = lambda x: x.bintype == typename and (
            x.version == version or version == ""
        )

        return dict([(a.name, a) for a in artifacts if _select(a)])

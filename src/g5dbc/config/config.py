from dataclasses import asdict, dataclass, field

from .artifacts import BinaryArtifact
from .caches import CacheConf
from .cpus import CPUConf
from .interconnect import InterconnectConf
from .memory import MemoryConf
from .network import NetworkConf
from .simulation import SimulationConf
from .system import SystemConf


@dataclass
class Config:
    simulation: SimulationConf
    system: SystemConf
    memory: MemoryConf
    interconnect: InterconnectConf
    network: NetworkConf
    cpus: dict[str, CPUConf] = field(default_factory=dict)
    caches: dict[str, CacheConf] = field(default_factory=dict)
    artifacts: dict[str, list[BinaryArtifact]] = field(default_factory=dict)
    parameters: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, conf_dict: dict):
        for k in ["simulation", "system", "cpus", "caches"]:
            assert k in conf_dict, f"Key {k} has not been be defined"

        config = cls(
            simulation=SimulationConf(**conf_dict["simulation"]),
            system=SystemConf(**conf_dict["system"]),
            memory=MemoryConf(**conf_dict.get("memory", dict())),
            interconnect=InterconnectConf(**conf_dict.get("interconnect", dict())),
            network=NetworkConf(**conf_dict.get("network", dict())),
        )

        for k, v in conf_dict["cpus"].items():
            config.cpus[k] = CPUConf(**{**v, "name": k})

        if not config.system.cpus:
            config.system.cpus = [*config.cpus]

        for k, v in conf_dict["caches"].items():
            config.caches[k] = CacheConf(**{**v, "name": k})

        for k, v in conf_dict.get("artifacts", dict()).items():
            config.artifacts[k] = [BinaryArtifact(**a) for a in v]

        for k, v in conf_dict.get("parameters", dict()).items():
            config.parameters[k] = v

        return config

    def search_artifact(
        self,
        typename: str,
        name: str = "",
        version: str = "",
    ) -> dict[str, BinaryArtifact]:
        arch_name = self.system.architecture
        artifacts = self.artifacts[arch_name]

        _select = lambda x: x.bintype == typename and (
            (x.version == version or version == "") and (x.name == name or name == "")
        )

        return dict([(a.name, a) for a in artifacts if _select(a)])

    def get_artifact(
        self,
        typename: str,
        name: str = "",
        version: str = "",
    ) -> BinaryArtifact | None:
        return next(
            iter(
                self.search_artifact(
                    typename=typename,
                    name=name,
                    version=version,
                ).values()
            ),
            None,
        )

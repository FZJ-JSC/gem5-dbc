from dataclasses import dataclass, field

from .classic import Classic
from .garnet import Garnet
from .simple import Simple


@dataclass
class InterconnectConf:
    model: str = "classic"
    classic: Classic = field(default_factory=Classic)
    garnet: Garnet = field(default_factory=Garnet)
    simple: Simple = field(default_factory=Simple)

    def __post_init__(self):
        if isinstance(self.classic, dict):
            self.classic = Classic(**self.classic)

        if isinstance(self.garnet, dict):
            self.garnet = Garnet(**self.garnet)

        if isinstance(self.simple, dict):
            self.simple = Simple(**self.simple)

    def is_classic(self) -> bool:
        return self.model == "classic"

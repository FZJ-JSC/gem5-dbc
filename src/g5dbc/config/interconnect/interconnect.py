from dataclasses import dataclass

from .classic import Classic
from .garnet import Garnet
from .simple import Simple


@dataclass
class InterconnectConf:
    classic: Classic
    garnet: Garnet
    simple: Simple

    def __post_init__(self):
        if isinstance(self.classic, dict):
            self.classic = Classic(**self.classic)

        if isinstance(self.garnet, dict):
            self.garnet = Garnet(**self.garnet)

        if isinstance(self.simple, dict):
            self.simple = Simple(**self.simple)

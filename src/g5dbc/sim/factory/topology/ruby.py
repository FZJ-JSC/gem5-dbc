from g5dbc.config import Config
from g5dbc.sim.model.topology.ruby import *


class RubyTopologyFactory:

    @staticmethod
    def create(config: Config) -> RubyTopology:
        match config.network.topology[config.system.topology].model:
            case "Simple2D":
                return Simple2D(config)
            case _:
                raise ValueError(f"Unknown Topology {config.system.topology}")

from g5dbc.config import Config
from g5dbc.sim.model.interconnect import CoherentInterconnect
from g5dbc.sim.model.interconnect.classic import ClassicInterconnect, ClassicSE
from g5dbc.sim.model.interconnect.ruby import RubyInterconnect


class InterconnectFactory:
    @staticmethod
    def create(config: Config) -> CoherentInterconnect:
        ic: CoherentInterconnect | None = None

        if config.simulation.full_system:
            match config.interconnect.model:
                case "garnet" | "simple":
                    ic = RubyInterconnect(config)
                case "classic":
                    ic = ClassicInterconnect(config)
                case _:
                    raise ValueError(
                        f"Interconnect model {config.interconnect.model} not available"
                    )
        else:
            match config.interconnect.model:
                case "classic":
                    ic = ClassicSE(config)
                case _:
                    raise ValueError(
                        f"Interconnect model {config.interconnect.model} not available for SE"
                    )

        return ic

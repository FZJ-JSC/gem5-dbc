from g5dbc.config import Config
from g5dbc.sim.m5_objects.sim import find_SEWorkload
from g5dbc.sim.model.work import AbstractWork
from g5dbc.sim.model.work.arm import ArmLinuxWorkload


class WorkloadFactory:
    @staticmethod
    def create(config: Config) -> AbstractWork:
        arch = config.system.architecture
        match arch:
            case "arm64":
                if config.simulation.full_system:
                    work = ArmLinuxWorkload(config=config)
                else:
                    se_binary = config.search_artifacts(
                        "EXEC", name=config.simulation.se_cmd[0]
                    )
                    if not se_binary:
                        raise ValueError(
                            f"Could not find SE binary {config.simulation.se_cmd[0]}."
                        )
                    work = find_SEWorkload(se_binary[0].path)

            case _:
                raise ValueError(f"Workload for architecture {arch} not available")
        return work

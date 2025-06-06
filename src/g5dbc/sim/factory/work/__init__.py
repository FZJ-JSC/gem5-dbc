from g5dbc.config import Config
from g5dbc.sim.model.work import AbstractWork
from g5dbc.sim.model.work.arm import ArmLinuxWorkload


class WorkloadFactory:
    @staticmethod
    def create(config: Config) -> AbstractWork:
        arch = config.system.architecture
        match arch:
            case "arm64":
                work = ArmLinuxWorkload(config=config)
            case _:
                raise ValueError(f"Workload for architecture {arch} not available")
        return work

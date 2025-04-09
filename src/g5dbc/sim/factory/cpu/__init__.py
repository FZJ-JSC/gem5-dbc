from g5dbc.config import Config
from g5dbc.config.cpus import CPUConf
from g5dbc.sim.model.cpu.AbstractCore import AbstractCore
from g5dbc.sim.model.cpu.AbstractProcessor import AbstractProcessor
from g5dbc.sim.model.cpu.atomic.AtomicCore import AtomicCore
from g5dbc.sim.model.cpu.o3cpu import Arm

from .bpred import BPredFactory


class CoreFactory:
    @staticmethod
    def create(cpu_conf: CPUConf, config: Config, cpu_id: int = 0) -> AbstractCore:
        core: AbstractCore | None = None
        match cpu_conf.model:
            case "Arm":
                core = Arm(cpu_id, cpu_conf, bp=BPredFactory.create(cpu_conf.bpred))
            case "AtomicSimple":
                core = AtomicCore(cpu_id)
            case _:
                raise ValueError(f"Platform model {cpu_conf.model} not available")
        return core


class ProcessorFactory:
    @staticmethod
    def create(config: Config) -> AbstractProcessor:
        num_cpus = config.system.num_cpus
        core_group = dict(
            (
                key,
                [
                    CoreFactory.create(cpu_conf, config, cpu_id)
                    for cpu_id in range(num_cpus)
                ],
            )
            for key, cpu_conf in config.cpus.items()
        )

        return AbstractProcessor(
            config=config,
            core_keys=config.system.cpus,
            core_group=core_group,
        )

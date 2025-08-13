from g5dbc.config import Config
from g5dbc.sim.model.cpu.AbstractCore import AbstractCore
from g5dbc.sim.model.cpu.AbstractProcessor import AbstractProcessor
from g5dbc.sim.model.cpu.atomic.AtomicCore import AtomicCore
from g5dbc.sim.model.cpu.o3cpu import Arm

from .bpred import BPredFactory


class CoreFactory:
    @staticmethod
    def create(config: Config, cpu_name: str, core_id: int = 0) -> AbstractCore:
        cpu_conf = config.cpus[cpu_name]
        match cpu_conf.model:
            case "Arm":
                core = Arm(
                    config=config,
                    cpu_name=cpu_name,
                    core_id=core_id,
                    bp=BPredFactory.create(cpu_conf.bpred),
                )
            case "AtomicSimple":
                core = AtomicCore(core_id=core_id)
            case _:
                raise ValueError(f"Platform model {cpu_conf.model} not available")
        return core


class ProcessorFactory:
    @staticmethod
    def create(config: Config) -> AbstractProcessor:
        num_cpus = config.system.num_cpus
        core_group = dict(
            (
                cpu_name,
                [
                    CoreFactory.create(config, cpu_name, core_id=core_id)
                    for core_id in range(num_cpus)
                ],
            )
            for cpu_name in config.cpus.keys()
        )

        return AbstractProcessor(
            config=config,
            core_keys=config.system.cpus,
            core_group=core_group,
        )

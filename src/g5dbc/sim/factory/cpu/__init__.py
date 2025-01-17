from g5dbc.config import Config
from g5dbc.config.cpus import CPUConf
from g5dbc.sim.model.cpu.AbstractProcessor import AbstractProcessor
from g5dbc.sim.model.cpu.arm.ArmCore import ArmCore
from g5dbc.sim.model.cpu.atomic.AtomicCore import AtomicCore

from ..pred import BPFactory


class CoreFactory:
    @staticmethod
    def create(config: Config, cpu_conf: CPUConf, cpu_id: int = 0) -> AbstractProcessor:
        core: AbstractProcessor | None = None
        match cpu_conf.model:
            case "Arm":
                core = ArmCore(cpu_conf, cpu_id)
                if cpu_conf.bp is not None:
                    bp_conf = config.branch_pred[cpu_conf.bp]
                    core.set_branchPred(BPFactory.create(bp_conf))
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
                    CoreFactory.create(config, cpu_conf, cpu_id)
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

from g5dbc.config import Config
from g5dbc.config.cpus import CPUConf
from g5dbc.sim.model.cpu.AbstractProcessor import AbstractProcessor
from g5dbc.sim.model.cpu.arm.ArmCore import ArmCore
from g5dbc.sim.model.cpu.atomic.AtomicCore import AtomicCore


class CoreFactory:
    @staticmethod
    def create(conf: CPUConf, cpu_id:int = 0) -> AbstractProcessor:
        match conf.model:
            case "Arm":
                return ArmCore(conf,cpu_id)
            case "AtomicSimple":
                return AtomicCore(cpu_id)
            case _:
                raise ValueError(f"Platform model {conf.model} not available")


class ProcessorFactory:
    @staticmethod
    def create(config: Config) -> AbstractProcessor:

        cpus     = config.cpus
        num_cpus = config.system.num_cpus
        core_group = dict( (key,[CoreFactory.create(conf,cpu_id) for cpu_id in range(num_cpus)]) for key,conf in cpus.items())

        p = AbstractProcessor(config=config, core_keys = config.system.cpus,  core_group=core_group)

        return p


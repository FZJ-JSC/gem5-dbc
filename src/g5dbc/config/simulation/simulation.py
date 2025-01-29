from dataclasses import dataclass


@dataclass
class SimulationConf:
    gem5_version: str
    output_dir: str = ""
    work_script: str = "work.sh"
    srun_script: str = "srun.sh"
    gem5_script: str = "srun.py"
    full_system: bool = True
    max_tick: int | None = None
    max_seconds: int | None = None
    disable_listeners: bool = True

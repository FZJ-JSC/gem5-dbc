from dataclasses import dataclass

@dataclass
class SimulationConf:
    output_dir: str = ""
    work_script: str = "work.sh"
    launch_script: str = "srun.sh"
    full_system: bool = True
    max_tick: int|None = None
    max_seconds: int|None = None
    disable_listeners: bool = True



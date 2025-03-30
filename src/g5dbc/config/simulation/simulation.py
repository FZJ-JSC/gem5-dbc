from dataclasses import dataclass


@dataclass
class SimulationConf:
    gem5_version: str = ""
    gem5_binary: str = ""
    linux_version: str = ""
    linux_binary: str = "vmlinux"
    bootloader_binary: str = "boot.arm64"
    output_dir: str = ""
    work_script: str = "work.sh"
    srun_script: str = "srun.sh"
    gem5_script: str = "srun.py"
    output_log: str | None = "output.log"
    full_system: bool = True
    max_tick: int | None = None
    max_seconds: int | None = None
    disable_listeners: bool = True

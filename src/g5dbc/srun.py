from pathlib import Path

from .manager import read_config_file
from .sim.m5_objects import m5_outdir
from .sim import simulate

def srun(config_file = "config.yaml"):
    output_dir = Path(m5_outdir()).resolve()
    simulate(read_config_file(output_dir.joinpath(config_file)))
    return 0

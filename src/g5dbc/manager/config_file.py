from pathlib import Path

from .options import Options
from ..util import yaml_dict
from ..config import Config


def read_config_file(opts: Options) -> Config:
    """
    Read config file

    Args:
        opts (Options): _description_

    Returns:
        Config: _description_
    """
    conf_dict = yaml_dict.load(opts.benchmark_cfg)

    if "artifacts" not in conf_dict:
        conf_dict["artifacts"] = dict(
            arch=yaml_dict.load(opts.artifacts),
            path=str(opts.artifacts.parent)
        )
    return Config.from_dict(conf_dict)

def write_config_file(config_file: Path, config: Config) -> Path:
    yaml_dict.write(config_file, config.to_dict())

    return config_file

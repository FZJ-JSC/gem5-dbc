from pathlib import Path

from ..config import Config
from ..util import yaml_dict


def read_config_file(config_file: Path, artifacts: dict | None = None) -> Config:
    config_dict = yaml_dict.load(config_file)
    if artifacts is not None:
        config_dict["artifacts"] = artifacts
    return Config.from_dict(config_dict)


def write_config_file(config_file: Path, config: Config) -> Path:
    yaml_dict.write(config_file, config.to_dict())
    return config_file

from pathlib import Path

from ..config import Config
from ..util import dict_yaml


def read_config_file(config_file: Path, **kwargs) -> Config:
    config_dict = dict_yaml.read(config_file)
    for k, v in kwargs.items():
        config_dict[k] = v
    return Config.from_dict(config_dict)


def write_config_file(config_file: Path, config: Config) -> Path:
    dict_yaml.write(config_file, config.to_dict())
    return config_file

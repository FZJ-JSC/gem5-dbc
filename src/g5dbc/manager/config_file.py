from pathlib import Path

from ..config import Config
from ..util import yaml_dict


def read_artifacts(sd: list[Path], key_name="artifacts") -> dict[str, str]:
    artifacts = dict()
    key_file = f"{key_name}.yaml"
    # Load artifact files from all known places, merge all
    files = [d.joinpath(key_file) for d in sd if d.joinpath(key_file).exists()]
    for f in files:
        l = yaml_dict.load(f)
        p = f.resolve().parent
        for arch, items in l.items():
            arch_items: list = artifacts.setdefault(arch, [])
            for i in items:
                if "path" in i and not Path(i["path"]).is_absolute():
                    i["path"] = str(p.joinpath(i["path"]))
            arch_items.extend(items)
    return artifacts


def read_config_file(config_file: Path, sd: list[Path] = [], key="artifacts") -> Config:
    config_dict = yaml_dict.load(config_file)
    if sd and key not in config_dict:
        artifacts = config_dict.setdefault(key, dict())
        for k, v in read_artifacts(sd).items():
            artifacts[k] = v
    return Config.from_dict(config_dict)


def write_config_file(config_file: Path, config: Config) -> Path:
    yaml_dict.write(config_file, config.to_dict())
    return config_file

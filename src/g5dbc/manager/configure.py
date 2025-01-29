import re
import subprocess
from pathlib import Path

from ..util import yaml_dict
from ..util.hash import md5sum
from .options import Options


def configure_gem5_binary(path: Path) -> tuple[str, list[dict[str, str]]]:

    if not path.is_file():
        raise SystemExit(f"gem5 binary path does not exist: {path}")

    outp = subprocess.run([str(path), "-B"], capture_output=True)
    outl = outp.stdout.decode().splitlines()

    gem5_meta = None
    gem5_arch = None
    gem5_ver = None

    r_meta = r"compiled (.+)"
    r_arch = r"USE_(\w+)_ISA = True"
    r_ver = r"gem5 version ([\w\.-]+)"
    for l in outl:
        if m := re.fullmatch(r_meta, l.strip()):
            gem5_meta = m[1]
            continue
        if m := re.fullmatch(r_ver, l.strip()):
            gem5_ver = m[1]
            continue

        if m := re.fullmatch(r_arch, l.strip()):
            match m[1]:
                case "ARM":
                    gem5_arch = "arm64"
                case _:
                    pass
            continue

    if gem5_arch is None:
        raise SystemExit(f"Could not determine gem5 isa: {path}")

    config = [
        dict(
            name=path.name,
            path=str(path.absolute()),
            md5hash=md5sum(path),
            version=gem5_ver,
            bintype="GEM5",
            metadata=gem5_meta,
        )
    ]

    return gem5_arch, config


def update_user_config(opts: Options):
    # Create user conf directory if it does not already exist
    opts.user_conf_dir.mkdir(parents=True, exist_ok=True)
    config_file = opts.user_conf_dir.joinpath("artifacts.yaml")
    config: dict[str, list[dict[str, str]]] = dict()

    match opts.configure[0]:
        case "GEM5":
            arch, items = configure_gem5_binary(Path(opts.configure[1]))
            arch_objs = config.setdefault(arch, [])
            arch_objs.extend(items)
        case _:
            pass

    if config_file.exists():
        prev_config: dict[str, list[dict[str, str]]] = yaml_dict.load(config_file)
        for arch, items in prev_config.items():
            if arch in config:
                _cksum = [o["md5hash"] for o in config[arch]]
                _items = [item for item in items if item["md5hash"] not in _cksum]
                config[arch].extend(_items)
            else:
                config[arch] = items
    if config:
        yaml_dict.write(config_file, config)

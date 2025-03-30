import re
import subprocess
from pathlib import Path

from ...util.hash import md5sum


def get_resource_simulator(path: Path) -> tuple[str, dict[str, str]]:

    if not path.is_file():
        raise SystemExit(f"gem5 binary path does not exist: {path}")

    arch = None

    _name = path.name
    _path = str(path.absolute())
    _hash = md5sum(path)
    _ver = None
    _meta = None

    outp = subprocess.run([str(path), "-B"], capture_output=True)
    outl = outp.stdout.decode().splitlines()

    r_meta = r"compiled (.+)"
    r_arch = r"USE_(\w+)_ISA = True"
    r_ver = r"gem5 version ([\w\.-]+)"
    for l in outl:
        if m := re.fullmatch(r_meta, l.strip()):
            _meta = m[1]
            continue
        if m := re.fullmatch(r_ver, l.strip()):
            _ver = m[1]
            continue

        if m := re.fullmatch(r_arch, l.strip()):
            match m[1]:
                case "ARM":
                    arch = "arm64"
                case _:
                    arch = m[1]
            continue

    if arch is None:
        raise SystemExit(f"Could not determine gem5 isa: {path}")

    entry = dict(
        bintype="GEM5",
        name=_name,
        path=_path,
        md5hash=_hash,
        version=_ver,
        metadata=_meta,
    )

    return arch, entry

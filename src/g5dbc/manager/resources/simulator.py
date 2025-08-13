import re
import subprocess
from pathlib import Path

from ..options import Options


def add_simulator(opts: Options) -> tuple[str, dict[str, str]]:

    resource_path = Path(opts.resource_add).resolve()
    md5hash = opts.resource_hash

    arch = None
    ver = ""
    meta = ""

    outp = subprocess.run([str(resource_path), "-B"], capture_output=True)
    outl = outp.stdout.decode().splitlines()

    r_arch = r"USE_(\w+)_ISA = True"
    r_ver = r"gem5 version ([\w\.-]+)"
    r_meta = r"compiled (.+)"
    for l in outl:
        if m := re.fullmatch(r_meta, l.strip()):
            meta = m[1]
            continue
        if m := re.fullmatch(r_ver, l.strip()):
            ver = m[1]
            continue
        if m := re.fullmatch(r_arch, l.strip()):
            match m[1]:
                case "ARM":
                    arch = "arm64"
                case _:
                    arch = m[1]
            continue

    if arch is None:
        raise SystemExit(f"Could not determine gem5 isa: {resource_path}")

    entry: dict[str, str] = dict(
        bintype="GEM5",
        name=resource_path.name,
        path=str(resource_path),
        md5hash=md5hash,
        version=ver,
        metadata=meta,
    )

    return arch, entry

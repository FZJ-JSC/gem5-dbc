import re
from pathlib import Path

from ...util.hash import md5sum
from ..artifact_db import artifact_db_add, artifact_db_delete
from ..options import Options
from .simulator import get_resource_simulator


def get_default_resource(
    path: Path,
    _type: str,
    arch: str | None = None,
    version: str | None = None,
    metadata: str | None = None,
) -> tuple[str, dict[str, str]]:

    if not path.is_file():
        raise SystemExit(f"Artifact path does not exist: {path}")

    if _type not in ["KERNEL", "DISK", "BOOT"]:
        raise SystemExit(f"Artifact type {_type} invalid.")

    if arch is None:
        raise SystemExit(f"Artifact architecture unknown")

    _name = path.name
    _path = str(path.absolute())
    _hash = md5sum(path)
    _ver = version if version is not None else ""
    _meta = metadata if metadata is not None else ""

    # Try to get version from name
    r_name = r"([\w\.]+)-([\w\.-]+)"
    if m := re.fullmatch(r_name, path.name):
        _name = m[1]
        _ver = m[2]

    entry = dict(
        bintype=_type,
        name=_name,
        path=_path,
        md5hash=_hash,
        version=_ver,
        metadata=_meta,
    )

    return arch, entry


def configure_resources(cmd: str, opts: Options):
    # Create user conf directory if it does not already exist
    opts.user_conf_dir.mkdir(parents=True, exist_ok=True)
    index_file = opts.user_conf_dir.joinpath("artifacts.yaml")

    match cmd:
        case "add":
            _type = opts.resource_add[0]
            _path = Path(opts.resource_add[1])

            match _type:
                case "GEM5":
                    arch, item = get_resource_simulator(_path)
                case _:
                    arch, item = get_default_resource(
                        _path,
                        _type,
                        arch=opts.resource_arch,
                        version=opts.resource_version,
                        metadata=opts.resource_metadata,
                    )
            artifact_db_add(index_file, arch, item)
        case "del":
            artifact_db_delete(index_file, opts.resource_del[0])
        case _:
            raise SystemExit(f"Resource verb unknown")

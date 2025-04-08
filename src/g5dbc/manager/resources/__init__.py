import re
from pathlib import Path

from ...util import files
from ..artifact_db import artifact_db_add, artifact_db_delete
from ..options import Options
from .simulator import get_resource_simulator


def get_default_resource(
    r_path: Path,
    r_type: str,
    r_arch: str = "",
    r_version: str = "",
    r_meta: str = "",
) -> tuple[str, dict[str, str]]:

    if not r_path.is_file():
        raise SystemExit(f"Artifact path does not exist: {r_path}.")

    if r_type not in ["KERNEL", "DISK", "BOOT"]:
        raise SystemExit(f"Unknown artifact type {r_type}.")

    if r_arch == "":
        raise SystemExit(f"Unknown artifact architecture {r_arch}.")

    r_name = r_path.name
    # Try to get version from name
    if m := re.fullmatch(r"([\w\.]+)-([\w\.-]+)", r_path.name):
        r_name = m[1]
        r_version = m[2]

    entry = dict(
        bintype=r_type,
        name=r_name,
        path=str(r_path.absolute()),
        md5hash=files.hash_md5(r_path),
        version=r_version,
        metadata=r_meta,
    )

    return r_arch, entry


def configure_resources(opts: Options, path: Path | None = None):
    """Configure simulation resources

    Args:
        opts (Options): Command line options
        path (Path | None, optional): Path to artifact resource. Defaults to None.

    Raises:
        SystemExit: If resource could not be configured due to missing information.
    """
    # Create user conf directory if it does not already exist
    opts.user_conf_dir.mkdir(parents=True, exist_ok=True)
    index_file = opts.user_conf_dir.joinpath("artifacts.yaml")

    match opts.command:
        case "add":
            match opts.resource_type:
                case "GEM5":
                    if path is None:
                        raise SystemExit(f"Please specify path of gem5 binary.")
                    arch, item = get_resource_simulator(path)
                case _:
                    if path is None:
                        raise SystemExit(f"Please specify path of artifact.")
                    arch, item = get_default_resource(
                        r_path=path,
                        r_type=opts.resource_type,
                        r_arch=opts.resource_arch,
                        r_version=opts.resource_version,
                        r_meta=opts.resource_metadata,
                    )
            artifact_db_add(index_file, arch, item)
        case "del":
            if path is None:
                raise SystemExit(
                    f"Please specify path of artifact to be removed from database."
                )
            artifact_db_delete(index_file, path)
        case _:
            raise SystemExit(f"Resource verb {opts.command} unknown.")

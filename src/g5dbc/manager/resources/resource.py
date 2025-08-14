from pathlib import Path

from ...util import files, sys_info
from ..options import Options
from . import artifact_db
from .simulator import add_simulator


def resource_item(opts: Options) -> tuple[str, dict[str, str]]:
    return opts.resource_arch, dict(
        bintype=opts.resource_type,
        name=opts.resource_name,
        version=opts.resource_version,
        metadata=opts.resource_meta,
        path=opts.resource_add,
        md5hash=opts.resource_hash,
    )


def resource_add(opts: Options):

    artifact_index = Path(opts.artifact_index[0])
    res = Path(opts.resource_add)

    if not opts.resource_hash:
        opts.resource_hash = files.hash_md5(res)

    if res.is_relative_to(artifact_index.parent):
        opts.resource_add = str(res.relative_to(artifact_index.parent))

    match opts.resource_type:
        case "GEM5":
            if opts.resource_version:
                arch, item = resource_item(opts)
            else:
                arch, item = add_simulator(opts)

        case "EXEC":
            if not opts.resource_arch:
                opts.resource_arch = sys_info.get_local_architecture()
            if not opts.resource_name:
                opts.resource_name = Path(opts.resource_add).name

            arch, item = resource_item(opts)

        case "KERNEL" | "DISK" | "BOOT":
            if not opts.resource_arch:
                raise SystemExit(f"Resource architecture not specified.")
            if not opts.resource_name:
                raise SystemExit(f"Resource name not specified.")
            if not opts.resource_version:
                raise SystemExit(f"Resource version not specified.")

            arch, item = resource_item(opts)

        case "":
            raise SystemExit(f"Resource type not specified.")
        case _:
            raise SystemExit(f"Resource type {opts.resource_type} unknown.")

    artifact_db.add(artifact_index, arch, [item])


def resource_del(opts: Options):
    artifact_index = Path(opts.artifact_index[0])
    path = Path(opts.resource_del)

    if path.is_relative_to(artifact_index.parent):
        path = path.relative_to(artifact_index.parent)

    artifact_db.remove(artifact_index, path)
